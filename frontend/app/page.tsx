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
    <section className="landing-hero" id="introduction" aria-labelledby="landing-title">
      <div className="landing-introduction">
      <p className="public-eyebrow">For PalSU undergraduates</p>
      <h1 id="landing-title">Ask away,<br />Bintanong.</h1>
      <p className="landing-description">A place to start with your courses, university policies, and what to do next.</p>
      <p className="landing-languages">English, Filipino, or Taglish. Ask in your own words.</p>
      <div className="public-actions">
        <Button asChild><a href="/chat">Ask a question</a></Button>
        <a href="#questions">What can I ask?</a>
      </div>
      <p className="public-caption">Continue as a guest or sign in with your PSU Google account.<br />Research preview. University validation is pending.</p>
      </div>
      <figure className="landing-photo"><img src="/design/campus.png" alt="Entrance to Palawan State University" fetchPriority="high" />
        <figcaption>Palawan State University<span>Undergraduate academic affairs</span></figcaption>
      </figure>
    </section>
    <section className="landing-questions" id="questions" aria-labelledby="questions-title">
      <div><p className="public-eyebrow">From the question to the next step</p>
        <h2 id="questions-title">Start with your question.</h2>
        <p>You do not need to know which document to open first. Answers depend on the reviewed information available.</p>
      </div>
      <dl className="question-examples">
        <div><dt>Courses</dt><dd>What are the prerequisites of my course?</dd></div>
        <div><dt>Procedures</dt><dd>How does enrollment work?</dd></div>
        <div><dt>Next steps</dt><dd>What should I do next?</dd></div>
      </dl>
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
          <p>Guest access needs no account. Optional PSU Google sign-in stores your account email. Chat messages, uploaded files, and course details stay in temporary memory,
            separate from institutional knowledge. Clear your session when you finish.</p></div>
      </div>
    </section>
    <footer className="public-footer"><span>Bintanong · PalSU undergraduate research</span>
      <p>Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</p>
    </footer>
  </main>;
}
