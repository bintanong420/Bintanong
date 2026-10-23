"use client";

import { useEffect, useReducer, useRef } from "react";
import { createWorkspace, selectFiles, workspaceReducer } from "@/lib/workspace";
import { prepareDemo } from "@/lib/demo";
import { Sidebar } from "./sidebar";
import { Conversation, EmptyConversation } from "./conversation";
import { Composer } from "./composer";

export function Workspace() {
  const [state, dispatch] = useReducer(workspaceReducer, undefined, createWorkspace);
  const main = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!state.pending) return;
    const controller = new AbortController();
    const id = state.pending;
    prepareDemo(controller.signal).then(answer => dispatch({ type: "complete", id, ...answer })).catch(error => {
      if (!controller.signal.aborted) dispatch({ type: "complete", id, text: "This interface example could not be prepared. No academic answer was generated. Start a new preview chat to try again.", sources: [] });
    });
    return () => controller.abort();
  }, [state.pending]);

  function chooseDraft(text: string) {
    dispatch({ type: "draft", text });
    main.current?.querySelector<HTMLTextAreaElement>("textarea")?.focus();
  }

  return <div className="workspace">
    <a className="skip-link" href="#question">Skip to question</a>
    <Sidebar onNewChat={() => dispatch({ type: "new-chat" })} onExample={chooseDraft} />
    <main className="workspace-main" ref={main} id="question" tabIndex={-1}>
      {state.messages.length === 0 && <div className="campus-banner" aria-hidden="true"><img src="/design/campus.png" alt="" /></div>}
      <div className="preview-notice"><span>Interface preview</span> · Fictional responses. Files stay local and are not analyzed.</div>
      {state.messages.length === 0 ? <EmptyConversation onSuggest={chooseDraft} /> : <Conversation messages={state.messages} pending={state.pending !== null} />}
      <Composer draft={state.draft} attachments={state.attachments} pending={state.pending !== null} warning={state.warning}
        onDraft={text => dispatch({ type: "draft", text })} onSend={() => dispatch({ type: "submit", id: crypto.randomUUID() })}
        onSelect={files => dispatch({ type: "select", ...selectFiles(files, () => crypto.randomUUID()) })} onRemove={id => dispatch({ type: "remove", id })} />
    </main>
  </div>;
}
