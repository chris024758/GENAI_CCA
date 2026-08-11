from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    name: str
    category: str
    description: str
    price: float
    currency: Literal["INR", "USD"]
    image_url: str
    audience: str
    key_benefits: list[str]
    brand_tone: str


class InventoryResponse(BaseModel):
    products: list[Product]
    source: Literal["mcp", "fallback"]
    error: str | None = None


class GenerateAdRequest(BaseModel):
    product_id: str | None = None
    platform: str = Field(default="Instagram")
    style: str = Field(default="premium social media ad")
    audience: str | None = None
    cta: str = Field(default="Shop now")


class AgentEvent(BaseModel):
    agent: Literal["inventory", "prompt", "image", "workflow"]
    status: Literal["idle", "running", "complete", "failed", "fallback"]
    message: str
    input: dict | None = None
    output: dict | None = None
    error: str | None = None


class AdGenerationResult(BaseModel):
    product: Product
    ad_prompt: str
    image_url: str
    inventory_source: Literal["mcp", "fallback"]
    errors: list[str]
