import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "legal-eval-ui",
  description: "Static reader for legal-eval harness results",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-white text-neutral-900 antialiased">
        {children}
      </body>
    </html>
  );
}
