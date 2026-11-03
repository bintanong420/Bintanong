export type Appearance = "light" | "dark" | "system";

// Light is the default; "system" stays available as an explicit choice.
export function appearanceValue(value: unknown): Appearance {
  return value === "dark" || value === "system" ? value : "light";
}

export const appearanceKey = "bintanong-appearance";

// Apply the saved visual preference before paint; no chat or file state is persisted.
export const appearanceBootstrap = `try{document.documentElement.dataset.appearance=(${appearanceValue.toString()})(localStorage.getItem(${JSON.stringify(appearanceKey)}))}catch{document.documentElement.dataset.appearance="light"}`;
