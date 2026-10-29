import type { Attachment, ExampleKind, Fact, WorkspaceAction } from "./workspace";

export const demoAnswer = {
  text: "This is a fictional example response, included to preview how a Bintanong conversation will look.\n\nAn academic answer will appear here with its supporting sources once the public service is connected. This preview has not checked a PalSU policy, curriculum or prerequisite.\n\nAny files you select stay on this page as filename chips. Their contents are not opened, uploaded or analyzed.",
  sources: [],
};

export function prepareDemo(signal: AbortSignal): Promise<typeof demoAnswer> {
  // A short, explicitly simulated pause makes the approved status presentation inspectable.
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(new DOMException("Preview reset", "AbortError"));
    const timer = setTimeout(() => { signal.removeEventListener("abort", cancel); resolve(demoAnswer); }, 650);
    function cancel() { clearTimeout(timer); reject(new DOMException("Preview reset", "AbortError")); }
    signal.addEventListener("abort", cancel, { once: true });
  });
}

export const previewExamples: { kind: ExampleKind; label: string }[] = [
  { kind: "clarification", label: "Clarify a course" }, { kind: "source", label: "Answer and source details" },
  { kind: "advisory", label: "Prerequisite information missing" }, { kind: "upload", label: "File selection and review" },
  { kind: "review", label: "Check these details" }, { kind: "files", label: "Files and typed details" },
  { kind: "working", label: "Checking available information" }, { kind: "insufficient", label: "Information unavailable" },
  { kind: "conflict", label: "Sources disagree" }, { kind: "out-of-scope", label: "Outside supported scope" },
  { kind: "connection", label: "Connection interrupted" }, { kind: "unsupported", label: "Unsupported file format" },
  { kind: "unreadable", label: "Unreadable file" }, { kind: "file-failed", label: "File processing failed" },
  { kind: "expired", label: "Files no longer available" }, { kind: "clear-failed", label: "Clear request not confirmed" },
];

export const exampleCopy: Partial<Record<ExampleKind, { title: string; text: string; tone: "info" | "warning" | "danger" }>> = {
  source: { title: "Hindi ko pa ma-confirm ang prerequisite.", text: "Hindi ko pa makita ang policy na kailangan para sagutin ito. Hindi ibig sabihin nito na wala kang prerequisite.", tone: "info" },
  advisory: { title: "Hindi pa ma-confirm kung puwede mong kunin ang course.", text: "Kulang pa ang impormasyon para i-check ang prerequisite mo. Hindi ito ‘failed’ o ‘not eligible’.", tone: "warning" },
  insufficient: { title: "Hindi ko pa makita ang policy para dito.", text: "Kaya hindi ko pa ma-confirm ang prerequisite o eligibility mo. Hindi mo kailangang hanapin muna ang tamang memo para magtanong.", tone: "info" },
  conflict: { title: "Magkaiba ang impormasyong nakita ko.", text: "Hindi pa malinaw kung aling policy ang applicable. Hindi muna ako magbibigay ng eligibility result.", tone: "warning" },
  "out-of-scope": { title: "That’s outside Bintanong’s scope.", text: "I can help with PalSU undergraduate academic questions, but not advertising.", tone: "info" },
  connection: { title: "Hindi natuloy ang sagot", text: "Nagkaproblema sa koneksyon sa halimbawang ito. Nandito pa ang tanong mo.", tone: "danger" },
  unsupported: { title: "Unsupported file format", text: "Choose a PDF, JPG, or PNG. File selection here is a local preview only.", tone: "warning" },
  unreadable: { title: "Hindi ko mabasa ang file.", text: "Halimbawa: subukan ang mas malinaw na larawan o readable PDF. This preview has not opened or read a file.", tone: "warning" },
  "file-failed": { title: "Hindi natuloy ang pagbasa ng file", text: "Halimbawa: subukan ulit. Your question and selection are still here. No details have been confirmed.", tone: "danger" },
  expired: { title: "Files no longer available", text: "Halimbawa: hindi na available ang mga file. Nandito pa ang tanong mo. Add the file again, then review its details. Old details are not reused.", tone: "warning" },
};

export function sampleFacts(fileId: string | null): Fact[] {
  return [
    { id: "sample-course", label: "Target course label", value: "Course A", fileId, decision: "unconfirmed" },
    { id: "sample-note", label: "Course note", value: "Optional sample note", fileId, decision: "unconfirmed" },
  ];
}

export function exampleAction(kind: ExampleKind, id: string): WorkspaceAction {
  const files: Attachment[] = [
    { id: `${id}-pdf`, name: "curriculum_example.pdf", size: 4200, type: "application/pdf", synthetic: true },
    { id: `${id}-png`, name: "course_note.png", size: 2100, type: "image/png", synthetic: true },
  ];
  const withFiles = ["upload", "review", "files", "unreadable", "file-failed", "clear-failed"].includes(kind);
  return { type: "example", kind, id, question: kind === "out-of-scope" ? "Can you write an advert for an unrelated product?" : "Paano ko mache-check ang prerequisite ng course na gusto kong kunin?",
    files: withFiles ? files : [], facts: kind === "review" || kind === "files" ? sampleFacts(kind === "files" ? null : files[1].id) : [] };
}

// Every delay and outcome here is a fixture, never a network or file-processing event.
export function previewDelay(signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(new DOMException("Preview reset", "AbortError"));
    const timer = setTimeout(() => { signal.removeEventListener("abort", cancel); resolve(); }, 650);
    function cancel() { clearTimeout(timer); reject(new DOMException("Preview reset", "AbortError")); }
    signal.addEventListener("abort", cancel, { once: true });
  });
}
