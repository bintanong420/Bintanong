import type { StudentAnswer } from "./student-contracts.ts";

export type Attachment = { id: string; name: string; type: string };
export type Message = { id: string; role: "user" | "assistant"; text: string; answer?: StudentAnswer; delivery?: "streaming" | "interrupted" };
export type WorkspaceState = { draft: string; messages: Message[]; pending: string | null; warning: string | null };
export type WorkspaceAction = { type: "draft"; text: string } | { type: "submit"; id: string }
  | { type: "delta"; id: string; text: string } | { type: "complete"; id: string; answer: StudentAnswer }
  | { type: "interrupt"; id: string; warning: string } | { type: "warning"; warning: string | null } | { type: "clear" };
export const createWorkspace = (): WorkspaceState => ({ draft: "", messages: [], pending: null, warning: null });
export function workspaceReducer(state: WorkspaceState, action: WorkspaceAction): WorkspaceState {
  if (action.type === "draft") return { ...state, draft: action.text };
  if (action.type === "warning") return { ...state, warning: action.warning };
  if (action.type === "clear") return createWorkspace();
  if (action.type === "submit") {
    if (state.pending || !state.draft.trim()) return state;
    return { ...state, draft: "", warning: null, pending: action.id, messages: [...state.messages,
      { id: action.id, role: "user", text: state.draft.trim() },
      { id: action.id + "-answer", role: "assistant", text: "", delivery: "streaming" }] };
  }
  if (state.pending !== action.id) return state;
  const messages = state.messages.map(message => message.id !== action.id + "-answer" ? message :
    action.type === "delta" ? { ...message, text: message.text + action.text } :
    action.type === "complete" ? { ...message, text: action.answer.text, answer: action.answer, delivery: undefined } :
    { ...message, delivery: "interrupted" as const });
  return { ...state, messages, pending: action.type === "delta" ? state.pending : null,
    warning: action.type === "interrupt" ? action.warning : state.warning };
}
export function shouldSend(event: { key: string; shiftKey: boolean; isComposing: boolean; keyCode: number }) {
  return event.key === "Enter" && !event.shiftKey && !event.isComposing && event.keyCode !== 229;
}
export function selectedPDF(files: File[]): { file: File | null; warning: string | null } {
  if (!files.length) return { file: null, warning: null };
  if (files.length !== 1) return { file: null, warning: "Choose one PDF at a time so you can review its details." };
  const file = files[0];
  if (!/\.pdf$/i.test(file.name) || file.size < 1 || file.size > 15 * 1024 * 1024) return {
    file: null, warning: "Choose a PDF up to 15 MB. Photos and scanned documents are not supported yet." };
  return { file, warning: null };
}
