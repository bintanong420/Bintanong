import { serverAuth, studentAccessToken } from "@/lib/server-auth";
import { siteOrigin } from "@/lib/auth-policy";
import { forwardStudentRequest } from "@/lib/student-proxy";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const origin = siteOrigin(request.url, process.env.SITE_ORIGIN);
  if (request.headers.get("origin") !== origin || request.headers.get("sec-fetch-site") === "cross-site") return new Response(null, { status: 403 });
  const client = await serverAuth(), token = await studentAccessToken();
  if (!client || !token) return Response.json({ error: "sign_in_required" }, { status: 401 });
  const clearing = new Request(origin + "/api/session", { method: "DELETE", headers: request.headers, signal: request.signal });
  const response = await forwardStudentRequest(clearing, "/session", { accessToken: token });
  if (response.status !== 204) return response;
  const { error } = await client.auth.signOut({ scope: "local" });
  if (error) return Response.json({ error: "signout_unavailable" }, { status: 503 });
  const jar = await cookies();
  jar.set("__Host-bintanong_session", "", { path: "/", httpOnly: true, secure: true, sameSite: "strict", maxAge: 0 });
  return new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
}
