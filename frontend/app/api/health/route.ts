import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const apiUrl = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
  const start = performance.now();

  try {
    const res = await fetch(`${apiUrl}/health/ready`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    const latency = Math.round(performance.now() - start);
    const data = await res.json().catch(() => ({}));

    return NextResponse.json(
      {
        status: data.status || (res.ok ? "ready" : "degraded"),
        latency_ms: latency,
        probes: data.probes || {
          supabase: false,
          janus: false,
          embedding: false,
          bintu: false,
        },
        errors: data.errors || {},
      },
      { status: res.status }
    );
  } catch (error) {
    const latency = Math.round(performance.now() - start);
    return NextResponse.json(
      {
        status: "degraded",
        latency_ms: latency,
        probes: {
          api: false,
          supabase: false,
          janus: false,
          embedding: false,
          bintu: false,
        },
        errors: {
          api: error instanceof Error ? error.message : "API service unreachable",
        },
      },
      { status: 503 }
    );
  }
}
