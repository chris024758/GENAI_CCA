import { fallbackProducts } from "./data/fallbackProducts";
import type { InventoryResult } from "./types";

export const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function fetchInventory(): Promise<InventoryResult> {
  try {
    const response = await fetch(`${API_BASE}/api/inventory`);
    if (!response.ok) {
      throw new Error(`Inventory API returned ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    // The UI should keep demonstrating the agent pipeline even if the backend is down.
    return {
      products: fallbackProducts,
      source: "fallback",
      error: error instanceof Error ? error.message : "Unknown inventory failure"
    };
  }
}
