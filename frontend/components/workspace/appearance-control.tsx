import { useEffect, useState } from "react";
import { Monitor, Moon, Sun } from "lucide-react";
import { appearanceKey, appearanceValue, type Appearance } from "@/lib/appearance";

export function AppearanceControl() {
  const [appearance, setAppearance] = useState<Appearance>("system");

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

  const Icon = appearance === "light" ? Sun : appearance === "dark" ? Moon : Monitor;
  return <label className="appearance-control" title="Appearance">
    <Icon size={16} aria-hidden="true" />
    <span className="sr-only">Appearance</span>
    <select value={appearance} onChange={event => {
      const value = appearanceValue(event.target.value);
      document.documentElement.dataset.appearance = value;
      setAppearance(value);
      try { localStorage.setItem(appearanceKey, value); } catch { /* Appearance still works when browser storage is blocked. */ }
    }}>
      <option value="system">System</option>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  </label>;
}
