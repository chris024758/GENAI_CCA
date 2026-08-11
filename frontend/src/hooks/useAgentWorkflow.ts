import { useMemo, useRef, useState } from "react";
import { API_BASE } from "../api";
import type { AgentEvent, AgentRun, Product, WorkflowResult } from "../types";

const initialAgents: AgentRun[] = [
  { id: "inventory", name: "Inventory Agent", status: "idle", logs: ["Waiting for pipeline run."] },
  { id: "prompt", name: "Prompt Agent", status: "idle", logs: ["Waiting for product context."] },
  { id: "image", name: "Image Ad Agent", status: "idle", logs: ["Waiting for ad prompt."] }
];

export function useAgentWorkflow() {
  const [agents, setAgents] = useState<AgentRun[]>(initialAgents);
  const [result, setResult] = useState<WorkflowResult>({});
  const [running, setRunning] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const resetAgents = () => {
    setAgents(initialAgents.map((agent) => ({ ...agent, logs: agent.logs.slice() })));
    setResult({});
  };

  const applyEvent = (event: AgentEvent) => {
    if (event.agent === "workflow") {
      setRunning(false);
      setResult((event.output ?? {}) as WorkflowResult);
      eventSourceRef.current?.close();
      return;
    }

    setAgents((current) =>
      current.map((agent) => {
        if (agent.id !== event.agent) return agent;
        const now = Date.now();
        const wasIdle = agent.status === "idle";
        return {
          ...agent,
          status: event.status,
          logs: [...(wasIdle ? [] : agent.logs), event.message],
          input: event.input ?? agent.input,
          output: event.output ?? agent.output,
          error: event.error ?? agent.error,
          startedAt: agent.startedAt ?? now,
          completedAt: ["complete", "failed", "fallback"].includes(event.status) ? now : agent.completedAt
        };
      })
    );

    if (event.output && event.agent === "inventory") {
      const output = event.output as { product?: Product; source?: "mcp" | "fallback" };
      setResult((current) => ({ ...current, product: output.product, inventory_source: output.source }));
    }
    if (event.output && event.agent === "prompt") {
      const output = event.output as { ad_prompt?: string; master_prompt?: string };
      setResult((current) => ({ ...current, ad_prompt: output.master_prompt ?? output.ad_prompt }));
    }
    if (event.output && event.agent === "image") {
      const output = event.output as { image_url?: string };
      setResult((current) => ({ ...current, image_url: output.image_url }));
    }
  };

  const run = (params: {
    productId?: string;
    platform: string;
    style: string;
    audience?: string;
    cta: string;
  }) => {
    eventSourceRef.current?.close();
    resetAgents();
    setRunning(true);

    const query = new URLSearchParams({
      platform: params.platform,
      style: params.style,
      cta: params.cta
    });
    if (params.productId) query.set("product_id", params.productId);
    if (params.audience) query.set("audience", params.audience);

    const source = new EventSource(`${API_BASE}/api/generate-ad/stream?${query.toString()}`);
    eventSourceRef.current = source;

    source.onmessage = (message) => {
      applyEvent(JSON.parse(message.data) as AgentEvent);
    };
    source.onerror = () => {
      source.close();
      setRunning(false);
      setAgents((current) =>
        current.map((agent) =>
          agent.status === "running"
            ? { ...agent, status: "failed", logs: [...agent.logs, "Stream connection failed."] }
            : agent
        )
      );
    };
  };

  const activeAgent = useMemo(() => agents.find((agent) => agent.status === "running")?.id, [agents]);

  return { agents, result, running, activeAgent, run };
}
