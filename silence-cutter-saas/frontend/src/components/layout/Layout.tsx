import React, { ReactNode } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Footer from "./Footer";
import { useAuth } from "@/contexts/AuthContext";

interface LayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  hideNavbar?: boolean;
  hideFooter?: boolean;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  title = "Silence Cutter - Automatically remove silence from your videos",
  description = "Upload your videos and automatically remove silent parts to create more engaging content.",
  hideNavbar = false,
  hideFooter = false,
}) => {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="flex flex-col min-h-screen">
        {!hideNavbar && <Navbar />}

        <main className="flex-grow">{children}</main>

        {!hideFooter && <Footer />}
      </div>
    </>
  );
};

export default Layout;
