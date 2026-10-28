export type Appearance = "light" | "dark" | "system";

export function appearanceValue(value: unknown): Appearance {
  return value === "light" || value === "dark" ? value : "system";
}

export const appearanceKey = "bintanong-appearance";

// Apply the saved visual preference before paint; no chat or file state is persisted.
export const appearanceBootstrap = `try{document.documentElement.dataset.appearance=(${appearanceValue.toString()})(localStorage.getItem(${JSON.stringify(appearanceKey)}))}catch{document.documentElement.dataset.appearance="system"}`;
