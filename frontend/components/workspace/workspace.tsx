"use client";

import { useEffect, useId, useReducer, useRef, useState } from "react";
import { ChevronDown, Ellipsis, FolderOpen, Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { clearStudentSession, confirmStudentFile, getStudentCurricula, removeStudentFile, sendStudentMessage, uploadStudentFile } from "@/lib/student-transport";
import { StudentTransportError, type StudentChoice, type StudentCurriculum } from "@/lib/student-contracts";
import { createWorkspace, selectedPDF, workspaceReducer } from "@/lib/student-workspace";
import { Button } from "@/components/ui/button";
import { Sidebar } from "./sidebar";
import { Conversation, ConversationStarters, EmptyConversation } from "./conversation";
import { Composer } from "./composer";
import { AppearanceControl } from "./appearance-control";
import { PreviewDialog } from "./preview-dialog";
import { FilePanel, type ChatFile } from "./file-panel";
import { SourcePanel } from "./source-panel";

const stages: Record<string, string> = { waiting: "Waiting for a free answer slot… You can stop waiting.", understanding: "Checking the information for your question…", writing: "Preparing the response…" };
function errorText(error: unknown) {
  if (error instanceof StudentTransportError) {
    if (error.code === "sign_in_required" || error.code === "psu_account_required") return "Your sign-in needs attention. Sign in again to continue; your conversation is still visible here.";
    if (error.code === "answers_busy") return "All answer slots are busy. Your question is still here; try again later.";
    if (error.code === "account_busy" || error.code === "chat_in_progress") return "Another question from your account is still running. Wait for it to finish or stop it in that tab.";
    if (error.code === "already_answered") return "That question already finished on the server. Edit or resend it explicitly if you need a new check.";
  }
  return "The request did not finish. Your conversation is still here. The server may have completed it; resending starts a new check.";
}

type CurriculumState = "loading" | "ready" | "failed";
function ScopePanel({ curricula, current, busy, status, onRetry, onSave, onClose }: { curricula: StudentCurriculum[]; current: StudentCurriculum | null;
  busy: boolean; status: CurriculumState; onRetry: () => void; onSave: (scope: StudentCurriculum | null) => void; onClose: () => void }) {
  const [value, setValue] = useState(current?.curriculumId ?? "");
  return <PreviewDialog title="Program and curriculum" onClose={onClose}>
    <p>Choose your curriculum when the question depends on course requirements or when adding a PDF. You can ask general policy questions without choosing one.</p>
    {status === "loading" && <p role="status">Loading reviewed curriculum choices…</p>}
    {status === "failed" && <div role="alert"><p>Curriculum choices could not load. You can still ask general policy questions.</p><Button variant="outline" onClick={onRetry}>Try loading curricula again</Button></div>}
    {status === "ready" && !curricula.length && <p role="status">No reviewed curriculum choices are available. You can still ask general policy questions.</p>}
    <label className="scope-field">Curriculum<select disabled={status !== "ready" || !curricula.length || busy} value={value} onChange={event => setValue(event.target.value)}>
      <option value="">No selection</option>{curricula.map(option => <option key={option.curriculumId} value={option.curriculumId}>{option.programName} · {option.curriculumName}</option>)}
    </select></label>
    <p className="supporting-copy">These are reviewed research records. A proposed curriculum keeps its proposed label.</p>
    <div className="card-actions"><Button disabled={busy || status !== "ready" || !curricula.length} onClick={() => onSave(curricula.find(c => c.curriculumId === value) ?? null)}>Use selection</Button><Button variant="outline" onClick={onClose}>Cancel</Button></div>
  </PreviewDialog>;
}

export function Workspace() {
  const [state, dispatch] = useReducer(workspaceReducer, undefined, createWorkspace);
  const [curricula, setCurricula] = useState<StudentCurriculum[]>([]), [scope, setScope] = useState<StudentCurriculum | null>(null);
  const [curriculaStatus, setCurriculaStatus] = useState<CurriculumState>("loading"), [curriculaAttempt, setCurriculaAttempt] = useState(0);
  const [scopeOpen, setScopeOpen] = useState(false), [filesOpen, setFilesOpen] = useState(false), [clearOpen, setClearOpen] = useState(false);
  const [files, setFiles] = useState<ChatFile[]>([]), [fileWarning, setFileWarning] = useState<string | null>(null);
  const [sourceId, setSourceId] = useState<string | null>(null), [progress, setProgress] = useState("Connecting…");
  const [busy, setBusy] = useState<"chat" | "file" | "clear" | null>(null), [signInNeeded, setSignInNeeded] = useState(false);
  const [navigationCollapsed, setNavigationCollapsed] = useState(false), [mobileNavigation, setMobileNavigation] = useState(false);
  const optionsId = useId();
  const flight = useRef<{ controller: AbortController; id: string; kind: "chat" | "file" | "clear" } | null>(null);
  const picker = useRef<HTMLInputElement>(null), main = useRef<HTMLElement>(null);
  useEffect(() => {
    const controller = new AbortController();
    setCurriculaStatus("loading");
    getStudentCurricula(controller.signal).then(value => { if (!controller.signal.aborted) { setCurricula(value); setCurriculaStatus("ready"); } }).catch(error => {
      if (controller.signal.aborted) return;
      setCurriculaStatus("failed");
      if (error instanceof StudentTransportError && error.status === 401) setSignInNeeded(true);
    });
    return () => controller.abort();
  }, [curriculaAttempt]);
  useEffect(() => () => flight.current?.controller.abort(), []);
  function draft(text: string) { dispatch({ type: "draft", text }); requestAnimationFrame(() => main.current?.querySelector("textarea")?.focus()); }
  function begin(kind: "chat" | "file" | "clear") {
    const value = { controller: new AbortController(), id: "msg-" + crypto.randomUUID(), kind };
    flight.current = value; setBusy(kind); return value;
  }
  function finish(value: NonNullable<typeof flight.current>) { if (flight.current === value) { flight.current = null; setBusy(null); } }
  function authError(error: unknown) { if (error instanceof StudentTransportError && error.status === 401) setSignInNeeded(true); }
  async function send() {
    if (flight.current || !state.draft.trim() || signInNeeded) return;
    const value = begin("chat"), text = state.draft.trim();
    dispatch({ type: "submit", id: value.id }); setProgress("Connecting…");
    try {
      const answer = await sendStudentMessage({ id: value.id, text, ...(scope ? { programId: scope.programId, curriculumId: scope.curriculumId } : {}) }, {
        signal: value.controller.signal,
        onText: text => { if (!value.controller.signal.aborted) dispatch({ type: "delta", id: value.id, text }); },
        onProgress: stage => { if (!value.controller.signal.aborted) setProgress(stages[stage]); },
      });
      if (!value.controller.signal.aborted) dispatch({ type: "complete", id: value.id, answer });
    } catch (error) { if (!value.controller.signal.aborted) { authError(error); dispatch({ type: "interrupt", id: value.id, warning: errorText(error) }); } }
    finally { finish(value); }
  }
  function stop() {
    const value = flight.current;
    if (!value || value.kind !== "chat") return;
    value.controller.abort(); flight.current = null; setBusy(null);
    dispatch({ type: "interrupt", id: value.id, warning: "Response stopped. Your question remains in the conversation." });
  }
  async function clear() {
    if (flight.current?.kind === "file" || flight.current?.kind === "clear") return;
    stop(); const value = begin("clear");
    try {
      await clearStudentSession(value.controller.signal);
      if (!value.controller.signal.aborted) {
        dispatch({ type: "clear" }); setFiles([]); setScope(null); setSourceId(null); setFileWarning(null); setClearOpen(false); setFilesOpen(false);
      }
    } catch (error) { authError(error); dispatch({ type: "warning", warning: "Clearing was not confirmed. Your conversation and files are still here." }); }
    finally { finish(value); }
  }
  async function selectFiles(selected: File[]) {
    if (flight.current) return;
    const selection = selectedPDF(selected);
    setFileWarning(selection.warning);
    if (!selection.file) return;
    if (!scope) { setFileWarning("Choose your program and curriculum before adding a PDF."); setScopeOpen(true); return; }
    if (files.some(file => !file.confirmed)) { setFileWarning("Review or remove the pending PDF before adding another."); setFilesOpen(true); return; }
    if (files.length >= 8) { setFileWarning("Remove a file before adding another. This chat can hold eight file references."); return; }
    const file = selection.file, value = begin("file"); setFilesOpen(true);
    try {
      const review = await uploadStudentFile(file, scope, value.controller.signal);
      if (!value.controller.signal.aborted) setFiles(previous => [...previous, { id: review.uploadId, name: file.name,
        scope: scope.programName + " · " + scope.curriculumName, review, confirmed: false }]);
    } catch (error) { if (!value.controller.signal.aborted) { authError(error); setFileWarning(error instanceof StudentTransportError && error.code === "no_rows" ? "No supported course rows were found. You can type course details instead." : "The PDF could not be reviewed. Existing files are unchanged. Choose a readable, text-based PDF or type your details."); } }
    finally { finish(value); }
  }
  async function fileAction(id: string, choices?: StudentChoice[]) {
    if (flight.current) return;
    const value = begin("file"); setFileWarning(null);
    try {
      if (choices) await confirmStudentFile(id, choices, value.controller.signal);
      else await removeStudentFile(id, value.controller.signal);
      if (!value.controller.signal.aborted) setFiles(previous => choices ? previous.map(file => file.id === id ? { ...file, confirmed: true } : file) : previous.filter(file => file.id !== id));
    } catch (error) { if (!value.controller.signal.aborted) { authError(error); setFileWarning("The file change was not confirmed. Your file list is unchanged."); } }
    finally { finish(value); }
  }
  async function signOut() {
    if (flight.current) return;
    const value = begin("clear");
    try {
      const response = await fetch("/auth/signout", { method: "POST", signal: value.controller.signal });
      if (response.status !== 204) throw new Error("signout_unavailable");
      dispatch({ type: "clear" }); setFiles([]); window.location.assign("/login");
    } catch { dispatch({ type: "warning", warning: "Sign-out did not finish. Your conversation is still visible here; try again." }); }
    finally { finish(value); }
  }
  return <div className={`workspace live-workspace${navigationCollapsed ? " navigation-collapsed" : ""}`}>
    <a className="skip-link" href="#question">Skip to question</a>
    <Sidebar live className="desktop-sidebar" hidden={navigationCollapsed} busy={busy === "file" || busy === "clear"} onNewChat={() => setClearOpen(true)} onExample={draft} />
    <main className="workspace-main" id="question" tabIndex={-1} ref={main}>
      {!state.messages.length && <div className="campus-banner" aria-hidden="true"><img src="/design/campus.png" alt="" /></div>}
      <header className="workspace-toolbar">
        {!!state.messages.length && <h1 className="sr-only">Your conversation with Bintanong</h1>}
        <div className="workspace-heading">
          <Button variant="ghost" size="icon" className="desktop-navigation-toggle" aria-label={navigationCollapsed ? "Open navigation" : "Close navigation"} aria-expanded={!navigationCollapsed} onClick={() => setNavigationCollapsed(value => !value)}>{navigationCollapsed ? <PanelLeftOpen aria-hidden="true" /> : <PanelLeftClose aria-hidden="true" />}</Button>
          <Button variant="ghost" size="icon" className="mobile-navigation-toggle" aria-label="Open navigation" aria-expanded={mobileNavigation} onClick={() => setMobileNavigation(true)}><Menu aria-hidden="true" /></Button>
          <span className="workspace-name">Bintanong</span><p className="preview-notice">Research preview</p>
        </div>
        <Button variant="ghost" size="icon" aria-label="Chat options" title="Chat options" popoverTarget={optionsId}><Ellipsis aria-hidden="true" /></Button>
        <div id={optionsId} popover="auto" className="workspace-options"><AppearanceControl /><p className="supporting-copy">University validation is pending.</p><form action="/auth/signout" method="post" onSubmit={event => { event.preventDefault(); void signOut(); }}><Button type="submit" variant="outline" disabled={!!busy}>Sign out</Button></form></div>
      </header>
      <div className={`workspace-content${state.messages.length ? "" : " welcome-mode"}`}>
      {state.messages.length ? <Conversation state={state} progress={progress} onSource={setSourceId} onScope={() => { if (!flight.current) setScopeOpen(true); }} /> : <EmptyConversation />}
      {state.warning && <div className="outcome-notice status-danger" role="alert"><p>{state.warning}</p>{signInNeeded && <a href="/login">Sign in again</a>}{state.messages.some(message => message.role === "user") && <Button variant="outline" size="sm" onClick={() => draft(state.messages.findLast(message => message.role === "user")?.text ?? "")}>Edit question</Button>}</div>}
      {signInNeeded && !state.warning && <p className="session-notice" role="alert">Your sign-in needs attention. <a href="/login">Sign in again</a> to continue.</p>}
      <Composer live picker={picker} draft={state.draft} attachments={[]} warning={fileWarning} pending={!!busy || signInNeeded}
        onDraft={text => dispatch({ type: "draft", text })} onSend={send} onStop={busy === "chat" ? stop : undefined} onSelect={selectFiles} onRemove={() => {}}
        tools={<><Button type="button" variant="ghost" size="sm" disabled={!!busy} aria-label={scope ? scope.curriculumName : "Program and curriculum"} title={scope ? `${scope.programName} · ${scope.curriculumName}` : "Choose a curriculum for course checks or PDF review"} onClick={() => setScopeOpen(true)}><span className="composer-scope-label">{scope ? scope.curriculumName : "Curriculum"}</span><ChevronDown size={14} aria-hidden="true" /></Button><Button type="button" variant="ghost" size="sm" disabled={!!busy} aria-label="Files in this chat" onClick={() => setFilesOpen(true)}><FolderOpen size={16} aria-hidden="true" />Files{files.length ? ` (${files.length})` : ""}</Button></>}
        starters={!state.messages.length && <ConversationStarters onSuggest={draft} />} />
      {curriculaStatus === "failed" && !scope && <p className="scope-summary">Curriculum choices are unavailable. General policy questions are still welcome.</p>}
      </div>
      {mobileNavigation && <PreviewDialog title="Navigation" side className="navigation-dialog" onClose={() => setMobileNavigation(false)}><Sidebar live busy={busy === "file" || busy === "clear"} onNewChat={() => { setMobileNavigation(false); setClearOpen(true); }} onExample={text => { setMobileNavigation(false); draft(text); }} /></PreviewDialog>}
      {sourceId && <SourcePanel key={sourceId} sourceId={sourceId} onClose={() => setSourceId(null)} />}
      {scopeOpen && <ScopePanel curricula={curricula} current={scope} status={curriculaStatus} onRetry={() => setCurriculaAttempt(n => n + 1)} busy={!!busy} onClose={() => setScopeOpen(false)} onSave={value => { setScope(value); setScopeOpen(false); }} />}
      {filesOpen && <FilePanel files={files} busy={busy === "file"} warning={fileWarning} onClose={() => setFilesOpen(false)} onPick={() => picker.current?.click()}
        onConfirm={fileAction} onRemove={id => fileAction(id)} onType={() => { setFilesOpen(false); main.current?.querySelector("textarea")?.focus(); }} />}
      {clearOpen && <PreviewDialog title="Clear this chat?" busy={busy === "clear"} onClose={() => setClearOpen(false)}>
        <p>This removes the server’s temporary context and clears the conversation after confirmation.</p>
        {busy === "clear" ? <p role="status">Waiting for confirmation…</p> : <div className="card-actions"><Button onClick={clear}>Clear chat</Button><Button variant="outline" onClick={() => setClearOpen(false)}>Cancel</Button></div>}
      </PreviewDialog>}
    </main>
  </div>;
}
