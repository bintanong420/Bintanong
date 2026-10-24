import { authConfiguration } from "@/lib/server-auth";
import { AppearanceControl } from "@/components/workspace/appearance-control";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export const dynamic = "force-dynamic";
export default async function Login({ searchParams }: { searchParams: Promise<{ error?: string; notice?: string }> }) {
  const config = authConfiguration();
  let available = false;
  if (config) {
    try {
      const result = await fetch(config.url + "/auth/v1/settings", { headers: { apikey: config.key }, cache: "no-store", signal: AbortSignal.timeout(10000) });
      available = result.ok && (await result.json()).external?.google === true;
    } catch {}
  }
  const { error, notice } = await searchParams;
  return <main className="workspace public-page auth-page">
    <aside className="auth-art" aria-label="Palawan State University">
      <img src="/design/campus.png" alt="Entrance to Palawan State University" />
      <div className="auth-art-caption"><a href="/">Bintanong</a><p>For the questions that come with university life.</p></div>
    </aside>
    <div className="auth-panel">
      <header className="auth-navigation"><a href="/"><ArrowLeft size={16} aria-hidden="true" />Back to home</a><AppearanceControl /></header>
      <section className="auth-content" aria-labelledby="login-title">
        <p className="public-eyebrow">PalSU undergraduate research preview</p>
        <h1 id="login-title">Sign in to Bintanong</h1>
        <p>Use your PSU Google account to ask about subjects, prerequisites, enrollment and university policies.</p>
        {notice === "signed_out" && <p role="status">You're signed out of Bintanong on this browser.</p>}
        {notice === "cleanup_pending" && <p role="status">You're signed out of Bintanong on this browser. We couldn't confirm that all temporary data was cleared.</p>}
        {error && <p role="alert" className="outcome-notice status-danger">{error === "psu_account_required" ? "Use a verified @psu.palawan.edu.ph Google account." : "Sign-in could not finish. Please try again."}</p>}
        <form action="/auth/login" method="post"><Button type="submit" disabled={!available} className="google-sign-in">
          <span className="google-letter" aria-hidden="true">G</span>Continue with PSU Google
        </Button></form>
        {!available && <p role="status" className="auth-status">PSU Google sign-in is unavailable right now. <a href="/login">Try again</a>.</p>}
        <p className="auth-account-note">Only verified @psu.palawan.edu.ph Google accounts can continue.</p>
        <div className="auth-privacy"><p>Sign-in stores your account email. Chat messages and course details stay temporary.</p>
          <a href="/#privacy">How your information is handled</a></div>
      </section>
      <footer className="auth-footer">Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</footer>
    </div>
  </main>;
}
