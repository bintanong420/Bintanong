import { ArrowLeft, BookOpen, CircleCheck, Landmark, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppearanceControl } from "@/components/workspace/appearance-control";
import { BrandMark } from "@/components/workspace/brand-mark";

const capabilities = [
  { icon: CircleCheck, title: "Prerequisite checks", text: "Ask what a course requires. Share your curriculum and the courses you have passed, and Bintanong checks them against the reviewed prerequisite rules where they are available." },
  { icon: BookOpen, title: "Curriculum information", text: "Look up the courses, units and term placement printed in the reviewed prospectus for your curriculum." },
  { icon: Landmark, title: "Policies and procedures", text: "Find what the reviewed handbook and Citizens’ Charter sources say about enrollment and other academic procedures, with the source for each answer." },
];

export default function About() {
  return <main className="workspace public-page about-page">
    <a className="public-skip" href="#about-title">Skip to content</a>
    <header className="about-header">
      <a href="/chat"><ArrowLeft size={16} aria-hidden="true" />Back to chat</a>
      <AppearanceControl />
    </header>
    <div className="about-content">
      <section className="about-hero">
        <BrandMark size={112} />
        <h1 id="about-title">Hi, I&apos;m Bintanong</h1>
        <p>Your academic guide for Palawan State University undergraduates. Ask in English, Filipino, or Taglish.</p>
      </section>
      <ul className="about-capabilities">
        {capabilities.map(({ icon: Icon, title, text }) => <li key={title}>
          <span className="about-icon"><Icon size={20} aria-hidden="true" /></span>
          <h2>{title}</h2><p>{text}</p>
        </li>)}
      </ul>
      <section className="about-note" aria-labelledby="about-why">
        <h2 id="about-why">Why Bintanong?</h2>
        <p>Named after the Palawan binturong (bearcat), Bintanong was created to guide PalSU college students through curricula, prerequisites and academic procedures with clarity.</p>
        <p className="about-limits"><ShieldCheck size={16} aria-hidden="true" /><span><strong>Research preview.</strong> University validation is pending. Bintanong only gives advice: it cannot enroll you, change grades or issue a COR, and information it does not have stays unknown. Confirm important academic decisions with the relevant university office or academic adviser. <a href="/#scope">Scope and privacy</a></span></p>
      </section>
      <div className="about-action"><Button asChild><a href="/chat">Start chatting with Bintanong</a></Button></div>
    </div>
  </main>;
}
