import type { Metadata } from "next";
import { DM_Sans, Instrument_Serif } from "next/font/google";

import { AuthProvider } from "@/components/AuthProvider";

import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
});

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-instrument-serif",
});

export const metadata: Metadata = {
  title: "Legal Eval — prove your legal AI extraction pipeline",
  description:
    "Reproducible, auditable evaluation for legal document extraction teams. BYOK, custom datasets, multi-provider comparison, judge-validated metrics, and shareable trust reports for enterprise buyers.",
};

export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`h-full ${dmSans.variable} ${instrumentSerif.variable}`}>
      <body className="min-h-full antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
