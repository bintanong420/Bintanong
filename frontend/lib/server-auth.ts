import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export function authConfiguration() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL, key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  return url && key ? { url, key } : null;
}
export function authCookieName(url: string) {
  return `sb-${new URL(url).hostname.split(".")[0]}-auth-token`;
}
export async function serverAuth(signal?: AbortSignal) {
  const config = authConfiguration();
  if (!config) return null;
  const jar = await cookies();
  return createServerClient(config.url, config.key, {
    cookieOptions: { name: authCookieName(config.url) },
    ...(signal ? { global: { fetch: (input, init) => fetch(input, { ...init, signal: AbortSignal.any([signal, ...(init?.signal ? [init.signal] : [])]) }) } } : {}),
    cookies: {
    getAll: () => jar.getAll(),
    setAll: values => { if (!signal?.aborted) values.forEach(({ name, value, options }) => jar.set(name, value, options)); },
  } });
}
export async function studentAccessToken() {
  const client = await serverAuth();
  if (!client) return null;
  // This token is only a credential to forward; FastAPI verifies identity and membership on every request.
  const { data, error } = await client.auth.getSession();
  if (error) return null;
  return data.session?.access_token ?? null;
}
