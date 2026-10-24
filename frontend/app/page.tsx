import { AppearanceControl } from "@/components/workspace/appearance-control";
import { Button } from "@/components/ui/button";

export default function Home() {
  return <main className="workspace public-page landing-page">
    <a className="public-skip" href="#introduction">Skip to content</a>
    <header className="public-header">
      <a className="public-brand" href="/" aria-label="Bintanong home">Bintanong<span>PalSU academic guide</span></a>
      <nav aria-label="Main navigation">
        <a href="#scope">About the research</a>
        <AppearanceControl />
        <Button asChild variant="outline"><a href="/login">Sign in</a></Button>
      </nav>
    </header>
    <div className="landing-photo"><img src="/design/campus.png" alt="Entrance to Palawan State University" /></div>
    <section className="landing-introduction" id="introduction" aria-labelledby="landing-title">
      <p className="public-eyebrow">Research preview</p>
      <h1 id="landing-title">Ask away, Bintanong.</h1>
      <p className="landing-description">Your questions about university and curriculum policies, in one place.
        Bintanong is a PalSU undergraduate academic guide that combines reviewed sources with structured curriculum checks.</p>
      <div className="public-actions">
        <Button asChild><a href="/chat">Ask a question</a></Button>
        <a href="#scope">What can I ask?</a>
      </div>
      <p className="public-caption">A thesis research build. University validation is pending.</p>
    </section>
    <section className="landing-scope" id="scope" aria-labelledby="scope-title">
      <div><p className="public-eyebrow">Before you ask</p><h2 id="scope-title">An academic guide, with clear limits.</h2></div>
      <div className="scope-details">
        <p>Bintanong covers PalSU undergraduate academic affairs for the 2026–2027 study.
          Ask about supported curriculum requirements and documented academic procedures.
          Its Citizens’ Charter source is the university-wide 2025 4th Edition.</p>
        <p>Coverage depends on the reviewed sources. Missing information stays unknown.
          Graduate and professional programs, laboratory school, and staff-only procedures are outside this study.</p>
        <div id="privacy"><h3>Your information stays separate</h3>
          <p>PSU Google sign-in stores your account email. Chat messages, uploaded files, and course details stay in temporary memory,
            separate from institutional knowledge. Clear your session when you finish.</p></div>
      </div>
    </section>
    <footer className="public-footer"><span>Bintanong · PalSU undergraduate research</span>
      <p>Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</p>
    </footer>
  </main>;
}
