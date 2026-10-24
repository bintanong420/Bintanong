import { authConfiguration } from "@/lib/server-auth";
import { AppearanceControl } from "@/components/workspace/appearance-control";
import { Button } from "@/components/ui/button";
import { LogIn } from "lucide-react";

export const dynamic = "force-dynamic";
export default async function Login({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const config = authConfiguration();
  let available = false;
  if (config) {
    try {
      const result = await fetch(config.url + "/auth/v1/settings", { headers: { apikey: config.key }, cache: "no-store", signal: AbortSignal.timeout(10000) });
      available = result.ok && (await result.json()).external?.google === true;
    } catch {}
  }
  const { error } = await searchParams;
  return <main className="workspace login-page">
    <div className="campus-banner" aria-hidden="true"><img src="/design/campus.png" alt="" /></div>
    <header className="login-heading"><p className="brand">Bintanong</p><AppearanceControl /></header>
    <section className="login-content" aria-labelledby="login-title">
      <p className="supporting-copy">Research preview · University validation is pending.</p>
      <h1 id="login-title">Your academic questions, in one place.</h1>
      <p>Sign in with your PSU Google account to ask about undergraduate curricula and academic policies.</p>
      {error && <p role="alert" className="outcome-notice status-danger">{error === "psu_account_required" ? "Use a verified @psu.palawan.edu.ph Google account." : "Sign-in could not finish. Please try again."}</p>}
      {available ? <form action="/auth/login" method="post"><Button type="submit"><LogIn aria-hidden="true" size={18} />Continue with PSU Google</Button></form>
        : <p role="status" className="outcome-notice status-info">Sign-in isn’t available yet. Please try again later.</p>}
      <p className="supporting-copy">Sign-in stores your account email. Chat messages and course details stay temporary.</p>
      <p className="responsible-use">Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</p>
    </section>
  </main>;
}
