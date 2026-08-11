export type Product = {
  id: string;
  name: string;
  category: string;
  description: string;
  price: number;
  currency: "INR" | "USD";
  image_url: string;
  audience: string;
  key_benefits: string[];
  brand_tone: string;
};

export type AgentId = "inventory" | "prompt" | "image" | "workflow";
export type AgentStatus = "idle" | "running" | "complete" | "failed" | "fallback";

export type AgentRun = {
  id: AgentId;
  name: string;
  status: AgentStatus;
  logs: string[];
  input?: unknown;
  output?: unknown;
  error?: string;
  startedAt?: number;
  completedAt?: number;
};

export type AgentEvent = {
  agent: AgentId;
  status: AgentStatus;
  message: string;
  input?: unknown;
  output?: unknown;
  error?: string;
};

export type InventoryResult = {
  products: Product[];
  source: "mcp" | "fallback";
  error?: string;
};

export type WorkflowResult = {
  product?: Product;
  ad_prompt?: string;
  image_url?: string;
  inventory_source?: "mcp" | "fallback";
  errors?: string[];
};
