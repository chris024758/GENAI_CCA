from __future__ import annotations

import os
import re
from urllib.parse import quote

from langchain_core.tools import tool

from inventory import fetch_inventory

MAX_PROMPT_WORDS = 300


def _cap_words(text: str, limit: int = MAX_PROMPT_WORDS) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]).rstrip(",.;:") + "."


@tool
async def get_inventory_tool() -> dict:
    """Fetch products from MCP inventory, falling back to local demo products."""
    try:
        inventory = await fetch_inventory()
        return inventory.model_dump()
    except Exception as exc:
        # Tools must report recoverable failures instead of crashing the graph.
        return {"products": [], "source": "fallback", "error": str(exc)}


@tool
async def generate_prompt_tool(
    product: dict,
    platform: str,
    style: str,
    audience: str | None,
    cta: str,
) -> dict:
    """Generate a master image-ad prompt with Groq."""
    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")

        llm = ChatGroq(
            api_key=api_key,
            model=os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"),
            temperature=0.7,
            max_tokens=1500,
            reasoning_effort="none",
        )
        target_audience = audience or product.get("audience", "online shoppers")
        messages = [
            SystemMessage(
                content=(
                    "You are the Prompt Agent in an image advertisement pipeline. Your job is to transform "
                    "inventory product data plus the selected platform, creative style, audience, and call to action "
                    "into one detailed master prompt for the downstream Image Ad Agent. Write only the final master "
                    "prompt, with no reasoning, preamble, headings, or markdown. Make it image-generation-ready, "
                    "covering scene composition, product placement, camera angle, lighting, background, color palette, "
                    "text overlay, visual hierarchy, brand tone, platform fit, target audience, and call to action. "
                    "Avoid unsafe claims and do not invent medical or regulated benefits. "
                    "Strict limit: the prompt must be between 250 and 300 words. Do not exceed 300 words."
                )
            ),
            HumanMessage(
                content=(
                    f"Product: {product.get('name')}\n"
                    f"Category: {product.get('category')}\n"
                    f"Description: {product.get('description')}\n"
                    f"Benefits: {', '.join(product.get('key_benefits', []))}\n"
                    f"Price: {product.get('currency')} {product.get('price')}\n"
                    f"Platform: {platform}\n"
                    f"Style: {style}\n"
                    f"Audience: {target_audience}\n"
                    f"CTA: {cta}"
                )
            ),
        ]
        response = await llm.ainvoke(messages)
        # Qwen's thinking models emit reasoning in <think> tags before the answer; strip it.
        cleaned = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
        if "<think>" in cleaned:
            # Response was truncated mid-thought (hit max_tokens); no closing tag to match.
            raise RuntimeError("Model response was truncated inside its reasoning block")
        return {"ad_prompt": _cap_words(cleaned), "provider": "groq"}
    except Exception as exc:
        # The fallback keeps the visual demo usable when keys or quotas are missing.
        benefits = ", ".join(product.get("key_benefits", []))
        fallback_prompt = (
            f"Master image ad prompt for {platform}: Create a {style} advertisement for {product.get('name')} "
            f"in the {product.get('category')} category. Feature the product as the clear hero subject with "
            f"clean composition, confident lighting, a polished background, and platform-ready visual hierarchy. "
            f"Show short overlay text for the key benefits: {benefits}. Include price {product.get('currency')} "
            f"{product.get('price')} and call to action '{cta}'. Design it for "
            f"{audience or product.get('audience', 'online shoppers')} with a {product.get('brand_tone', 'modern')} "
            f"brand tone. Keep the layout readable, aspirational, and suitable for image generation."
        )
        return {"ad_prompt": _cap_words(fallback_prompt), "provider": "fallback", "error": str(exc)}


@tool
async def generate_image_tool(ad_prompt: str) -> dict:
    """Generate an advertisement image from the master prompt using Gemini's image model."""
    try:
        import httpx

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": api_key},
                json={"contents": [{"parts": [{"text": ad_prompt}]}]},
            )
            response.raise_for_status()
            payload = response.json()

        parts = payload["candidates"][0]["content"]["parts"]
        image_part = next(part for part in parts if "inlineData" in part)
        mime_type = image_part["inlineData"].get("mimeType", "image/png")
        base64_data = image_part["inlineData"]["data"]
        image_url = f"data:{mime_type};base64,{base64_data}"
        return {"image_url": image_url, "provider": "gemini"}
    except Exception as exc:
        # Fall back to a free prompt-based image endpoint so the demo stays usable.
        try:
            prompt = quote(ad_prompt[:1800])
            image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
            return {"image_url": image_url, "provider": "pollinations", "error": str(exc)}
        except Exception:
            return {
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1024&q=80",
                "provider": "fallback",
                "error": str(exc),
            }
