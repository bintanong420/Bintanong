import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Bintanong compatibility status",
  description: "Phase 0 service compatibility surface",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
