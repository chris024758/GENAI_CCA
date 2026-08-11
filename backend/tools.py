from __future__ import annotations

import os
from urllib.parse import quote

from langchain_core.tools import tool

from inventory import fetch_inventory


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
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        target_audience = audience or product.get("audience", "online shoppers")
        messages = [
            SystemMessage(
                content=(
                    "You are the Prompt Agent in an image advertisement pipeline. Your job is to transform "
                    "inventory product data plus the selected platform, creative style, audience, and call to action "
                    "into one detailed master prompt for the downstream Image Ad Agent. Write only the final master "
                    "prompt. Make it image-generation-ready with scene composition, product placement, camera angle, "
                    "lighting, background, color palette, text overlay, visual hierarchy, brand tone, platform fit, "
                    "target audience, and call to action. Avoid unsafe claims and do not invent medical or regulated benefits."
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
        return {"ad_prompt": response.content, "provider": "groq"}
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
        return {"ad_prompt": fallback_prompt, "provider": "fallback", "error": str(exc)}


@tool
async def generate_image_tool(ad_prompt: str) -> dict:
    """Generate an advertisement image URL using a free image endpoint."""
    try:
        # Pollinations supports URL-based generation, which is ideal for a no-key demo.
        prompt = quote(ad_prompt[:1800])
        image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
        return {"image_url": image_url, "provider": "pollinations"}
    except Exception as exc:
        return {
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1024&q=80",
            "provider": "fallback",
            "error": str(exc),
        }
