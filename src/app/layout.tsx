import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "INDY MONEY – Mutual Fund FAQ Assistant",
  description:
    "Get verified factual information about selected mutual fund schemes from official sources. Facts only, no investment advice.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">{children}</body>
    </html>
  );
}
