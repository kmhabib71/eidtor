import { useState } from "react";
import { NextPage } from "next";
import Link from "next/link";
import Layout from "@/components/layout/Layout";

// FAQ interface
interface FAQ {
  question: string;
  answer: string;
  category: string;
}

const HelpPage: NextPage = () => {
  // List of FAQs
  const faqs: FAQ[] = [
    {
      question: "What is Silence Cutter?",
      answer:
        "Silence Cutter is a SaaS tool that automatically detects and removes silent parts from your videos, making them more engaging and concise. Upload your videos, and our AI will analyze them to identify and remove silence based on customizable thresholds.",
      category: "general",
    },
    {
      question: "How does silence detection work?",
      answer:
        "Our AI technology analyzes the audio track of your video and identifies segments where the audio level falls below a certain threshold for a specified duration. These silent segments are then automatically removed, and the remaining parts are stitched together seamlessly.",
      category: "technical",
    },
    {
      question: "What video formats are supported?",
      answer:
        "Silence Cutter supports most popular video formats including MP4, MOV, AVI, and WebM. The maximum file size is 500MB for all plans, but resolution limits vary based on your subscription tier.",
      category: "technical",
    },
    {
      question: "Can I customize the silence detection settings?",
      answer:
        "Yes, with our Pro and Enterprise plans, you can customize the silence threshold (how quiet is considered 'silence') and the minimum silence duration (how long a quiet period needs to be to count as silence).",
      category: "features",
    },
    {
      question: "How long does processing take?",
      answer:
        "Processing time depends on the length and size of your video, as well as your subscription tier. Most videos are processed within a few minutes, but longer videos may take more time. You'll receive a notification when processing is complete.",
      category: "technical",
    },
    {
      question: "What are processing minutes?",
      answer:
        "Processing minutes refer to the total duration of videos you can upload and process each month. For example, with the Free plan's 10 processing minutes, you can upload videos totaling 10 minutes in length. This limit resets at the beginning of each billing cycle.",
      category: "billing",
    },
    {
      question: "How do I cancel my subscription?",
      answer:
        "You can cancel your subscription at any time from your Subscription page. After cancellation, your account will remain active until the end of your current billing period, after which it will revert to the Free plan.",
      category: "billing",
    },
    {
      question: "Is my payment information secure?",
      answer:
        "Yes, we use Stripe for payment processing, which is PCI-compliant and uses industry-standard encryption to protect your payment information. We do not store your full credit card details on our servers.",
      category: "security",
    },
    {
      question: "What happens to my videos after processing?",
      answer:
        "Your original uploaded videos and the processed versions (with silence removed) are stored securely in our cloud storage. You can download or delete them at any time from your account. We maintain strict privacy and security practices.",
      category: "security",
    },
    {
      question: "Can I use Silence Cutter for commercial projects?",
      answer:
        "Yes, you can use Silence Cutter for both personal and commercial projects. Our Pro and Enterprise plans are designed for professional content creators and businesses that need higher processing limits and advanced features.",
      category: "general",
    },
  ];

  // State for active category filter
  const [activeCategory, setActiveCategory] = useState<string>("all");

  // Get unique categories
  const categories = ["all", ...new Set(faqs.map((faq) => faq.category))];

  // Filter FAQs by category
  const filteredFaqs =
    activeCategory === "all"
      ? faqs
      : faqs.filter((faq) => faq.category === activeCategory);

  return (
    <Layout title="Help & Support - Silence Cutter">
      <div className="bg-gray-50 min-h-screen py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Help & Support
          </h1>

          {/* Support Options */}
          <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
            <h2 className="text-xl font-semibold mb-4">Support Options</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <div className="text-primary-600 mb-3">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-8 w-8"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium mb-2">Email Support</h3>
                <p className="text-gray-600 mb-4">
                  Get help from our support team via email. We typically respond
                  within 24 hours.
                </p>
                <a
                  href="mailto:support@silencecutter.com"
                  className="text-primary-600 hover:text-primary-800 font-medium"
                >
                  support@silencecutter.com
                </a>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <div className="text-primary-600 mb-3">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-8 w-8"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium mb-2">Live Chat</h3>
                <p className="text-gray-600 mb-4">
                  Chat with our support team during business hours for immediate
                  assistance.
                </p>
                <button
                  onClick={() => alert("Live chat would open here")}
                  className="text-primary-600 hover:text-primary-800 font-medium"
                >
                  Start Chat
                </button>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <div className="text-primary-600 mb-3">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-8 w-8"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium mb-2">Documentation</h3>
                <p className="text-gray-600 mb-4">
                  Browse our comprehensive documentation for detailed guides and
                  tutorials.
                </p>
                <Link
                  href="/docs"
                  className="text-primary-600 hover:text-primary-800 font-medium"
                >
                  View Documentation
                </Link>
              </div>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-semibold mb-6">
              Frequently Asked Questions
            </h2>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2 mb-8">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-medium ${
                    activeCategory === category
                      ? "bg-primary-100 text-primary-800"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>

            {/* FAQ List */}
            <div className="space-y-6">
              {filteredFaqs.map((faq, index) => (
                <div
                  key={index}
                  className="border-b border-gray-200 pb-6 last:border-b-0 last:pb-0"
                >
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {faq.question}
                  </h3>
                  <p className="text-gray-600">{faq.answer}</p>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {faq.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Contact CTA */}
            <div className="mt-10 border-t border-gray-200 pt-8 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Still have questions?
              </h3>
              <p className="text-gray-600 mb-4">
                If you can't find the answer you're looking for, please contact
                our support team.
              </p>
              <a
                href="mailto:support@silencecutter.com"
                className="btn btn-primary inline-block"
              >
                Contact Support
              </a>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default HelpPage;
