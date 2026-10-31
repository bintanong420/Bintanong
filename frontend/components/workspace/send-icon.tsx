export function SendIcon({ size = 26 }: { size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 100 100" fill="none" aria-hidden="true">
    <polygon points="6,6 96,48 30,48" fill="currentColor" />
    <polygon points="6,94 30,52 96,52" fill="currentColor" />
  </svg>;
}
