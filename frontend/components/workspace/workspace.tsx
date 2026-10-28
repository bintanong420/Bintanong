"use client";

import { useCallback, useEffect, useId, useReducer, useRef, useState } from "react";
import { ChevronDown, ClipboardList, Ellipsis, FolderOpen, LogOut, Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { clearStudentSession, confirmStudentFile, getStudentCurricula, removeStudentFile, sendStudentMessage, uploadStudentFile } from "@/lib/student-transport";
import { StudentTransportError, type StudentAnswer, type StudentChoice, type StudentCurriculum, type StudentScope, type StudentSourceSummary } from "@/lib/student-contracts";
import { createWorkspace, selectedPDF, workspaceReducer } from "@/lib/student-workspace";
import { Button } from "@/components/ui/button";
import { Sidebar } from "./sidebar";
import { Conversation, ConversationStarters, EmptyConversation } from "./conversation";
import { Composer } from "./composer";
import { AppearanceControl } from "./appearance-control";
import { PreviewDialog } from "./preview-dialog";
import { FilePanel, type ChatFile } from "./file-panel";
import { SourcePanel } from "./source-panel";
import { ClarificationDialog } from "./clarification-dialog";
import { clarificationQuestions, confirmedDetails, followUpMessage, sameScope } from "@/lib/student-clarification";
import { RephraseDialog, SuppliedDetailsPanel } from "./follow-up-dialog";

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
  return <PreviewDialog title="Program and curriculum" className="curriculum-dialog" onClose={onClose}>
    <p>Choose the curriculum you follow so Bintanong can check your subjects and prerequisites. You'll also need it when adding a PDF.</p>
    <p className="supporting-copy">You can skip this for questions about enrollment or university policies.</p>
    {status === "loading" && <p role="status">Loading programs and curricula…</p>}
    {status === "failed" && <div className="curriculum-status" role="alert"><p>We couldn't load the program and curriculum list. Try again in a moment.</p><Button variant="outline" onClick={onRetry}>Try again</Button></div>}
    {status === "ready" && !curricula.length && <p role="status">No curricula are available yet. You can leave this blank.</p>}
    <label className="scope-field">Program and curriculum<select disabled={status !== "ready" || !curricula.length || busy} value={value} onChange={event => setValue(event.target.value)}>
      <option value="">Not selected</option>{curricula.map(option => <option key={option.curriculumId} value={option.curriculumId}>{option.programName} · {option.curriculumName}</option>)}
    </select></label>
    <p className="supporting-copy">Not sure which version you follow? Check your prospectus or ask your academic adviser. A curriculum marked “Proposed” may not apply to you.</p>
    <div className="card-actions"><Button disabled={busy || status !== "ready" || !curricula.length} onClick={() => onSave(curricula.find(c => c.curriculumId === value) ?? null)}>{value ? "Use this curriculum" : "Continue without selecting"}</Button><Button variant="outline" onClick={onClose}>Cancel</Button></div>
  </PreviewDialog>;
}

export function Workspace() {
  const [state, dispatch] = useReducer(workspaceReducer, undefined, createWorkspace);
  const [curricula, setCurricula] = useState<StudentCurriculum[]>([]), [scope, setScope] = useState<StudentCurriculum | null>(null);
  const [curriculaStatus, setCurriculaStatus] = useState<CurriculumState>("loading"), [curriculaAttempt, setCurriculaAttempt] = useState(0);
  const [scopeOpen, setScopeOpen] = useState(false), [filesOpen, setFilesOpen] = useState(false), [clearOpen, setClearOpen] = useState(false);
  const [files, setFiles] = useState<ChatFile[]>([]), [fileWarning, setFileWarning] = useState<string | null>(null);
  const [sources, setSources] = useState<StudentSourceSummary[] | null>(null), [progress, setProgress] = useState("Connecting…");
  const [detailsOpen, setDetailsOpen] = useState(false), [rephraseOpen, setRephraseOpen] = useState(false), [selectedDetails, setSelectedDetails] = useState<string[]>([]);
  const [review, setReview] = useState<{ text: string; scope: StudentScope | null } | null>(null);
  const [busy, setBusy] = useState<"chat" | "file" | "clear" | "signout" | null>(null), [signInNeeded, setSignInNeeded] = useState(false);
  const [signOutFailed, setSignOutFailed] = useState(false);
  const [navigationCollapsed, setNavigationCollapsed] = useState(false), [mobileNavigation, setMobileNavigation] = useState(false);
  const [clarification, setClarification] = useState<{ id: string; original: string; answer: StudentAnswer; scope: StudentScope | null; open: boolean } | null>(null);
  const optionsId = useId();
  const flight = useRef<{ controller: AbortController; id: string; kind: "chat" | "file" | "clear" | "signout" } | null>(null);
  const picker = useRef<HTMLInputElement>(null), main = useRef<HTMLElement>(null);
  const details = state.supplied.filter(detail => sameScope(detail, scope));
  const authError = useCallback((error: unknown) => {
    if (error instanceof StudentTransportError && error.status === 401) {
      setSignInNeeded(true); dispatch({ type: "forget-details" }); setSelectedDetails([]); setReview(null); setDetailsOpen(false); setClarification(null);
    }
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    setCurriculaStatus("loading");
    getStudentCurricula(controller.signal).then(value => { if (!controller.signal.aborted) { setCurricula(value); setCurriculaStatus("ready"); } }).catch(error => {
      if (controller.signal.aborted) return;
      setCurriculaStatus("failed");
      authError(error);
    });
    return () => controller.abort();
  }, [curriculaAttempt, authError]);
  useEffect(() => () => flight.current?.controller.abort(), []);
  function draft(text: string) { dispatch({ type: "draft", text }); requestAnimationFrame(() => main.current?.querySelector("textarea")?.focus()); }
  function openCurrentChat() { setMobileNavigation(false); requestAnimationFrame(() => main.current?.querySelector("textarea")?.focus()); }
  function begin(kind: "chat" | "file" | "clear" | "signout") {
    const value = { controller: new AbortController(), id: "msg-" + crypto.randomUUID(), kind };
    flight.current = value; setBusy(kind); return value;
  }
  function finish(value: NonNullable<typeof flight.current>) { if (flight.current === value) { flight.current = null; setBusy(null); } }
  function changeScope(value: StudentCurriculum | null) {
    if (!sameScope(scope, value)) { dispatch({ type: "forget-details" }); setSelectedDetails([]); setReview(null); setClarification(null); }
    setScope(value);
  }
  function prepareSend() {
    if (flight.current || signInNeeded || !state.draft.trim()) return;
    try {
      const text = followUpMessage(state.draft, scope, details, selectedDetails);
      if (selectedDetails.length) setReview({ text, scope });
      else void send();
    } catch { dispatch({ type: "warning", warning: "This message could not be prepared. Shorten the question or review the selected course details." }); }
  }
  async function send(confirmed?: { text: string; scope: StudentScope | null; clearDraft?: boolean }) {
    const text = (confirmed?.text ?? state.draft).trim(), selectedScope = confirmed ? confirmed.scope : scope;
    if (flight.current || !text || signInNeeded) return;
    const value = begin("chat");
    setClarification(null); setSelectedDetails([]); setReview(null);
    dispatch({ type: "submit", id: value.id, ...(confirmed ? { text, clearDraft: confirmed.clearDraft } : {}) }); setProgress("Connecting…");
    try {
      const answer = await sendStudentMessage({ id: value.id, text, ...(selectedScope ? { programId: selectedScope.programId, curriculumId: selectedScope.curriculumId } : {}) }, {
        signal: value.controller.signal,
        onText: text => { if (!value.controller.signal.aborted) dispatch({ type: "delta", id: value.id, text }); },
        onProgress: stage => { if (!value.controller.signal.aborted) setProgress(stages[stage]); },
      });
      if (!value.controller.signal.aborted) {
        dispatch({ type: "complete", id: value.id, answer });
        if (clarificationQuestions(answer, curricula).length) setClarification({ id: value.id + "-answer", original: text, answer, scope: selectedScope, open: false });
      }
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
    if (flight.current && flight.current.kind !== "chat") return;
    stop(); const value = begin("clear");
    try {
      await clearStudentSession(value.controller.signal);
      if (!value.controller.signal.aborted) {
        dispatch({ type: "clear" }); setClarification(null); setFiles([]); setScope(null); setSources(null); setFileWarning(null); setClearOpen(false); setFilesOpen(false);
        setSelectedDetails([]); setReview(null); setDetailsOpen(false); setRephraseOpen(false);
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
    stop();
    if (flight.current) return;
    const value = begin("signout"); setSignOutFailed(false);
    try {
      const response = await fetch("/auth/signout", { method: "POST", signal: value.controller.signal });
      if (response.status !== 204) throw new Error("signout_unavailable");
      dispatch({ type: "clear" }); setClarification(null); setFiles([]); setSelectedDetails([]); setReview(null); setDetailsOpen(false);
      window.location.assign(response.headers.get("x-bintanong-signout-notice") === "cleanup_pending" ? "/login?notice=cleanup_pending" : "/login?notice=signed_out");
    } catch { setSignOutFailed(true); }
    finally { finish(value); }
  }
  return <div className={`workspace live-workspace${navigationCollapsed ? " navigation-collapsed" : ""}`}>
    <a className="skip-link" href="#question">Skip to question</a>
    <Sidebar currentChat={state.messages.find(message => message.role === "user")} className="desktop-sidebar" hidden={navigationCollapsed} busy={!!busy && busy !== "chat"} onNewChat={() => setClearOpen(true)} onOpenChat={openCurrentChat} />
    <main className="workspace-main" id="question" tabIndex={-1} ref={main}>
      {!state.messages.length && <div className="campus-banner" aria-hidden="true"><img src="/design/campus.png" alt="" /></div>}
      <header className="workspace-toolbar">
        {!!state.messages.length && <h1 className="sr-only">Your conversation with Bintanong</h1>}
        <div className="workspace-heading">
          <Button variant="ghost" size="icon" className="desktop-navigation-toggle" aria-label={navigationCollapsed ? "Open navigation" : "Close navigation"} aria-expanded={!navigationCollapsed} onClick={() => setNavigationCollapsed(value => !value)}>{navigationCollapsed ? <PanelLeftOpen aria-hidden="true" /> : <PanelLeftClose aria-hidden="true" />}</Button>
          <Button variant="ghost" size="icon" className="mobile-navigation-toggle" aria-label="Open navigation" aria-expanded={mobileNavigation} onClick={() => setMobileNavigation(true)}><Menu aria-hidden="true" /></Button>
          <span className="workspace-name">Bintanong</span>
          <Button type="button" variant="ghost" className="header-scope" disabled={!!busy} aria-label="Program and curriculum" title={scope ? `${scope.programName} · ${scope.curriculumName}` : "Choose your program and curriculum"} onClick={() => setScopeOpen(true)}>
            <span>{scope ? scope.curriculumName : "Choose curriculum"}</span><ChevronDown size={14} aria-hidden="true" />
          </Button>
        </div>
        <div className="workspace-account-actions">
          {details.length > 0 && <Button type="button" variant="ghost" size="sm" className="header-details" aria-label={`You supplied (${details.length})`} title={`You supplied (${details.length})`} disabled={!!busy || signInNeeded} onClick={() => setDetailsOpen(true)}><ClipboardList size={16} aria-hidden="true" /><span className="account-action-label">You supplied ({details.length})</span></Button>}
          <Button variant="ghost" size="icon" aria-label="Chat options" title="Chat options" popoverTarget={optionsId}><Ellipsis aria-hidden="true" /></Button>
          <Button variant="ghost" className="header-signout" aria-label={busy === "signout" ? "Signing out…" : "Sign out"} title={busy === "signout" ? "Signing out…" : "Sign out"} disabled={busy === "file" || busy === "clear" || busy === "signout"} onClick={() => void signOut()}><LogOut size={16} aria-hidden="true" /><span className="account-action-label">{busy === "signout" ? "Signing out…" : "Sign out"}</span></Button></div>
        <div id={optionsId} popover="auto" className="workspace-options"><AppearanceControl /><p className="supporting-copy">Research preview. University validation is still pending.</p></div>
      </header>
      <div className={`workspace-content${state.messages.length ? "" : " welcome-mode"}`}>
      {state.messages.length ? <Conversation state={state} progress={progress} onSource={setSources} canClarify={!!clarification && !signInNeeded} onEdit={draft} onRephrase={() => setRephraseOpen(true)} onClarify={() => { if (!flight.current) setClarification(previous => previous ? { ...previous, open: true } : null); }} /> : <EmptyConversation />}
      {signOutFailed && <div className="outcome-notice status-danger" role="alert"><p>We couldn't finish signing you out. Try again before leaving this device.</p><Button variant="outline" disabled={!!busy} onClick={() => void signOut()}>Try signing out again</Button></div>}
      {state.warning && <div className="outcome-notice status-danger" role="alert"><p>{state.warning}</p>{signInNeeded && <a href="/login">Sign in again</a>}{state.messages.some(message => message.role === "user") && <Button variant="outline" size="sm" onClick={() => draft(state.messages.findLast(message => message.role === "user")?.text ?? "")}>Edit question</Button>}</div>}
      {signInNeeded && !state.warning && <p className="session-notice" role="alert">Your sign-in needs attention. <a href="/login">Sign in again</a> to continue.</p>}
      <Composer live picker={picker} draft={state.draft} attachments={[]} warning={fileWarning} pending={!!busy || signInNeeded}
        onDraft={text => dispatch({ type: "draft", text })} onSend={prepareSend} onStop={busy === "chat" ? stop : undefined} onSelect={selectFiles} onRemove={() => {}}
        contextNote={selectedDetails.length ? `${selectedDetails.length} earlier details selected. Review before sending.` : undefined}
        tools={<><Button type="button" variant="ghost" size="sm" disabled={!!busy} aria-label="Files in this chat" onClick={() => setFilesOpen(true)}><FolderOpen size={16} aria-hidden="true" />Files{files.length ? ` (${files.length})` : ""}</Button>
          {details.length > 0 && <Button type="button" variant="ghost" size="sm" disabled={!!busy || signInNeeded} onClick={() => setDetailsOpen(true)}>Include earlier details{selectedDetails.length ? ` (${selectedDetails.length})` : ""}</Button>}</>}
        starters={!state.messages.length && <ConversationStarters onSuggest={draft} />} />
      {curriculaStatus === "failed" && !scope && <p className="scope-summary">We couldn't load the curriculum list. <button type="button" className="text-action" onClick={() => setScopeOpen(true)}>Try again</button></p>}
      </div>
      {mobileNavigation && <PreviewDialog title="Navigation" side className="navigation-dialog" onClose={() => setMobileNavigation(false)}><Sidebar currentChat={state.messages.find(message => message.role === "user")} busy={!!busy && busy !== "chat"} onNewChat={() => { setMobileNavigation(false); setClearOpen(true); }} onOpenChat={openCurrentChat} /></PreviewDialog>}
      {sources && <SourcePanel key={sources.map(s => s.sourceId).join(",")} sources={sources} onError={authError} onClose={() => setSources(null)} />}
      {clarification && <ClarificationDialog key={clarification.id} original={clarification.original} answer={clarification.answer} curricula={curricula} status={curriculaStatus} open={clarification.open && !busy}
        onClose={() => setClarification(previous => previous ? { ...previous, open: false } : null)} onRetry={() => setCurriculaAttempt(n => n + 1)}
        onConfirm={(reply, drafts) => {
          if (flight.current || signInNeeded || clarification.id !== state.messages.at(-1)?.id) return;
          const needsScope = clarification.answer.missingFields.some(field => field === "program" || field === "curriculum");
          const selected = needsScope ? reply.scope : reply.scope ?? clarification.scope;
          changeScope(curricula.find(c => c.curriculumId === selected?.curriculumId && c.programId === selected?.programId) ?? null);
          dispatch({ type: "remember", details: confirmedDetails(clarification.answer, curricula, drafts, selected) });
          void send({ text: reply.text, scope: selected });
        }} />}
      {scopeOpen && <ScopePanel curricula={curricula} current={scope} status={curriculaStatus} onRetry={() => setCurriculaAttempt(n => n + 1)} busy={!!busy} onClose={() => setScopeOpen(false)} onSave={value => { changeScope(value); setScopeOpen(false); }} />}
      {rephraseOpen && <RephraseDialog onClose={() => setRephraseOpen(false)} onUse={text => { draft(text); setRephraseOpen(false); }} />}
      {detailsOpen && <SuppliedDetailsPanel details={details} selected={selectedDetails} scopeLabel={scope ? `${scope.programName} · ${scope.curriculumName}` : "No curriculum selected"} onClose={() => setDetailsOpen(false)} onUse={keys => { setSelectedDetails(keys); setDetailsOpen(false); }} />}
      {review && <PreviewDialog title="Review your next message" onClose={() => setReview(null)}>
        <p className="supporting-copy">{scope ? `${scope.programName} · ${scope.curriculumName}` : "No curriculum selected"}</p>
        <p className="clarification-review">{review.text}</p><p className="supporting-copy">Only this question and the details shown here will be sent. Earlier messages are not automatically attached.</p>
        <div className="card-actions"><Button disabled={!!busy || signInNeeded} onClick={() => { if (review.scope === scope || sameScope(review.scope, scope)) void send({ ...review, clearDraft: true }); }}>Confirm and send</Button><Button variant="outline" onClick={() => setReview(null)}>Edit more</Button></div>
      </PreviewDialog>}
      {filesOpen && <FilePanel files={files} busy={busy === "file"} warning={fileWarning} onClose={() => setFilesOpen(false)} onPick={() => picker.current?.click()}
        onConfirm={fileAction} onRemove={id => fileAction(id)} onType={() => { setFilesOpen(false); main.current?.querySelector("textarea")?.focus(); }} />}
      {clearOpen && <PreviewDialog title="Clear this chat?" busy={busy === "clear"} onClose={() => setClearOpen(false)}>
        <p>This removes the server’s temporary context and clears the conversation after confirmation.</p>
        {busy === "clear" ? <p role="status">Waiting for confirmation…</p> : <div className="card-actions"><Button onClick={clear}>Clear chat</Button><Button variant="outline" onClick={() => setClearOpen(false)}>Cancel</Button></div>}
      </PreviewDialog>}
    </main>
  </div>;
}
