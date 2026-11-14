import type { Metadata } from "next";

export const metadata: Metadata = { title: "Bintanong compatibility status", description: "Phase 0 service compatibility surface" };

export default function HealthLayout({ children }: { children: React.ReactNode }) {
  return children;
}
