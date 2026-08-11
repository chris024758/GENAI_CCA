from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

from models import InventoryResponse, Product

DATA_PATH = Path(__file__).parent / "data" / "inventory.json"


def load_fallback_products() -> list[Product]:
    try:
        with DATA_PATH.open("r", encoding="utf-8") as handle:
            return [Product.model_validate(item) for item in json.load(handle)]
    except Exception as exc:
        # This fallback protects the demo even if the JSON file is edited badly.
        return [
            Product(
                id="demo-product",
                name="Demo Product",
                category="Fallback",
                description=f"Local inventory could not be read: {exc}",
                price=999,
                currency="INR",
                image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
                audience="general shoppers",
                key_benefits=["available for demo", "local fallback", "resilient pipeline"],
                brand_tone="minimal",
            )
        ]


async def fetch_inventory() -> InventoryResponse:
    mcp_url = os.getenv("INVENTORY_MCP_URL")
    if not mcp_url:
        return InventoryResponse(
            products=load_fallback_products(),
            source="fallback",
            error="INVENTORY_MCP_URL is not configured; using local fallback inventory.",
        )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(mcp_url)
            response.raise_for_status()
            payload = response.json()
        raw_products = payload.get("products", payload)
        return InventoryResponse(
            products=[Product.model_validate(item) for item in raw_products],
            source="mcp",
        )
    except Exception as exc:
        return InventoryResponse(
            products=load_fallback_products(),
            source="fallback",
            error=f"MCP inventory fetch failed: {exc}",
        )
