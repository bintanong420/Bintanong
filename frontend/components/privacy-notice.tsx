"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

// Owner, 4 Nov 2026: a privacy notice the first time the site is opened in a browser session.
const SEEN = "bintanong-privacy-notice-seen";

export const privacyNotice = {
  title: "Your privacy",
  body: "Bintanong follows the Data Privacy Act of 2012 (Republic Act No. 10173). What you type or upload is used only to answer your questions during this session. It is kept temporarily and is not stored permanently.",
  researchBody: "Research mode saves questions, model outputs and evaluator judgments to a local evaluation log. Use benchmark or synthetic questions. Do not enter personal records or private documents.",
  accept: "I understand",
};

function seen(key: string) {
  try { return window.sessionStorage.getItem(key) === "1"; } catch { return false; }
}

export function PrivacyNotice() {
  const dialog = useRef<HTMLDialogElement>(null);
  const research = usePathname()?.startsWith("/dev/evaluation");
  const key = research ? SEEN + "-evaluation" : SEEN;

  useEffect(() => {
    if (!seen(key) && dialog.current && !dialog.current.open) dialog.current.showModal();
  }, [key]);

  function accept() {
    try { window.sessionStorage.setItem(key, "1"); } catch { /* the notice simply shows again next time */ }
    dialog.current?.close();
  }

  return (
    <dialog ref={dialog} aria-labelledby="privacy-notice-title" onCancel={accept}
      className="m-auto w-[min(28rem,calc(100vw-2rem))] rounded-2xl border border-black/10 bg-background p-6 text-foreground shadow-2xl backdrop:bg-black/50">
      <h2 id="privacy-notice-title" className="text-lg font-semibold">{privacyNotice.title}</h2>
      <p className="mt-3 text-sm leading-6">{research ? privacyNotice.researchBody : privacyNotice.body}</p>
      <div className="mt-5 flex justify-end">
        <Button type="button" onClick={accept} autoFocus>{privacyNotice.accept}</Button>
      </div>
    </dialog>
  );
}
