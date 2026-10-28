"use client";

import { useEffect, useState } from "react";
import styles from "./health.module.css";

interface ProbeData {
  status: string;
  latency_ms: number;
  probes: Record<string, boolean>;
  errors: Record<string, string>;
}

export default function Home() {
  const [data, setData] = useState<ProbeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const checkHealth = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/health");
      const json = await res.json();
      setData(json);
    } catch (err) {
      setData({
        status: "offline",
        latency_ms: 0,
        probes: { api: false },
        errors: { client: "Failed to connect to health surface proxy" },
      });
    } finally {
      setLoading(false);
      setLastUpdated(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const isReady = data?.status === "ready";

  const components = [
    {
      id: "supabase",
      name: "Supabase & pgvector",
      desc: "Relational storage & vector index extension",
      ok: data?.probes?.supabase ?? false,
    },
    {
      id: "janus",
      name: "SWI-Prolog & Janus",
      desc: "Neuro-symbolic execution bridge (harmless query test)",
      ok: data?.probes?.janus ?? false,
    },
    {
      id: "embedding",
      name: "SEA-LION Embedding Service",
      desc: "E5-600M 1,024-dimensional normalized vector service",
      ok: data?.probes?.embedding ?? false,
    },
    {
      id: "bintu",
      name: "Bintu LLM (llama.cpp)",
      desc: "Gemma 4 E4B quantized GGUF query router",
      ok: data?.probes?.bintu ?? false,
    },
  ];

  return (
    <div className={styles.dashboard}>
    <main className={styles["dashboard-container"]}>
      <header className={styles["dashboard-header"]}>
        <div className={styles["title-area"]}>
          <div className={styles["brand-badge"]}>PalSU Academic Guide</div>
          <h1>Bintanong System Compatibility</h1>
          <p className={styles["subtitle"]}>Phase 0: Docker Foundation & Component Readiness Probe</p>
        </div>
        <div className={styles["global-status-card"]}>
          <div className={`${styles["status-pill"]} ${styles[isReady ? "status-ready" : "status-degraded"]}`}>
            <span className={styles["indicator-dot"]} />
            <span className={styles["status-text"]}>
              {loading && !data ? "Checking..." : isReady ? "All Systems Ready" : "System Degraded"}
            </span>
          </div>
          <div className={styles["latency-info"]}>
            {data ? `${data.latency_ms} ms roundtrip` : "--"}
          </div>
        </div>
      </header>

      <section className={styles["components-grid"]}>
        {components.map((comp) => (
          <div key={comp.id} className={`${styles["component-card"]} ${styles[comp.ok ? "card-ok" : "card-fail"] ?? ""}`}>
            <div className={styles["card-top"]}>
              <span className={styles["component-name"]}>{comp.name}</span>
              <span className={`${styles.badge} ${styles[comp.ok ? "badge-success" : "badge-error"]}`}>
                {comp.ok ? "Operational" : "Degraded"}
              </span>
            </div>
            <p className={styles["component-desc"]}>{comp.desc}</p>
            {data?.errors?.[comp.id] && (
              <div className={styles["error-box"]}>
                <code>{data.errors[comp.id]}</code>
              </div>
            )}
          </div>
        ))}
      </section>

      <footer className={styles["dashboard-footer"]}>
        <div>
          <span>Last checked: {lastUpdated || "never"}</span>
        </div>
        <button type="button" onClick={checkHealth} className={styles["refresh-btn"]}>
          Refresh Probes
        </button>
      </footer>
    </main>
    </div>
  );
}
