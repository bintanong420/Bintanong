import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { isPSUAccount, pageRedirect } from "./lib/auth-policy";
import { authConfiguration } from "./lib/server-auth";

export async function proxy(request: NextRequest) {
  if (request.nextUrl.pathname === "/chat" || request.nextUrl.pathname.startsWith("/api/")) {
    const response = NextResponse.next();
    response.headers.set("Cache-Control", "no-store");
    return response;
  }
  let response = NextResponse.next({ request });
  const config = authConfiguration();
  let permitted = false;
  if (config) {
    const client = createServerClient(config.url, config.key, { cookies: {
      getAll: () => request.cookies.getAll(),
      setAll(values) {
        values.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        values.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
      },
    } });
    const { data } = await client.auth.getUser();
    permitted = isPSUAccount(data.user);
  }
  const destination = pageRedirect(request.nextUrl.pathname, permitted);
  if (destination) {
    const next = NextResponse.redirect(new URL(destination, request.url));
    response.cookies.getAll().forEach(cookie => next.cookies.set(cookie));
    next.headers.set("Cache-Control", "no-store");
    return next;
  }
  response.headers.set("Cache-Control", "no-store");
  return response;
}
export const config = { matcher: ["/chat", "/login", "/api/:path*"] };
