import { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    template: "%s | Silence Cutter",
    default: "Silence Cutter - Automatically Remove Silence from Videos",
  },
  description:
    "Automatically detect and remove silent parts from your videos, making them more engaging and concise.",
  keywords: [
    "silence removal",
    "video editing",
    "silence cutter",
    "video processor",
    "saas",
  ],
  authors: [{ name: "Silence Cutter Team" }],
  creator: "Silence Cutter",
  publisher: "Silence Cutter",
  formatDetection: {
    email: true,
    address: true,
    telephone: true,
  },
  openGraph: {
    title: "Silence Cutter - Automatically Remove Silence from Videos",
    description:
      "Automatically detect and remove silent parts from your videos, making them more engaging and concise.",
    url: "https://silence-cutter.com",
    siteName: "Silence Cutter",
    images: [
      {
        url: "https://silence-cutter.com/images/og-image.jpg",
        width: 1200,
        height: 630,
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Silence Cutter - Automatically Remove Silence from Videos",
    description:
      "Automatically detect and remove silent parts from your videos, making them more engaging and concise.",
    images: ["https://silence-cutter.com/images/twitter-image.jpg"],
  },
};
