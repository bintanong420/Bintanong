import { siteOrigin } from "./auth-policy.ts";

type Options = { accessToken: string | null; baseUrl?: string; siteOrigin?: string; fetch?: typeof fetch };
const failure = (status: number, error: string) => Response.json({ error }, { status, headers: { "Cache-Control": "no-store" } });

export async function forwardStudentRequest(request: Request, path: string, options: Options) {
  const upload = path === "/uploads";
  // Gated on the API by the evaluator passcode; off, or a wrong passcode, is a 404 from the API.
  const evaluationPost = path === "/evaluation/run" || /^\/evaluation\/runs\/run-[a-f0-9]{16}\/judgment$/.test(path);
  const evaluationGet = path === "/evaluation/cases" || path === "/evaluation/runs";
  const methods = path === "/chat" || upload || evaluationPost || /^\/uploads\/upl-[a-f0-9]{16}\/confirm$/.test(path) ? ["POST"]
    : path === "/session" || /^\/uploads\/upl-[a-f0-9]{16}$/.test(path) ? ["DELETE"]
    : path === "/curricula" || evaluationGet || /^\/sources\/ev-[a-f0-9]{64}$/.test(path) ? ["GET"] : null;
  if (!methods) return failure(404, "route_unavailable");
  if (!methods.includes(request.method)) return failure(405, "method_unavailable");
  const url = new URL(request.url), host = request.headers.get("host");
  if (["localhost", "127.0.0.1", "[::1]"].includes(url.hostname) && host && /^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host)) url.host = host;
  // Behind a tunnel request.url stays loopback, so the public origin must come from configuration.
  const origin = request.headers.get("origin"), configured = options.siteOrigin ?? process.env.SITE_ORIGIN;
  const trusted = [url.origin, ...(configured ? [siteOrigin(request.url, configured)] : [])];
  if (request.method !== "GET" && (!origin || !trusted.includes(origin) || request.headers.get("sec-fetch-site") === "cross-site")) return failure(403, "origin_not_allowed");
  const headers = new Headers({ Accept: path === "/chat" ? "text/event-stream" : "application/json" });
  // Browser headers cannot replace the cookie identity used by this workspace.
  if (request.headers.has("authorization")) return failure(401, "sign_in_required");
  if (options.accessToken) headers.set("Authorization", "Bearer " + options.accessToken);
  const passcode = request.headers.get("x-bintanong-evaluator");
  if (passcode && (evaluationPost || evaluationGet)) headers.set("x-bintanong-evaluator", passcode);
  // Only the chat session and the anonymous browser id (per-person question limit) reach the API.
  const owned = request.headers.get("cookie")?.split(";").map(c => c.trim())
    .filter(c => /^__Host-bintanong_(session|client)=[A-Za-z0-9_-]{43}$/.test(c)) ?? [];
  if (owned.length) headers.set("Cookie", owned.join("; "));
  if (origin && request.method !== "GET") headers.set("Origin", origin);
  let body: Uint8Array<ArrayBuffer> | undefined;
  if (request.method === "POST") {
    const reader = request.body?.getReader(), chunks: Uint8Array[] = [];
    let bytes = 0;
    try {
      if (reader) while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        bytes += value.byteLength;
        if (bytes > (upload ? 15 * 1024 * 1024 : 32768)) { await reader.cancel(); return failure(413, "request_too_large"); }
        chunks.push(value);
      }
    } finally { reader?.releaseLock(); }
    body = new Uint8Array(bytes); let offset = 0;
    for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
    headers.set("Content-Type", upload ? "application/octet-stream" : "application/json");
  }
  try {
    const base = new URL(options.baseUrl ?? process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8021");
    if (!["http:", "https:"].includes(base.protocol) || base.username || base.password || base.search || base.hash || base.pathname !== "/") return failure(503, "service_unavailable");
    const target = new URL(path, base);
    if (upload) {
      if ([...url.searchParams.keys()].some(k => !["programId", "curriculumId"].includes(k))) return failure(422, "invalid_scope");
      for (const key of ["programId", "curriculumId"]) {
        const values = url.searchParams.getAll(key);
        if (values.length !== 1 || !values[0] || values[0].length > 128) return failure(422, "incomplete_scope");
        target.searchParams.set(key, values[0]);
      }
    }
    const upstream = await (options.fetch ?? fetch)(target, { method: request.method, headers, body,
      signal: request.signal, redirect: "error", cache: "no-store" });
    const outgoing = new Headers({ "Cache-Control": "no-store", "X-Accel-Buffering": "no" });
    for (const name of ["content-type", "x-vercel-ai-ui-message-stream"]) {
      const value = upstream.headers.get(name); if (value) outgoing.set(name, value);
    }
    for (const cookie of upstream.headers.getSetCookie()) if (/^__Host-bintanong_(session|client)=/.test(cookie)) outgoing.append("Set-Cookie", cookie);
    return new Response(upstream.body, { status: upstream.status, headers: outgoing });
  } catch { return failure(503, "connection_failed"); }
}
