import { useEffect } from "react";
import { NextPage } from "next";
import Link from "next/link";
import { useRouter } from "next/router";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/contexts/AuthContext";

const CheckoutSuccessPage: NextPage = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Subscription Confirmed - Silence Cutter">
      <div className="bg-gray-50 min-h-screen py-12">
        <div className="max-w-lg mx-auto bg-white rounded-lg shadow-sm p-8">
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>

            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Subscription Confirmed!
            </h1>

            <p className="text-center text-gray-600 mb-8">
              Thank you for subscribing to Silence Cutter. Your payment was
              processed successfully and your subscription is now active.
            </p>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 w-full mb-8">
              <h2 className="text-lg font-semibold mb-3">
                Subscription Details
              </h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Plan:</span>
                  <span className="font-medium">
                    {user?.subscription_tier.charAt(0).toUpperCase() +
                      user?.subscription_tier.slice(1)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="text-green-600 font-medium">Active</span>
                </div>
                {user?.subscription_end_date && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Next Billing Date:</span>
                    <span className="font-medium">
                      {new Date(
                        user.subscription_end_date
                      ).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-4 w-full">
              <Link href="/dashboard" className="btn btn-primary w-full">
                Go to Dashboard
              </Link>
              <Link href="/videos/upload" className="btn btn-outline w-full">
                Upload Your First Video
              </Link>
            </div>

            <p className="text-sm text-gray-500 mt-8 text-center">
              We've sent a confirmation email with your subscription details. If
              you have any questions, please contact our{" "}
              <a
                href="/help"
                className="text-primary-600 hover:text-primary-800"
              >
                support team
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CheckoutSuccessPage;
