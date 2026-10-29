import { NextResponse } from "next/server";
import { serverAuth } from "@/lib/server-auth";
import { siteOrigin } from "@/lib/auth-policy";

export async function POST(request: Request) {
  const origin = siteOrigin(request.url, process.env.SITE_ORIGIN);
  if (request.headers.get("origin") !== origin || request.headers.get("sec-fetch-site") === "cross-site") return new Response(null, { status: 403 });
  const client = await serverAuth();
  if (!client) return NextResponse.redirect(new URL("/login?error=unavailable", origin), 303);
  const { data, error } = await client.auth.signInWithOAuth({ provider: "google", options: {
    redirectTo: origin + "/auth/callback", skipBrowserRedirect: true, queryParams: { hd: "psu.palawan.edu.ph" },
  } });
  return NextResponse.redirect(error || !data.url ? new URL("/login?error=unavailable", origin) : data.url, 303);
}
