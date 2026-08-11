import { useEffect, useState } from "react";
import { fetchInventory } from "../api";
import type { InventoryResult, Product } from "../types";

export function useInventory() {
  const [products, setProducts] = useState<Product[]>([]);
  const [source, setSource] = useState<InventoryResult["source"]>("fallback");
  const [error, setError] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchInventory().then((result) => {
      if (!mounted) return;
      setProducts(result.products);
      setSource(result.source);
      setError(result.error);
      setLoading(false);
    });
    return () => {
      mounted = false;
    };
  }, []);

  return { products, source, error, loading };
}
