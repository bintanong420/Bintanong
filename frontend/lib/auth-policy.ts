type User = { email?: string; email_confirmed_at?: string | null; identities?: { provider?: string; identity_data?: Record<string, unknown> }[] };
export function pageRedirect(pathname: string, permitted: boolean) {
  if (pathname === "/login" && permitted) return "/chat";
  return null;
}

export function isPSUAccount(user: User | null | undefined) {
  const email = user?.email?.toLowerCase();
  return !!email && !!user?.email_confirmed_at && email.split("@").length === 2 && email.split("@")[1] === "psu.palawan.edu.ph"
    && !!user.identities?.some(identity => identity.provider === "google" && identity.identity_data?.email_verified === true
      && typeof identity.identity_data.email === "string" && identity.identity_data.email.toLowerCase() === email);
}
export function siteOrigin(requestUrl: string, configured?: string) {
  const request = new URL(requestUrl);
  if (!configured) {
    if (!["localhost", "127.0.0.1", "[::1]"].includes(request.hostname)) throw new Error("site_origin_required");
    return request.origin;
  }
  const url = new URL(configured);
  if (url.username || url.password || url.search || url.hash || url.pathname !== "/" ||
      (url.protocol !== "https:" && !(url.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)))) throw new Error("invalid_site_origin");
  return url.origin;
}
