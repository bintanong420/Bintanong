import type { Metadata } from "next";
import { Geist, Inter } from "next/font/google";
import "./styles.css";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Bintanong | Academic guide preview",
  description: "Interface preview for PalSU undergraduate academic guidance. Fictional examples only.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${geist.variable} ${inter.variable}`}>{children}</body>
    </html>
  );
}
