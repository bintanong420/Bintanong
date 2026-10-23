export type Attachment = { id: string; name: string; size: number; type: string };
export type Message = { id: string; role: "user" | "assistant"; text: string; attachments: Attachment[]; sources: string[] };
export type WorkspaceState = { draft: string; attachments: Attachment[]; messages: Message[]; pending: string | null; warning: string | null };
export type WorkspaceAction =
  | { type: "draft"; text: string }
  | { type: "select"; attachments: Attachment[]; warning: string | null }
  | { type: "remove"; id: string }
  | { type: "submit"; id: string }
  | { type: "complete"; id: string; text: string; sources: string[] }
  | { type: "new-chat" };

export function createWorkspace(): WorkspaceState {
  return { draft: "", attachments: [], messages: [], pending: null, warning: null };
}

export function workspaceReducer(state: WorkspaceState, action: WorkspaceAction): WorkspaceState {
  switch (action.type) {
    case "draft": return { ...state, draft: action.text };
    case "select": return { ...state, attachments: [...state.attachments, ...action.attachments], warning: action.warning };
    case "remove": return { ...state, attachments: state.attachments.filter(file => file.id !== action.id) };
    case "new-chat": return createWorkspace();
    case "submit": {
      if (state.pending || !state.draft.trim()) return state;
      const message: Message = { id: action.id, role: "user", text: state.draft.trim(), attachments: state.attachments, sources: [] };
      return { ...state, draft: "", attachments: [], warning: null, pending: action.id, messages: [...state.messages, message] };
    }
    case "complete": {
      if (state.pending !== action.id) return state;
      const message: Message = { id: `${action.id}-answer`, role: "assistant", text: action.text, attachments: [], sources: action.sources };
      return { ...state, pending: null, messages: [...state.messages, message] };
    }
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
