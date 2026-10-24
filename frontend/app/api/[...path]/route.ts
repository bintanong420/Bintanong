import { studentAccessToken } from "@/lib/server-auth";
import { forwardStudentRequest } from "@/lib/student-proxy";

export const dynamic = "force-dynamic";
async function forward(request: Request, context: { params: Promise<{ path: string[] }> }) {
  try {
    const { path } = await context.params;
    return await forwardStudentRequest(request, "/" + path.join("/"), { accessToken: await studentAccessToken() });
  } catch { return Response.json({ error: "auth_unavailable" }, { status: 503, headers: { "Cache-Control": "no-store" } }); }
}
export const GET = forward;
export const POST = forward;
export const DELETE = forward;
