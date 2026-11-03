"use client";

import { useEffect, useState } from "react";
import { Lightbulb, LightbulbOff } from "lucide-react";
import { appearanceKey, appearanceValue, nextAppearance, type Appearance } from "@/lib/appearance";

/** A light bulb button that switches between light (the default) and dark. */
export function AppearanceControl({ className = "" }: { className?: string }) {
  const [appearance, setAppearance] = useState<Appearance>("light");

  useEffect(() => {
    setAppearance(appearanceValue(document.documentElement.dataset.appearance));
    function sync(event: StorageEvent) {
      if (event.key !== appearanceKey && event.key !== null) return;
      const value = appearanceValue(event.newValue);
      document.documentElement.dataset.appearance = value;
      setAppearance(value);
    }
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);

  const dark = appearance === "dark" || (appearance === "system" && typeof window !== "undefined" && matchMedia("(prefers-color-scheme: dark)").matches);
  const label = dark ? "Switch to light mode" : "Switch to dark mode";
  return <button type="button" className={`theme-toggle ${className}`} aria-label={label} title={label} onClick={() => {
    const value = nextAppearance(appearance, matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.appearance = value;
    setAppearance(value);
    try { localStorage.setItem(appearanceKey, value); } catch { /* The theme still switches when browser storage is blocked. */ }
  }}>
    {dark ? <LightbulbOff size={18} aria-hidden="true" /> : <Lightbulb size={18} aria-hidden="true" />}
  </button>;
}
