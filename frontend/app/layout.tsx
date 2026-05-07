import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import React from "react";

export const metadata: Metadata = {
  title: "EduWatch | Smart Student Savings",
  description: "Track essential study items and buy at the best price."
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="site-bg-glow" aria-hidden="true" />
        <nav className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
            <Link href="/" className="text-base font-bold text-indigo-700 hover:text-indigo-800">
              EduWatch
            </Link>
            <Link
              href="/watchlist"
              className="rounded-xl border border-slate-200 px-4 py-1.5 text-sm font-medium text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700"
            >
              My Watchlist
            </Link>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
