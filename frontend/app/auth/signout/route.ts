import { clearAuthCookiesAtScopes } from "@supabase/ssr";
import { authConfiguration, authCookieName, serverAuth } from "@/lib/server-auth";
import { siteOrigin } from "@/lib/auth-policy";
import { forwardStudentRequest } from "@/lib/student-proxy";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const origin = siteOrigin(request.url, process.env.SITE_ORIGIN);
  if (request.headers.get("origin") !== origin || request.headers.get("sec-fetch-site") === "cross-site") return new Response(null, { status: 403 });
  const config = authConfiguration();
  if (!config) return Response.json({ error: "signout_unavailable" }, { status: 503, headers: { "Cache-Control": "no-store" } });
  const deadline = AbortSignal.timeout(5000), client = await serverAuth(deadline);
  let cleanupPending = false;
  try {
    await Promise.race([
      (async () => {
        if (!client) throw new Error("signout_unavailable");
        const { data, error } = await client.auth.getSession(), token = data.session?.access_token;
        cleanupPending = !!error || (!token && /(?:^|;\s*)__Host-bintanong_session=/.test(request.headers.get("cookie") ?? ""));
        if (token) {
          const clearing = new Request(origin + "/api/session", { method: "DELETE", headers: request.headers, signal: AbortSignal.any([deadline, AbortSignal.timeout(3000)]) });
          const response = await forwardStudentRequest(clearing, "/session", { accessToken: token });
          cleanupPending ||= response.status !== 204;
        }
        if (!deadline.aborted && !error) {
          const signedOut = await client.auth.signOut({ scope: "local" });
          cleanupPending ||= !!signedOut.error;
        }
      })(),
      new Promise((_, reject) => deadline.addEventListener("abort", () => reject(deadline.reason), { once: true })),
    ]);
  } catch { cleanupPending = true; }
  const jar = await cookies();
  // An expired token can make the SDK return before removing its cookie storage.
  await clearAuthCookiesAtScopes({ storageKey: authCookieName(config.url), scopes: [{ path: "/" }],
    getAll: () => jar.getAll(), setAll: values => values.forEach(({ name, value, options }) => jar.set(name, value, options)),
  });
  jar.set("__Host-bintanong_session", "", { path: "/", httpOnly: true, secure: true, sameSite: "strict", maxAge: 0 });
  return new Response(null, { status: 204, headers: { "Cache-Control": "no-store", ...(cleanupPending ? { "X-Bintanong-Signout-Notice": "cleanup_pending" } : {}) } });
}
