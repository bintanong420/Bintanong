type Options = { accessToken: string | null; baseUrl?: string; fetch?: typeof fetch };
const failure = (status: number, error: string) => Response.json({ error }, { status, headers: { "Cache-Control": "no-store" } });

export async function forwardStudentRequest(request: Request, path: string, options: Options) {
  const upload = path === "/uploads";
  const methods = path === "/chat" || upload || /^\/uploads\/upl-[a-f0-9]{16}\/confirm$/.test(path) ? ["POST"]
    : path === "/session" || /^\/uploads\/upl-[a-f0-9]{16}$/.test(path) ? ["DELETE"]
    : path === "/curricula" || /^\/sources\/ev-[a-f0-9]{64}$/.test(path) ? ["GET"] : null;
  if (!methods) return failure(404, "route_unavailable");
  if (!methods.includes(request.method)) return failure(405, "method_unavailable");
  const url = new URL(request.url), host = request.headers.get("host");
  if (["localhost", "127.0.0.1", "[::1]"].includes(url.hostname) && host && /^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host)) url.host = host;
  if (request.method !== "GET" && (request.headers.get("origin") !== url.origin || request.headers.get("sec-fetch-site") === "cross-site")) return failure(403, "origin_not_allowed");
  const headers = new Headers({ Accept: path === "/chat" ? "text/event-stream" : "application/json" });
  // Browser headers cannot replace the cookie identity used by this workspace.
  if (request.headers.has("authorization")) return failure(401, "sign_in_required");
  if (options.accessToken) headers.set("Authorization", "Bearer " + options.accessToken);
  const credential = request.headers.get("cookie")?.split(";").map(c => c.trim()).find(c => /^__Host-bintanong_session=[A-Za-z0-9_-]{43}$/.test(c));
  if (credential) headers.set("Cookie", credential);
  if (request.method !== "GET") headers.set("Origin", url.origin);
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
    for (const cookie of upstream.headers.getSetCookie()) if (cookie.startsWith("__Host-bintanong_session=")) outgoing.append("Set-Cookie", cookie);
    return new Response(upstream.body, { status: upstream.status, headers: outgoing });
  } catch { return failure(503, "connection_failed"); }
}
