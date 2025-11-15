import type { Metadata } from "next";

import "./globals.css";
import Header from "../components/Header";
import Footer from "../components/Footer";
import ChatbotWrapper from "../components/ChatbotWrapper";

export const metadata: Metadata = {
  title: "Career Harmony - Job Portal",
  description: "Find your dream job that honors your whole self",
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Header />
        <main>{children}</main>
        <Footer />
        <ChatbotWrapper />
      </body>
    </html>
  );
}
