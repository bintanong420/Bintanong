"use client";

import { useEffect, useReducer, useRef, useState } from "react";
import { createWorkspace, selectFiles, workspaceReducer, type ExampleKind } from "@/lib/workspace";
import { exampleAction, prepareDemo, previewDelay, previewExamples } from "@/lib/demo";
import { Button } from "@/components/ui/button";
import { FolderOpen } from "lucide-react";
import { Sidebar } from "./sidebar";
import { Conversation, EmptyConversation } from "./conversation";
import { Composer } from "./composer";
import { AppearanceControl } from "./appearance-control";
import { InspectionPanel } from "./inspection-panel";
import { PreviewDialog } from "./preview-dialog";

export function Workspace() {
  const [state, dispatch] = useReducer(workspaceReducer, undefined, createWorkspace);
  const main = useRef<HTMLElement>(null);
  const picker = useRef<HTMLInputElement>(null);
  const [panel, setPanel] = useState<"files" | "sources" | null>(null);
  const [clearOpen, setClearOpen] = useState(false);
  useEffect(() => {
    if (!state.pending) return;
    const controller = new AbortController();
    const id = state.pending;
    prepareDemo(controller.signal).then(answer => dispatch({ type: "complete", id, ...answer })).catch(error => {
      if (!controller.signal.aborted) dispatch({ type: "complete", id, text: "This interface example could not be prepared. No academic answer was generated. Start a new preview chat to try again.", sources: [] });
    });
    return () => controller.abort();
  }, [state.pending]);

  useEffect(() => {
    const id = state.preview.fileRequest;
    if (!id) return;
    const controller = new AbortController();
    async function run() {
      await previewDelay(controller.signal);
      dispatch({ type: "file-stage", id: id!, stage: "reading" });
      await previewDelay(controller.signal);
      dispatch({ type: "file-stage", id: id!, stage: "review" });
    }
    run().catch(() => { if (!controller.signal.aborted) dispatch({ type: "file-cancel" }); });
    return () => controller.abort();
  }, [state.preview.fileRequest]);

  useEffect(() => {
    const id = state.preview.clearRequest;
    if (!id) return;
    const controller = new AbortController();
    const confirmed = state.preview.kind !== "clear-failed";
    previewDelay(controller.signal).then(() => {
      dispatch({ type: "clear-complete", id, confirmed });
      if (confirmed) { setClearOpen(false); setPanel(null); main.current?.scrollTo({ top: 0 }); }
    }).catch(() => { if (!controller.signal.aborted) dispatch({ type: "clear-complete", id, confirmed: false }); });
    return () => controller.abort();
  }, [state.preview.clearRequest, state.preview.kind]);

  function newChat() {
    dispatch({ type: "new-chat" }); setPanel(null); setClearOpen(false); main.current?.scrollTo({ top: 0 });
  }
  function loadExample(kind: string) {
    if (!kind) return newChat();
    dispatch(exampleAction(kind as ExampleKind, crypto.randomUUID()));
    if (kind === "expired") dispatch({ type: "expire" });
    main.current?.scrollTo({ top: 0 });
  }
  function focusDraft() { main.current?.querySelector<HTMLTextAreaElement>(".composer textarea")?.focus(); }
  function pickFiles() { setPanel(null); picker.current?.click(); }
  function reviewDetails() { setPanel(null); dispatch({ type: "review-details", id: crypto.randomUUID() }); }

  function chooseDraft(text: string) {
    dispatch({ type: "draft", text });
    focusDraft();
  }

  return <div className="workspace">
    <a className="skip-link" href="#question">Skip to question</a>
    <Sidebar onNewChat={newChat} onExample={chooseDraft} />
    <main className="workspace-main" ref={main} id="question" tabIndex={-1}>
      {state.messages.length === 0 && <div className="campus-banner" aria-hidden="true"><img src="/design/campus.png" alt="" /></div>}
      <header className="workspace-toolbar">
        <p className="preview-notice"><span>Interface preview</span> · Fictional responses and sample details. Files stay local.</p>
        <label className="example-picker"><span>Preview example</span><select value={state.preview.kind ?? ""} onChange={e => loadExample(e.target.value)}><option value="">New chat</option>{previewExamples.map(e => <option key={e.kind} value={e.kind}>{e.label}</option>)}</select></label>
        <div className="toolbar-actions"><Button variant="outline" size="sm" onClick={() => setPanel("files")}><FolderOpen aria-hidden="true" size={16} />Files in this chat{state.preview.files.length > 0 && ` (${state.preview.files.length})`}</Button><AppearanceControl /></div>
      </header>
      {state.messages.length === 0 ? <EmptyConversation onSuggest={chooseDraft} /> : <Conversation state={state} dispatch={dispatch} onFiles={() => setPanel("files")} onSources={() => setPanel("sources")} onPickFiles={pickFiles} onEdit={chooseDraft} onFocusDraft={focusDraft} />}
      <Composer picker={picker} draft={state.draft} attachments={state.attachments} pending={state.pending !== null || !!state.preview.fileRequest || state.preview.clear === "pending"} warning={state.warning}
        onDraft={text => dispatch({ type: "draft", text })} onSend={() => dispatch({ type: "submit", id: crypto.randomUUID() })}
        onSelect={files => dispatch({ type: "select", ...selectFiles(files, () => crypto.randomUUID()) })} onRemove={id => dispatch({ type: "remove", id })} />
      {panel && <InspectionPanel mode={panel} state={state} dispatch={dispatch} onClose={() => setPanel(null)} onClear={() => setClearOpen(true)} onReview={reviewDetails} onPickFiles={pickFiles} />}
      {clearOpen && <PreviewDialog title="Clear this preview chat?" onClose={() => setClearOpen(false)} busy={state.preview.clear === "pending"}>
        <p>This removes messages, filename chips and details from this page. No files have been uploaded.</p>
        {state.preview.clear === "pending" ? <p className="outcome-notice status-info" role="status">Clearing preview… waiting for the simulated result.</p> : <>
          {state.preview.clear === "failed" && <p className="outcome-notice status-danger" role="alert">The example clear request was not confirmed. Your conversation, files and details are unchanged.</p>}
          <div className="card-actions"><Button onClick={() => dispatch({ type: "clear-start", id: crypto.randomUUID() })}>{state.preview.clear === "failed" ? "Try again" : "Clear chat"}</Button><Button variant="outline" onClick={() => setClearOpen(false)}>Cancel</Button></div>
        </>}
      </PreviewDialog>}
    </main>
  </div>;
}
