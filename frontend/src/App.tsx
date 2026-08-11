import { Activity, BadgeIndianRupee, Box, CheckCircle2, Image, Loader2, Sparkles, Wand2 } from "lucide-react";
import { useMemo, useState } from "react";
import { useAgentWorkflow } from "./hooks/useAgentWorkflow";
import { useInventory } from "./hooks/useInventory";
import type { AgentRun, Product } from "./types";

const platforms = ["Instagram", "Facebook", "Website Banner", "Amazon Listing"];
const styles = ["premium social media ad", "minimal product ad", "bold festival offer", "eco lifestyle ad", "tech launch ad"];

function currency(product: Product) {
  return product.currency === "INR" ? `₹${product.price}` : `$${product.price}`;
}

function StatusBadge({ status }: { status: AgentRun["status"] }) {
  return <span className={`status status-${status}`}>{status}</span>;
}

function AgentCard({ agent }: { agent: AgentRun }) {
  const icon =
    agent.id === "inventory" ? <Box size={18} /> : agent.id === "prompt" ? <Wand2 size={18} /> : <Image size={18} />;
  return (
    <section className={`agent-card ${agent.status === "running" ? "agent-card-active" : ""}`}>
      <div className="agent-heading">
        <div className="agent-title">
          <span className="agent-icon">{icon}</span>
          <h2>{agent.name}</h2>
        </div>
        <StatusBadge status={agent.status} />
      </div>
      <div className="agent-log">
        {agent.logs.map((log, index) => (
          <div className="log-row" key={`${agent.id}-${index}`}>
            <span className="log-dot" />
            <span>{log}</span>
          </div>
        ))}
      </div>
      {agent.output ? (
        <pre className="agent-output">{JSON.stringify(agent.output, null, 2)}</pre>
      ) : (
        <div className="empty-output">No output yet</div>
      )}
    </section>
  );
}

function ProductCard({
  product,
  selected,
  onSelect
}: {
  product: Product;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button className={`product-card ${selected ? "product-card-selected" : ""}`} onClick={onSelect}>
      <img src={product.image_url} alt={product.name} />
      <div>
        <div className="product-topline">
          <strong>{product.name}</strong>
          <span>{currency(product)}</span>
        </div>
        <p>{product.description}</p>
        <div className="benefits">
          {product.key_benefits.slice(0, 2).map((benefit) => (
            <span key={benefit}>{benefit}</span>
          ))}
        </div>
      </div>
    </button>
  );
}

export function App() {
  const { products, source, error, loading } = useInventory();
  const { agents, result, running, run } = useAgentWorkflow();
  const [selectedProductId, setSelectedProductId] = useState<string | undefined>();
  const [platform, setPlatform] = useState(platforms[0]);
  const [style, setStyle] = useState(styles[0]);
  const [cta, setCta] = useState("Shop now");

  const selectedProduct = useMemo(
    () => products.find((product) => product.id === selectedProductId) ?? products[0],
    [products, selectedProductId]
  );

  const startPipeline = () => {
    run({
      productId: selectedProduct?.id,
      platform,
      style,
      audience: selectedProduct?.audience,
      cta
    });
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">
            <Activity size={15} />
            Agentic image advertisement pipeline
          </div>
          <h1>Inventory to generated ad, with every agent visible.</h1>
        </div>
        <button className="primary-action" disabled={running || !selectedProduct} onClick={startPipeline}>
          {running ? <Loader2 className="spin" size={18} /> : <Sparkles size={18} />}
          {running ? "Agents working" : "Run Pipeline"}
        </button>
      </header>

      <section className="control-strip">
        <label>
          Platform
          <select value={platform} onChange={(event) => setPlatform(event.target.value)}>
            {platforms.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label>
          Creative Style
          <select value={style} onChange={(event) => setStyle(event.target.value)}>
            {styles.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label>
          CTA
          <input value={cta} onChange={(event) => setCta(event.target.value)} />
        </label>
      </section>

      <div className="workspace">
        <aside className="inventory-panel">
          <div className="panel-heading">
            <h2>Inventory Source</h2>
            <span className={`source-pill source-${source}`}>{source}</span>
          </div>
          {error ? <div className="notice">{error}</div> : null}
          {loading ? <div className="loading">Loading products...</div> : null}
          <div className="product-list">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                selected={product.id === selectedProduct?.id}
                onSelect={() => setSelectedProductId(product.id)}
              />
            ))}
          </div>
        </aside>

        <section className="agent-board">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </section>

        <aside className="preview-panel">
          <div className="panel-heading">
            <h2>Generated Advertisement</h2>
            {result.image_url ? <CheckCircle2 size={18} /> : <Image size={18} />}
          </div>

          <div className="ad-canvas">
            {result.image_url ? (
              <img src={result.image_url} alt="Generated advertisement" />
            ) : (
              <div className="ad-placeholder">
                <Sparkles size={28} />
                <span>Run the pipeline to generate an image ad.</span>
              </div>
            )}
          </div>

          <div className="prompt-box">
            <div className="prompt-title">
              <Wand2 size={16} />
              Prompt Agent Master Prompt
            </div>
            <p>{result.ad_prompt ?? "The Prompt Agent will generate a detailed master prompt from product, platform, style, and CTA."}</p>
          </div>

          {result.product ? (
            <div className="selected-summary">
              <img src={result.product.image_url} alt={result.product.name} />
              <div>
                <strong>{result.product.name}</strong>
                <span>
                  <BadgeIndianRupee size={14} />
                  {currency(result.product)}
                </span>
              </div>
            </div>
          ) : null}
        </aside>
      </div>
    </main>
  );
}
