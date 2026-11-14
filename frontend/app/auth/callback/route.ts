import { NextResponse } from "next/server";
import { serverAuth } from "@/lib/server-auth";
import { SIGN_IN_ENABLED, isPSUAccount, siteOrigin } from "@/lib/auth-policy";

export async function GET(request: Request) {
  const origin = siteOrigin(request.url, process.env.SITE_ORIGIN), code = new URL(request.url).searchParams.get("code");
  if (!SIGN_IN_ENABLED) return NextResponse.redirect(new URL("/", origin));  // sign-in switched off (owner, 4 Nov 2026)
  const client = await serverAuth();
  if (client && code && code.length <= 2048) {
    const { error } = await client.auth.exchangeCodeForSession(code);
    if (!error) {
      const { data } = await client.auth.getUser();
      if (isPSUAccount(data.user)) return NextResponse.redirect(new URL("/chat", origin));
      await client.auth.signOut({ scope: "local" });
    }
  }
  return NextResponse.redirect(new URL("/login?error=psu_account_required", origin));
}
