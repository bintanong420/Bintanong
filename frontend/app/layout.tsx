import type { Metadata } from "next";
import { Geist, Inter } from "next/font/google";
import { appearanceBootstrap } from "@/lib/appearance";
import { PrivacyNotice } from "@/components/privacy-notice";
import "./styles.css";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Bintanong | Academic guide",
  description: "Research academic guide for PalSU undergraduate curricula and policies.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geist.variable} ${inter.variable}`}>
        <script dangerouslySetInnerHTML={{ __html: appearanceBootstrap }} />
        {children}<PrivacyNotice />
      </body>
    </html>
  );
}
