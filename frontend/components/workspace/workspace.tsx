"use client";

import { useCallback, useEffect, useId, useReducer, useRef, useState } from "react";
import { createBrowserClient } from "@supabase/ssr";
import { ChevronDown, ClipboardList, Ellipsis, FolderOpen, GraduationCap, Info, Lock, LogIn, LogOut, Menu } from "lucide-react";
import { clearStudentSession, confirmStudentFile, getStudentCurricula, removeStudentFile, sendStudentMessage, uploadStudentFile } from "@/lib/student-transport";
import { StudentTransportError, type StudentAnswer, type StudentChoice, type StudentCurriculum, type StudentScope, type StudentSourceSummary } from "@/lib/student-contracts";
import { busyRetryDelay, createWorkspace, selectedPDF, workspaceReducer } from "@/lib/student-workspace";
import { Button } from "@/components/ui/button";
import { Sidebar, SidebarBrand } from "./sidebar";
import { Conversation, EmptyConversation } from "./conversation";
import { ProgramPicker, type CurriculumState } from "./program-picker";
import { programShortName } from "@/lib/programs";
import { Composer } from "./composer";
import { BrandMark } from "./brand-mark";
import { AppearanceControl } from "./appearance-control";
import { PreviewDialog } from "./preview-dialog";
import { FilePanel, type ChatFile } from "./file-panel";
import { SourcePanel } from "./source-panel";
import { ClarificationDialog } from "./clarification-dialog";
import { clarificationQuestions, confirmedDetails, followUpMessage, sameScope, typedReply } from "@/lib/student-clarification";
import { RephraseDialog, SuppliedDetailsPanel } from "./follow-up-dialog";

/** m:ss, for the question-limit wait. */
const clockText = (ms: number) => { const seconds = Math.max(0, Math.ceil(ms / 1000)); return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`; };
const stages: Record<string, string> = { waiting: "Waiting for a free answer slot… You can stop waiting.", understanding: "Checking the information for your question…", writing: "Preparing the response…" };
function errorText(error: unknown) {
  if (error instanceof StudentTransportError) {
    if (error.code === "sign_in_required" || error.code === "psu_account_required") return "Your sign-in needs attention. Sign in again to continue; your conversation is still visible here.";
    if (error.code === "answers_busy") return "All answer slots are busy. Your question is still here; try again later.";
    if (error.code === "account_busy" || error.code === "chat_in_progress") return "Another question from this account or browser session is still running. Wait for it to finish or stop it in that tab.";
    if (error.code === "already_answered") return "That question already finished on the server. Edit or resend it explicitly if you need a new check.";
  }
  return "The request did not finish. Your conversation is still here. The server may have completed it; resending starts a new check.";
}

export function Workspace({ signedIn = false }: { signedIn?: boolean }) {
  const [state, dispatch] = useReducer(workspaceReducer, undefined, createWorkspace);
  const [curricula, setCurricula] = useState<StudentCurriculum[]>([]), [scope, setScope] = useState<StudentCurriculum | null>(null);
  const [curriculaStatus, setCurriculaStatus] = useState<CurriculumState>("loading"), [curriculaAttempt, setCurriculaAttempt] = useState(0);
  const [pickerKey, setPickerKey] = useState(0);
  const [scopeOpen, setScopeOpen] = useState(true), [filesOpen, setFilesOpen] = useState(false), [clearOpen, setClearOpen] = useState(false);
  const [files, setFiles] = useState<ChatFile[]>([]), [fileWarning, setFileWarning] = useState<string | null>(null);
  const [sources, setSources] = useState<StudentSourceSummary[] | null>(null), [progress, setProgress] = useState("Connecting…");
  const [detailsOpen, setDetailsOpen] = useState(false), [rephraseOpen, setRephraseOpen] = useState(false), [selectedDetails, setSelectedDetails] = useState<string[]>([]);
  // A question refused before it started: all answer slots busy, or this person's question limit (`limited`).
  // `retryAt` (epoch ms) is when it is sent again, null once automatic busy retries stop.
  const [retry, setRetry] = useState<{ text: string; scope: StudentScope | null; attempt: number; retryAt: number | null; limited: boolean } | null>(null);
  const [now, setNow] = useState(() => Date.now());
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
  useEffect(() => {
    const channel = new BroadcastChannel("bintanong-access");
    let identity: string | null = null, initialized = !signedIn;
    const reset = () => { flight.current?.controller.abort(); window.location.reload(); };
    channel.onmessage = event => {
      const next = event.data?.identity;
      if (initialized && (typeof next === "string" || next === null) && next !== identity) reset();
    };
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL, key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
    if (!url || !key) { channel.postMessage({ identity: null }); return () => channel.close(); }
    const client = createBrowserClient(url, key);
    const { data } = client.auth.onAuthStateChange((event, session) => {
      const next = session?.user.id ?? null;
      if (event === "INITIAL_SESSION") {
        identity = next; initialized = true; channel.postMessage({ identity });
      } else if (initialized && (event === "SIGNED_IN" || event === "SIGNED_OUT") && next !== identity) {
        identity = next; channel.postMessage({ identity }); reset();
      }
    });
    return () => { data.subscription.unsubscribe(); channel.close(); };
  }, [signedIn]);
  // Each open starts the picker afresh and re-attaches its dialog if it was removed from the page.
  function openPicker() { setPickerKey(n => n + 1); setScopeOpen(true); }
  function draft(text: string) { dispatch({ type: "draft", text }); requestAnimationFrame(() => main.current?.querySelector("textarea")?.focus()); }
  function toggleNavigation(collapsed: boolean) {
    setNavigationCollapsed(collapsed);
    requestAnimationFrame(() => document.querySelector<HTMLElement>(collapsed ? ".desktop-navigation-toggle" : ".sidebar-collapse")?.focus());
  }
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
    if (flight.current || signInNeeded || !scope || !state.draft.trim()) return;
    try {
      const text = followUpMessage(state.draft, scope, details, selectedDetails);
      const last = state.messages.findLast(m => m.role === "user")?.text ?? "";
      const typed = typedReply(clarification?.original ?? last, clarification?.answer ?? null, state.draft, curricula);
      if (selectedDetails.length) setReview({ text, scope });
      else if (typed && typed.text !== state.draft.trim()) {
        if (typed.scope) changeScope(curricula.find(c => sameScope(c, typed.scope)) ?? null);
        void send({ text: typed.text, scope: typed.scope ?? scope, clearDraft: true });
      } else void send();
    } catch { dispatch({ type: "warning", warning: "This message could not be prepared. Shorten the question or review the selected course details." }); }
  }
  async function send(confirmed?: { text: string; scope: StudentScope | null; clearDraft?: boolean; attempt?: number }) {
    const text = (confirmed?.text ?? state.draft).trim(), selectedScope = confirmed ? confirmed.scope : scope;
    // Owner decision, 3 Nov 2026: chat is locked until a program is chosen, whatever the DOM says.
    if (flight.current || !text || signInNeeded || !selectedScope) return;
    const value = begin("chat");
    setClarification(null); setSelectedDetails([]); setReview(null); setRetry(null);
    dispatch({ type: "submit", id: value.id, ...(confirmed ? { text, clearDraft: confirmed.clearDraft } : {}) }); setProgress("Connecting…");
    try {
      const answer = await sendStudentMessage({ id: value.id, text, programId: selectedScope.programId, curriculumId: selectedScope.curriculumId }, {
        signal: value.controller.signal,
        onText: text => { if (!value.controller.signal.aborted) dispatch({ type: "delta", id: value.id, text }); },
        onProgress: stage => { if (!value.controller.signal.aborted) setProgress(stages[stage]); },
      });
      if (!value.controller.signal.aborted) {
        dispatch({ type: "complete", id: value.id, answer });
        if (clarificationQuestions(answer, curricula).length) setClarification({ id: value.id + "-answer", original: text, answer, scope: selectedScope, open: false });
      }
    } catch (error) {
      if (value.controller.signal.aborted) return;
      authError(error);
      if (error instanceof StudentTransportError && (error.code === "answers_busy" || error.code === "rate_limited")) {
        // Refused before it started: show it as waiting, not as an interrupted answer, and send it again later.
        const attempt = confirmed?.attempt ?? 1, limited = error.code === "rate_limited";
        dispatch({ type: "withdraw", id: value.id });
        const delay = limited ? error.retryAfter ?? 60 : busyRetryDelay(attempt);
        setRetry({ text, scope: selectedScope, attempt, limited, retryAt: delay === null ? null : Date.now() + delay * 1000 });
        setNow(Date.now());
      } else dispatch({ type: "interrupt", id: value.id, warning: errorText(error) });
    }
    finally { finish(value); }
  }
  // The retry timer calls the latest send with the latest retry state.
  const sendRef = useRef(send), retryRef = useRef(retry); sendRef.current = send; retryRef.current = retry;
  // A limit wait is not a busy attempt, so it does not use up the automatic busy retries.
  const resend = (current: NonNullable<typeof retry>) => sendRef.current({ text: current.text, scope: current.scope,
    attempt: current.limited ? current.attempt : current.attempt + 1, clearDraft: false });
  function retryNow() { if (retry) void resend(retry); }
  function cancelRetry() { if (retry) { dispatch({ type: "draft", text: retry.text }); setRetry(null); } }
  useEffect(() => {
    if (!retry || retry.retryAt === null) return;
    const scheduled = retry;
    const send = setTimeout(function fire() {
      // Another request (for example a file) holds the connection: check again shortly.
      if (flight.current) { setTimeout(fire, 1000); return; }
      if (retryRef.current === scheduled) void resend(scheduled);
    }, Math.max(0, retry.retryAt - Date.now()));
    const tick = setInterval(() => setNow(Date.now()), 1000);  // only refreshes the countdown text
    return () => { clearTimeout(send); clearInterval(tick); };
  }, [retry]);
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
        dispatch({ type: "clear" }); setClarification(null); setFiles([]); setSources(null); setFileWarning(null); setClearOpen(false); setFilesOpen(false); setRetry(null);
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
    if (!scope) { setFileWarning("Choose your program and curriculum before adding a PDF."); openPicker(); return; }
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
      const channel = new BroadcastChannel("bintanong-access");
      channel.postMessage({ identity: null }); channel.close();
      dispatch({ type: "clear" }); setClarification(null); setFiles([]); setSelectedDetails([]); setReview(null); setDetailsOpen(false); setRetry(null);
      window.location.assign(response.headers.get("x-bintanong-signout-notice") === "cleanup_pending" ? "/login?notice=cleanup_pending" : "/login?notice=signed_out");
    } catch { setSignOutFailed(true); }
    finally { finish(value); }
  }
  return <div className={`workspace live-workspace${navigationCollapsed ? " navigation-collapsed" : ""}`}>
    <a className="skip-link" href="#question">Skip to question</a>
    <Sidebar currentChat={state.messages.find(message => message.role === "user")} className="desktop-sidebar" hidden={navigationCollapsed} busy={!!busy && busy !== "chat"} onCollapse={() => toggleNavigation(true)} onNewChat={() => setClearOpen(true)} onOpenChat={openCurrentChat} />
    <main className={`workspace-main${state.messages.length ? "" : " welcome-surface"}`} id="question" tabIndex={-1} ref={main}>
      <header className="workspace-toolbar">
        {!!state.messages.length && <h1 className="sr-only">Your conversation with Bintanong</h1>}
        <div className="workspace-heading">
          {navigationCollapsed && <Button variant="ghost" size="icon" className="desktop-navigation-toggle" aria-label="Open navigation" aria-expanded="false" onClick={() => toggleNavigation(false)}><Menu aria-hidden="true" /></Button>}
          <Button variant="ghost" size="icon" className="mobile-navigation-toggle" aria-label="Open navigation" aria-expanded={mobileNavigation} onClick={() => setMobileNavigation(true)}><Menu aria-hidden="true" /></Button>
          <span className="workspace-name"><BrandMark />Bintanong</span>
          {!!state.messages.length && <Button asChild variant="ghost" size="icon" className="header-about">
            {/* A new tab keeps this temporary chat, which lives only in this page. */}
            <a href="/about" target="_blank" rel="noopener" aria-label="About Bintanong (opens in a new tab)" title="About Bintanong"><Info aria-hidden="true" /></a>
          </Button>}
        </div>
        <div className="workspace-account-actions">
          {details.length > 0 && <Button type="button" variant="ghost" size="sm" className="header-details" aria-label={`You supplied (${details.length})`} title={`You supplied (${details.length})`} disabled={!!busy || signInNeeded} onClick={() => setDetailsOpen(true)}><ClipboardList size={16} aria-hidden="true" /><span className="account-action-label">You supplied ({details.length})</span></Button>}
          <AppearanceControl className="header-theme-toggle" />
          <Button variant="ghost" size="icon" aria-label="Chat options" title="Chat options" popoverTarget={optionsId}><Ellipsis aria-hidden="true" /></Button>
          {signedIn ? <Button variant="ghost" className="header-signout" aria-label={busy === "signout" ? "Signing out…" : "Sign out"} title={busy === "signout" ? "Signing out…" : "Sign out"} disabled={busy === "file" || busy === "clear" || busy === "signout"} onClick={() => void signOut()}><LogOut size={16} aria-hidden="true" /><span className="account-action-label">{busy === "signout" ? "Signing out…" : "Sign out"}</span></Button>
            : <Button asChild variant="ghost"><a href="/login" aria-label="Sign in" title="Sign in"><LogIn size={16} aria-hidden="true" /><span className="account-action-label">Sign in</span></a></Button>}</div>
        <div id={optionsId} popover="auto" className="workspace-options"><p className="supporting-copy">Research preview. University validation is still pending.</p></div>
      </header>
      {!signedIn && <p className="session-notice"><span>Guest</span> · Temporary chat</p>}
      <div className={`workspace-content${state.messages.length ? "" : " welcome-mode"}`}>
      {state.messages.length ? <Conversation state={state} progress={progress} onSource={setSources} canClarify={!!clarification && !signInNeeded} onEdit={draft} onRephrase={() => setRephraseOpen(true)} onClarify={() => { if (!flight.current) setClarification(previous => previous ? { ...previous, open: true } : null); }} /> : <EmptyConversation scope={scope} onSuggest={text => { draft(text); if (!scope) openPicker(); }} />}
      {signOutFailed && <div className="outcome-notice status-danger" role="alert"><p>We couldn't finish signing you out. Try again before leaving this device.</p><Button variant="outline" disabled={!!busy} onClick={() => void signOut()}>Try signing out again</Button></div>}
      {retry && <div className="outcome-notice busy-retry" role="status">
        <p className="busy-question">{retry.text}</p>
        {retry.limited && retry.retryAt !== null
          ? <p><span aria-hidden="true">You&apos;ve asked several questions in a short time. You can ask again in {clockText(retry.retryAt - now)}. </span>
              <span className="sr-only">You&apos;ve asked several questions in a short time. Bintanong will send this question when you can ask again. </span>
              <span className="busy-attempt">It will be sent automatically.</span></p>
          : retry.retryAt === null
          ? <p>Still busy. Try again in a moment. <span className="busy-attempt">(attempt {retry.attempt})</span></p>
          : <p><span aria-hidden="true">All answer slots are busy. Retrying in {Math.max(0, Math.ceil((retry.retryAt - now) / 1000))} s </span>
              <span className="sr-only">All answer slots are busy. Bintanong will try again automatically. </span>
              <span className="busy-attempt">(attempt {retry.attempt})</span></p>}
        <div className="card-actions">
          {!retry.limited && <Button type="button" size="sm" disabled={!!busy} onClick={retryNow}>{retry.retryAt === null ? "Try again" : "Try again now"}</Button>}
          <Button type="button" size="sm" variant="outline" onClick={cancelRetry}>Cancel</Button>
        </div>
      </div>}
      {state.warning && <div className="outcome-notice status-danger" role="alert"><p>{state.warning}</p>{signInNeeded && <a href="/login">Sign in again</a>}{state.messages.some(message => message.role === "user") && <Button variant="outline" size="sm" onClick={() => draft(state.messages.findLast(message => message.role === "user")?.text ?? "")}>Edit question</Button>}</div>}
      {signInNeeded && !state.warning && <p className="session-notice" role="alert">Your sign-in needs attention. <a href="/login">Sign in again</a> to continue.</p>}
      <Composer live picker={picker} locked={!scope && <>
          <Lock size={16} aria-hidden="true" />
          <span>{curriculaStatus === "failed" ? "We couldn't load the program list, so chat is locked." : "Choose your program to unlock the chat."}</span>
          {curriculaStatus === "failed" && <Button type="button" size="sm" variant="outline" onClick={() => { setCurriculaAttempt(n => n + 1); openPicker(); }}>Try again</Button>}
        </>} draft={state.draft} attachments={[]} warning={fileWarning} pending={!!busy || signInNeeded}
        onDraft={text => dispatch({ type: "draft", text })} onSend={prepareSend} onStop={busy === "chat" ? stop : undefined} onSelect={selectFiles} onRemove={() => {}}
        contextNote={selectedDetails.length ? `${selectedDetails.length} earlier details selected. Review before sending.` : undefined}
        tools={<><Button type="button" variant={scope ? "outline" : "default"} size="sm" className="program-chip" disabled={busy === "file" || busy === "clear" || busy === "signout"} aria-label={scope ? `Program: ${scope.programName}, ${scope.curriculumName} curriculum. Change program` : "Choose your program"} title={scope ? `${scope.programName} · ${scope.curriculumName}` : "Choose your program"} onClick={() => openPicker()}>
            <GraduationCap size={16} aria-hidden="true" />{scope ? <><span className="program-chip-label">{programShortName(scope.programId, scope.programName)}</span><span className="program-chip-year">{scope.curriculumName}</span></> : <span>Choose program</span>}<ChevronDown size={14} aria-hidden="true" />
          </Button>
          <Button type="button" variant="ghost" size="sm" disabled={!!busy || !scope} aria-label="Files in this chat" onClick={() => setFilesOpen(true)}><FolderOpen size={16} aria-hidden="true" />Files{files.length ? ` (${files.length})` : ""}</Button>
          {details.length > 0 && <Button type="button" variant="ghost" size="sm" disabled={!!busy || signInNeeded} onClick={() => setDetailsOpen(true)}>Include earlier details{selectedDetails.length ? ` (${selectedDetails.length})` : ""}</Button>}</>}
      />
      </div>
      {mobileNavigation && <PreviewDialog title="Navigation" heading={<SidebarBrand />} side className="navigation-dialog" onClose={() => setMobileNavigation(false)}><Sidebar showBrand={false} currentChat={state.messages.find(message => message.role === "user")} busy={!!busy && busy !== "chat"} onNewChat={() => { setMobileNavigation(false); setClearOpen(true); }} onOpenChat={openCurrentChat} /></PreviewDialog>}
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
      <ProgramPicker open={scopeOpen} openCount={pickerKey} curricula={curricula} current={scope} status={curriculaStatus} onRetry={() => setCurriculaAttempt(n => n + 1)} busy={busy === "file" || busy === "clear" || busy === "signout"} onClose={() => setScopeOpen(false)} onSave={value => { changeScope(value); setScopeOpen(false); }} />
      {rephraseOpen && <RephraseDialog onClose={() => setRephraseOpen(false)} onUse={text => { draft(text); setRephraseOpen(false); }} />}
      {detailsOpen && <SuppliedDetailsPanel details={details} selected={selectedDetails} scopeLabel={scope ? `${scope.programName} · ${scope.curriculumName}` : "No curriculum selected"} onClose={() => setDetailsOpen(false)} onUse={keys => { setSelectedDetails(keys); setDetailsOpen(false); }} />}
      {review && <PreviewDialog title="Review your next message" onClose={() => setReview(null)}>
        <p className="supporting-copy">{scope ? `${scope.programName} · ${scope.curriculumName}` : "No curriculum selected"}</p>
        <p className="clarification-review">{review.text}</p><p className="supporting-copy">Only this question and the details shown here will be sent. Course results you stated earlier in this chat are remembered for this curriculum until you start a new chat.</p>
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
