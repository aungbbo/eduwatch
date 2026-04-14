import "./globals.css";
import type { Metadata } from "next";
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
        {children}
      </body>
    </html>
  );
}
