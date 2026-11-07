import type { AnswerPresentation, StudentSourceSummary } from "@/lib/student-contracts";
import { MarkdownText } from "./markdown-text";

const labels = {
  en: { answered: "Answered", unknown: "Not established", clarification_needed: "More details needed",
    not_checked: "Not checked", withheld: "Answer withheld", unavailable: "Information unavailable" },
  taglish: { answered: "Nasagot", unknown: "Hindi pa established", clarification_needed: "Kailangan pa ng details",
    not_checked: "Hindi na-check", withheld: "Hindi muna masasagot", unavailable: "Wala pang reviewed information" },
};

export function AnswerPresentation({ presentation, sources, language, onSource }: {
  presentation: AnswerPresentation; sources: StudentSourceSummary[]; language: string;
  onSource: (sources: StudentSourceSummary[]) => void;
}) {
  const english = language === "en" || language === "unknown";
  const words = labels[english ? "en" : "taglish"];
  return <div className="answer-presentation">
    {presentation.coverageState === "partial" && <p className="supporting-copy">
      {english ? "Some parts could not be answered. See each result below." : "May mga bahaging hindi pa masagot. Tingnan ang bawat result sa ibaba."}
    </p>}
    {presentation.parts.map(part => {
      const cited = sources.filter(source => part.sourceIds.includes(source.sourceId));
      return <section key={part.partId} className="answer-part" aria-label={`${part.label}: ${words[part.state]}`}>
        <header className="answer-part-header"><h3>{part.label}</h3><span className="answer-part-state">{words[part.state]}</span></header>
        {part.blocks.map((block, index) => block.type === "details" ? <details key={index} className="answer-details">
          <summary>{block.title}</summary>
          <MarkdownText text={block.text} />
        </details> : <div key={index} className={`answer-block answer-block-${block.type}`}>
          <MarkdownText text={block.text} />
        </div>)}
        {part.conditional && <p className="supporting-copy">{english ? "This check depends on the course details you supplied." : "Base ang check na ito sa course details na ibinigay mo."}</p>}
        {!!cited.length && <button type="button" className="answer-part-sources" onClick={() => onSource(cited)}>
          {english ? "Sources" : "Mga source"} ({cited.length})<span className="sr-only"> {part.label}</span>
        </button>}
      </section>;
    })}
  </div>;
}
