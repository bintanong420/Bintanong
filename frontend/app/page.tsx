"use client";

import { useState } from "react";
import Link from "next/link";
import { SIGN_IN_ENABLED } from "@/lib/auth-policy";
import { ArrowUpRight, CheckCircle2, BookOpen, GraduationCap, ChevronDown, Menu, X } from "lucide-react";

// Illustrative only: these describe how Bintanong builds an answer, not institutional facts.
const demoPresets = [
  {
    title: "Prerequisite check",
    query: "Can I take CC5 if I failed CC4?",
    badge: "Curriculum rules",
    details: [
      "Reads “CC5” as the printed CC 5/L in your program’s curriculum",
      "Compares its recorded prerequisites with the grades you shared",
      "A missing grade or rule stays unknown, never assumed met",
    ],
    advice: "The answer names the prospectus it used. Confirm enrollment decisions with your academic adviser.",
  },
  {
    title: "University policy",
    query: "What is the policy on subject overload for graduating students?",
    badge: "Handbook & Citizens’ Charter",
    details: [
      "Searches the reviewed Student Handbook and Citizens’ Charter",
      "Answers with the source, section and date it used",
    ],
    advice: "If the reviewed sources don’t cover it, Bintanong says so and points you to the right office.",
  },
  {
    title: "Planning next semester",
    query: "I'm an irregular student. What can I take next semester?",
    badge: "Needs your details",
    details: [
      "Asks for your program and curriculum when it doesn’t have them",
      "Uses the subjects you list or upload as passed",
    ],
    advice: "Course details you share stay in temporary memory for this session.",
  },
];

const faqs = [
  {
    q: "What is Bintanong and who is it built for?",
    a: "Bintanong is a research academic guide for Palawan State University undergraduates. Ask about supported curriculum requirements, prerequisites and documented academic procedures. Graduate and professional programs, laboratory school, and staff-only procedures are outside this study.",
  },
  {
    q: "Can Bintanong enroll me or modify my grades?",
    a: "No. Bintanong is a read-only advisory guide. It does not replace the Registrar, your academic adviser, or the official portal.",
  },
  {
    q: "How are prerequisite checks done?",
    a: "Prerequisite checks use reviewed curriculum records and fixed rules, not guesses. When a grade, curriculum or rule is missing, Bintanong says it is unknown. Coverage depends on the reviewed sources, so verify important decisions with the relevant university office.",
  },
  {
    q: "Can I ask questions naturally?",
    a: "Yes. Ask in English, Filipino, or Taglish, in your own words. No special keywords needed.",
  },
  {
    q: "What happens to my information?",
    a: "No account is needed. Chat messages, uploaded files, and course details stay in temporary memory, separate from institutional knowledge, and are not stored permanently. Start a new chat to clear them when you finish.",
  },
];

const navLinks = [["#features", "Features"], ["#story", "About"], ["#faq", "FAQ"]];

export default function LandingPage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(0);
  const [demo, setDemo] = useState(demoPresets[0]);

  return (
    <div className="relative min-h-screen w-full bg-white text-[#111827] overflow-x-hidden selection:bg-orange-500/15 selection:text-orange-950 font-sans antialiased">
      <a href="#main" className="absolute left-4 -top-20 z-50 rounded-lg bg-white px-3 py-2 text-sm focus:top-2">Skip to content</a>

      <div className="relative w-full min-h-screen flex flex-col justify-between overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none select-none z-0">
          <img src="/landing/orange.jpg" alt="" className="w-full h-full object-cover object-center opacity-90" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_75%_55%_at_50%_45%,rgba(255,255,255,0.78)_0%,rgba(255,255,255,0.3)_60%,transparent_100%)]" />
          <div className="absolute inset-0 bg-gradient-to-b from-white/20 via-transparent to-white/40" />
        </div>

        <header className="relative z-20 w-full px-6 sm:px-12 md:px-16 lg:px-20 h-20 flex items-center justify-between border-b border-black/[0.03]">
          <Link href="/" className="flex items-center gap-2.5 group select-none">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-[#E11D48] p-0.5 shadow-xs flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
              <div className="w-full h-full bg-white rounded-full flex items-center justify-center p-1">
                <img src="/landing/v2-logo23.png" alt="" className="w-full h-full object-contain" />
              </div>
            </div>
            <span className="text-[17px] font-bold tracking-tight text-[#0F172A]">Bintanong</span>
          </Link>

          <nav aria-label="Main navigation" className="hidden md:flex items-center gap-9 text-[13.5px] font-medium text-[#52525B]">
            {navLinks.map(([href, label]) => <a key={href} href={href} className="hover:text-[#09090B] transition-colors">{label}</a>)}
          </nav>

          <div className="hidden md:flex items-center gap-5">
            {SIGN_IN_ENABLED && <Link href="/login" className="text-[13.5px] font-medium text-[#52525B] hover:text-[#09090B] transition-colors">Sign in</Link>}
            <Link href="/chat" className="inline-flex items-center justify-center px-4.5 py-2 rounded-full bg-[#0A0A0A] hover:bg-black text-white text-[13px] font-medium shadow-xs hover:shadow-md transition-all active:scale-95">
              Ask a question
            </Link>
          </div>

          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-neutral-600 hover:text-neutral-900"
            aria-label="Toggle navigation"
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </header>

        {isMobileMenuOpen && (
          <div className="relative z-30 md:hidden border-b border-neutral-100 bg-white/95 backdrop-blur-xl px-6 py-5 space-y-3">
            {navLinks.map(([href, label]) => <a key={href} href={href} onClick={() => setIsMobileMenuOpen(false)} className="block text-sm font-medium text-neutral-700 py-1">{label}</a>)}
            <div className="pt-2 flex flex-col gap-2">
              <Link href="/chat" className="w-full text-center py-2.5 rounded-full bg-neutral-950 text-white text-sm font-medium">Ask a question</Link>
              {SIGN_IN_ENABLED && <Link href="/login" className="w-full text-center py-2.5 rounded-full border border-neutral-200 text-neutral-800 text-sm font-medium">Sign in</Link>}
            </div>
          </div>
        )}

        <main id="main" className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pt-2 sm:pt-4 pb-10 sm:pb-14 max-w-5xl mx-auto w-full">
          <div className="flex items-center justify-center mb-5 sm:mb-6 select-none">
            <img src="/landing/bintanong-full-logo.png" alt="Bintanong" fetchPriority="high" className="h-24 sm:h-32 md:h-36 w-auto object-contain drop-shadow-xs transition-transform duration-300 hover:scale-105" />
          </div>
          <h1 className="text-[38px] sm:text-[56px] md:text-[68px] font-bold tracking-[-0.038em] text-[#0F172A] leading-[1.06] max-w-5xl mx-auto">
            AI Academic Guide <br />
            For <span className="text-[#C2410C]">Every PalSU Undergraduate Student.</span>
          </h1>
          <p className="mt-6 md:mt-7 text-[15px] sm:text-[17px] text-[#52525B] max-w-xl md:max-w-2xl mx-auto leading-[1.6]">
            Check your course prerequisites, understand your prospectus, and ask about PalSU rules. English, Filipino, or Taglish.
          </p>
          <div className="mt-8 md:mt-9 flex items-center justify-center">
            <Link href="/chat" className="inline-flex items-center justify-center px-7 py-3 rounded-full bg-[#0A0A0A] hover:bg-black text-white text-[14px] font-medium shadow-xs hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 active:scale-95 group">
              <span>Ask a question</span>
              <span aria-hidden="true" className="ml-2 text-sm transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5">↗</span>
            </Link>
          </div>
        </main>
      </div>

      <section id="use-case" className="relative z-10 w-full py-16 sm:py-20 px-6 sm:px-12 md:px-16 lg:px-20 max-w-7xl mx-auto">
        <div className="bg-[#FAFAFC] border border-neutral-200/70 rounded-3xl p-8 sm:p-12 shadow-sm relative overflow-hidden">
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-neutral-200/60">
              <div>
                <span className="text-xs font-semibold text-orange-700 uppercase tracking-wider">Preview</span>
                <h2 className="text-2xl font-bold tracking-tight text-neutral-900 mt-1">How Bintanong works through a question</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {demoPresets.map(preset => (
                  <button
                    key={preset.title}
                    type="button"
                    aria-pressed={demo === preset}
                    onClick={() => setDemo(preset)}
                    className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${demo === preset ? "bg-[#0A0A0A] text-white shadow-xs" : "bg-white hover:bg-neutral-100 text-neutral-600 border border-neutral-200/80"}`}
                  >
                    {preset.title}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-4 pt-2" aria-live="polite">
              <div className="flex justify-end">
                <div className="max-w-md bg-[#0F172A] text-white rounded-2xl rounded-tr-xs px-4 py-3 text-sm shadow-xs">{demo.query}</div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-[#E11D48] p-0.5 shrink-0 shadow-xs">
                  <div className="w-full h-full bg-white rounded-full flex items-center justify-center p-0.5">
                    <img src="/landing/v2-logo23.png" alt="" className="w-full h-full object-contain" />
                  </div>
                </div>
                <div className="max-w-xl w-full bg-white border border-neutral-200/80 rounded-2xl rounded-tl-xs p-5 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs font-semibold text-neutral-800">{demo.title}</span>
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-orange-100 text-orange-900">{demo.badge}</span>
                  </div>
                  <ul className="text-xs space-y-1 pl-3 border-l-2 border-neutral-200 text-neutral-600">
                    {demo.details.map(d => <li key={d}>{d}</li>)}
                  </ul>
                  <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200/60 text-xs text-neutral-600">{demo.advice}</div>
                  <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <span className="text-neutral-500">Illustration, not a real answer.</span>
                    <Link href="/chat" className="font-medium text-orange-700 hover:text-orange-800 inline-flex items-center gap-1">
                      <span>Try it in chat</span>
                      <ArrowUpRight className="w-3.5 h-3.5" aria-hidden="true" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="relative z-10 w-full py-20 sm:py-28 px-6 sm:px-12 md:px-16 lg:px-20 overflow-hidden my-4">
        <div className="absolute inset-0 bg-cover bg-[center_bottom_25%] sm:bg-[center_bottom_20%] scale-105 blur-[2px]" style={{ backgroundImage: "url('/landing/psu-campus.jpg')" }} />
        <div className="absolute inset-0 bg-black/35 backdrop-blur-[1px]" />
        <div className="relative z-10 max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-semibold text-orange-300 uppercase tracking-wider">Built for PalSU undergraduates</span>
            <h2 className="text-3xl font-bold tracking-tight text-white mt-1 drop-shadow-sm">Clear guidance for your degree</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              [CheckCircle2, "Prerequisite checks", "See whether your recorded grades meet a subject’s prerequisites before enrollment, with anything unknown called out."],
              [BookOpen, "Handbook & Charter", "Answers drawn from the reviewed PalSU Student Handbook and Citizens’ Charter, with the source cited."],
              [GraduationCap, "Natural conversations", "Ask in plain words, in English, Filipino, or Taglish. No special phrasing needed."],
            ].map(([Icon, title, body]) => {
              const I = Icon as typeof CheckCircle2;
              return (
                <div key={title as string} className="rounded-[28px] bg-white/70 backdrop-blur-md border border-white/40 p-9 sm:p-10 shadow-2xl transition-all duration-300 hover:-translate-y-1 space-y-5">
                  <div className="w-12 h-12 rounded-2xl bg-white/90 text-orange-700 flex items-center justify-center shadow-sm"><I className="w-6 h-6" aria-hidden="true" /></div>
                  <h3 className="text-xl font-bold text-neutral-900 tracking-tight">{title as string}</h3>
                  <p className="text-sm text-neutral-800 leading-relaxed font-medium">{body as string}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section id="story" className="relative z-10 w-full py-16 px-6 sm:px-12 md:px-16 lg:px-20 max-w-7xl mx-auto">
        <div className="rounded-3xl bg-[#FAFAFC] text-neutral-900 border border-neutral-200/80 p-8 sm:p-14 relative overflow-hidden shadow-sm">
          <div className="absolute inset-0 bg-cover sm:bg-contain bg-center bg-no-repeat opacity-[0.25] pointer-events-none" style={{ backgroundImage: "url('/landing/bintanong-mascot-duo.png')" }} />
          <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
            <div className="w-32 h-32 sm:w-40 sm:h-40 rounded-full bg-white border border-neutral-200/90 shadow-sm p-4 flex items-center justify-center shrink-0">
              <img src="/landing/v2-logo23.png" alt="Bintanong mascot" className="w-full h-full object-contain drop-shadow-sm" />
            </div>
            <div className="space-y-3 text-center md:text-left">
              <span className="text-xs font-semibold text-orange-700 uppercase tracking-widest">Palawan bearcat mascot</span>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-neutral-900">Made for Palawan State University students</h2>
              <p className="text-xs sm:text-sm text-neutral-600 leading-relaxed max-w-2xl">
                The binturong is known for its patience, steady footsteps, and calm navigation of dense rainforest canopies. Bintanong carries that steadiness into your questions about college.
              </p>
              <div className="pt-2">
                <Link href="/about" className="text-xs font-semibold text-orange-700 hover:text-orange-800 inline-flex items-center gap-1 underline underline-offset-4">
                  <span>Learn more about Bintanong</span>
                  <ArrowUpRight className="w-3.5 h-3.5" aria-hidden="true" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="faq" className="relative z-10 w-full py-16 px-6 sm:px-12 md:px-16 lg:px-20 max-w-4xl mx-auto">
        <div className="text-center space-y-2 mb-10">
          <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Answers</span>
          <h2 className="text-2xl font-bold tracking-tight text-neutral-900">Frequently asked questions</h2>
        </div>
        <div className="space-y-3">
          {faqs.map((faq, idx) => {
            const isOpen = openFaqIndex === idx;
            return (
              <div key={faq.q} id={idx === faqs.length - 1 ? "privacy" : undefined} className="border border-neutral-200/70 rounded-2xl overflow-hidden bg-white">
                <button
                  type="button"
                  aria-expanded={isOpen}
                  onClick={() => setOpenFaqIndex(isOpen ? null : idx)}
                  className="w-full px-6 py-4 flex items-center justify-between text-left gap-4 hover:bg-neutral-50/60"
                >
                  <span className="text-sm font-semibold text-neutral-900">{faq.q}</span>
                  <ChevronDown aria-hidden="true" className={`w-4 h-4 shrink-0 text-neutral-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
                </button>
                {isOpen && <div className="px-6 pb-5 pt-1 text-xs sm:text-sm text-neutral-600 border-t border-neutral-100 leading-relaxed">{faq.a}</div>}
              </div>
            );
          })}
        </div>
      </section>

      <section className="relative z-10 w-full py-16 px-6 sm:px-12 md:px-16 lg:px-20 max-w-6xl mx-auto">
        <div className="rounded-3xl bg-gradient-to-tr from-[#0F172A] to-[#000000] text-white p-10 sm:p-16 text-center relative overflow-hidden shadow-2xl">
          <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-orange-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -top-24 -right-24 w-80 h-80 bg-amber-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 max-w-xl mx-auto space-y-5">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">Start a conversation with Bintanong</h2>
            <div className="pt-2">
              <Link href="/chat" className="inline-flex items-center justify-center px-7 py-3.5 rounded-full bg-white text-[#0A0A0A] hover:bg-neutral-100 text-sm font-medium shadow-md transition-all active:scale-95">
                <span>Start a chat</span>
                <span aria-hidden="true" className="ml-2 text-sm">↗</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="w-full border-t border-neutral-100 py-8 px-6 sm:px-12 md:px-16 lg:px-20 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-neutral-500">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-neutral-800">Bintanong</span>
          <span aria-hidden="true">•</span>
          <span>PalSU undergraduate research preview</span>
        </div>
        <p className="text-center sm:text-right">Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</p>
      </footer>
    </div>
  );
}
