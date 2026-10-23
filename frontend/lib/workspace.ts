export type Attachment = { id: string; name: string; size: number; type: string; synthetic?: boolean };
export type ExampleKind = "clarification" | "source" | "advisory" | "upload" | "review" | "files" | "working" | "insufficient" | "conflict" | "out-of-scope" | "connection" | "unsupported" | "unreadable" | "file-failed" | "expired" | "clear-failed";
export type Fact = { id: string; label: string; value: string; fileId: string | null; decision: "unconfirmed" | "confirmed" | "removed"; draft?: string };
export type FileStage = "selected" | "checking" | "reading" | "review";
export type Message = { id: string; role: "user" | "assistant"; text: string; attachments: Attachment[]; sources: string[]; example?: ExampleKind };
export type PreviewState = {
  kind: ExampleKind | null; files: Attachment[]; facts: Fact[]; stage: FileStage; fileRequest: string | null;
  clarification: "pending" | "dismissed" | "submitted"; value: string; unknown: boolean;
  clear: "idle" | "pending" | "failed"; clearRequest: string | null; resolved: boolean;
};
export type WorkspaceState = { draft: string; attachments: Attachment[]; messages: Message[]; pending: string | null; warning: string | null; preview: PreviewState };
export type WorkspaceAction =
  | { type: "draft"; text: string }
  | { type: "select"; attachments: Attachment[]; warning: string | null }
  | { type: "remove"; id: string }
  | { type: "submit"; id: string }
  | { type: "complete"; id: string; text: string; sources: string[] }
  | { type: "new-chat" }
  | { type: "example"; kind: ExampleKind; id: string; question?: string; files: Attachment[]; facts: Fact[] }
  | { type: "clarification-draft"; value: string; unknown: boolean }
  | { type: "clarification-cancel" | "clarification-resume" | "retry" | "expire" | "file-cancel" }
  | { type: "clarification-submit"; id: string }
  | { type: "fact-edit"; id: string; value: string }
  | { type: "fact-confirm" | "fact-cancel" | "fact-remove"; id: string }
  | { type: "fact-add"; id: string; value: string }
  | { type: "review-details"; id: string }
  | { type: "review-continue" }
  | { type: "file-start"; id: string; facts: Fact[] }
  | { type: "file-stage"; id: string; stage: FileStage }
  | { type: "clear-start"; id: string }
  | { type: "clear-complete"; id: string; confirmed: boolean };

export function createWorkspace(): WorkspaceState {
  return { draft: "", attachments: [], messages: [], pending: null, warning: null, preview: {
    kind: null, files: [], facts: [], stage: "selected", fileRequest: null,
    clarification: "pending", value: "", unknown: false, clear: "idle", clearRequest: null, resolved: false,
  } };
}

export function workspaceReducer(state: WorkspaceState, action: WorkspaceAction): WorkspaceState {
  if (state.preview.clear === "pending" && action.type !== "clear-complete" && action.type !== "new-chat") return state;
  switch (action.type) {
    case "draft": return { ...state, draft: action.text };
    case "select": return { ...state, attachments: [...state.attachments, ...action.attachments], warning: action.warning,
      preview: { ...state.preview, files: [...state.preview.files, ...action.attachments], fileRequest: action.attachments.length ? null : state.preview.fileRequest, stage: action.attachments.length ? "selected" : state.preview.stage } };
    case "remove": return { ...state, attachments: state.attachments.filter(file => file.id !== action.id),
      preview: { ...state.preview, files: state.preview.files.filter(file => file.id !== action.id), facts: state.preview.facts.filter(fact => fact.fileId !== action.id), fileRequest: null, stage: "selected" } };
    case "new-chat": return createWorkspace();
    case "submit": {
      if (state.pending || state.preview.clear === "pending" || state.preview.fileRequest || !state.draft.trim()) return state;
      const message: Message = { id: action.id, role: "user", text: state.draft.trim(), attachments: state.attachments, sources: [] };
      return { ...state, draft: "", attachments: [], warning: null, pending: action.id, messages: [...state.messages, message] };
    }
    case "complete": {
      if (state.pending !== action.id) return state;
      const message: Message = { id: `${action.id}-answer`, role: "assistant", text: action.text, attachments: [], sources: action.sources };
      return { ...state, pending: null, messages: [...state.messages, message], preview: { ...state.preview, resolved: true } };
    }
    case "example": {
      const next = createWorkspace();
      next.preview = { ...next.preview, kind: action.kind, files: action.files, facts: action.facts, stage: action.kind === "review" ? "review" : "selected" };
      next.messages = [
        { id: action.id, role: "user", text: action.question ?? "A sample course question", attachments: [], sources: [] },
        { id: `${action.id}-example`, role: "assistant", text: "", attachments: [], sources: [], example: action.kind },
      ];
      return next;
    }
    case "clarification-draft": return { ...state, preview: { ...state.preview, value: action.value, unknown: action.unknown } };
    case "clarification-cancel": return { ...state, preview: { ...state.preview, clarification: "dismissed" } };
    case "clarification-resume": return { ...state, preview: { ...state.preview, clarification: "pending" } };
    case "clarification-submit": {
      const p = state.preview;
      if (state.pending || p.clear === "pending" || p.clarification !== "pending" || (!p.unknown && !p.value.trim())) return state;
      return { ...state, pending: action.id, preview: { ...p, clarification: "submitted" }, messages: [...state.messages,
        { id: action.id, role: "user", text: p.unknown ? "I don’t know" : p.value.trim(), attachments: [], sources: [] }] };
    }
    case "fact-confirm": {
      const fact = state.preview.facts.find(f => f.id === action.id);
      if (!fact || fact.decision === "removed" || !(fact.draft ?? fact.value).trim()) return state;
      return { ...state, preview: { ...state.preview, facts: state.preview.facts.map(f => f.id === action.id ? { ...f, value: (f.draft ?? f.value).trim(), draft: undefined, decision: "confirmed" } : f) } };
    }
    case "fact-add": return !action.value.trim() ? state : { ...state, preview: { ...state.preview, facts: [...state.preview.facts,
      { id: action.id, label: "Your detail", value: action.value.trim(), fileId: null, decision: "unconfirmed" }] } };
    case "review-details": return { ...state, preview: { ...state.preview, stage: "review" }, messages: state.messages.some(m => m.example === "review") ? state.messages : [...state.messages,
      { id: action.id, role: "assistant", text: "", sources: [], attachments: [], example: "review" }] };
    case "review-continue": return !state.preview.facts.some(f => f.decision === "confirmed") || state.preview.facts.some(f => f.draft !== undefined) ? state : {
      ...state, messages: state.messages.map(m => m.example === "review" ? { ...m, example: "advisory" } : m),
    };
    case "fact-edit":
    case "fact-cancel":
    case "fact-remove": return { ...state, preview: { ...state.preview, facts: state.preview.facts.map(f => f.id !== action.id || f.decision === "removed" ? f : {
      ...f, draft: action.type === "fact-edit" ? action.value : undefined, decision: action.type === "fact-remove" ? "removed" : "unconfirmed",
    }) } };
    case "retry": {
      if (state.pending || state.preview.resolved) return state;
      const question = state.messages.find(m => m.role === "user");
      return question ? { ...state, pending: question.id } : state;
    }
    case "file-start": return state.preview.files.length === 0 || state.preview.fileRequest ? state : { ...state, preview: { ...state.preview, stage: "checking", fileRequest: action.id, facts: action.facts } };
    case "file-stage": return state.preview.fileRequest !== action.id ? state : { ...state, preview: { ...state.preview, stage: action.stage, fileRequest: action.stage === "review" ? null : action.id } };
    case "file-cancel": return { ...state, preview: { ...state.preview, stage: "selected", fileRequest: null, facts: [] } };
    case "expire": return { ...state, pending: null, attachments: [], preview: { ...state.preview, kind: "expired", files: [], facts: [], fileRequest: null },
      messages: state.messages.map(m => ({ ...m, attachments: [], sources: [], example: m.example ? "expired" : undefined })) };
    case "clear-start": return state.preview.clear === "pending" ? state : { ...state, pending: null, preview: { ...state.preview, clear: "pending", clearRequest: action.id, fileRequest: null } };
    case "clear-complete": return state.preview.clearRequest !== action.id ? state : action.confirmed ? createWorkspace() : { ...state, preview: { ...state.preview, clear: "failed", clearRequest: null } };
  }
}

export function selectFiles(files: Iterable<Pick<File, "name" | "type" | "size">>, createId: () => string): { attachments: Attachment[]; warning: string | null } {
  const attachments: Attachment[] = [];
  let warning: string | null = null;
  for (const file of files) {
    if (!/\.(pdf|jpe?g|png)$/i.test(file.name) || (file.type && !["application/pdf", "image/jpeg", "image/png"].includes(file.type))) {
      warning = "This file type is not supported. Choose a PDF, JPG or PNG file.";
    } else if (file.size === 0 || file.size > 15 * 1024 * 1024) {
      warning = "Choose a non-empty file of 15 MiB or less for this preview.";
    } else {
      attachments.push({ id: createId(), name: file.name, type: file.type, size: file.size });
    }
  }
  return { attachments, warning };
}

export function shouldSend(event: { key: string; shiftKey?: boolean; isComposing?: boolean; keyCode?: number }): boolean {
  return event.key === "Enter" && !event.shiftKey && !event.isComposing && event.keyCode !== 229;
}
