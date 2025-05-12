"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { SubscriptionPlan } from "@/types";
import { useAuth } from "@/contexts/AuthContext";

export default function SubscriptionPage() {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([
    {
      id: "free",
      name: "Free",
      price: 0,
      description: "For casual users",
      features: [
        "10 minutes of processing per month",
        "720p max resolution",
        "Basic silence detection",
      ],
      processing_minutes: 10,
      max_resolution: "720p",
    },
    {
      id: "pro",
      name: "Pro",
      price: 9.99,
      description: "For content creators",
      features: [
        "120 minutes of processing per month",
        "1080p max resolution",
        "Advanced silence detection",
        "Customizable silence thresholds",
      ],
      processing_minutes: 120,
      max_resolution: "1080p",
      is_popular: true,
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: 29.99,
      description: "For professional studios",
      features: [
        "Unlimited processing minutes",
        "4K max resolution",
        "Premium silence detection",
        "Batch processing",
        "Priority support",
      ],
      processing_minutes: Infinity,
      max_resolution: "4K",
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"plans" | "billing">("plans");
  const [currentPlan, setCurrentPlan] = useState<string | null>(null);
  const [isChangingPlan, setIsChangingPlan] = useState(false);

  const { user, isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      setCurrentPlan(user.subscription_tier);
    }
  }, [user]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthLoading && !isAuthenticated) {
      router.push("/login?redirect=subscription");
    }
  }, [isAuthenticated, isAuthLoading, router]);

  const handlePlanChange = async (planId: string) => {
    if (planId === currentPlan) return;

    // Free plan can be selected without payment
    if (planId === "free") {
      try {
        setIsChangingPlan(true);
        setError("");

        // TODO: Implement API call to downgrade to free plan
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulated API call

        setCurrentPlan("free");
        setIsChangingPlan(false);
      } catch (err) {
        setError("Failed to change plan. Please try again.");
        setIsChangingPlan(false);
      }
      return;
    }

    // For paid plans, redirect to checkout
    router.push(`/checkout?plan=${planId}`);
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Subscription Management
        </h1>

        {/* Tab navigation */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("plans")}
              className={`${
                activeTab === "plans"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Plans
            </button>
            <button
              onClick={() => setActiveTab("billing")}
              className={`${
                activeTab === "billing"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Billing History
            </button>
          </nav>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Plans tab */}
        {activeTab === "plans" && (
          <div>
            <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
              <h2 className="text-lg font-semibold mb-4">Current Plan</h2>
              {user && (
                <div>
                  <p className="text-xl font-bold text-gray-900 mb-2">
                    {user.subscription_tier.charAt(0).toUpperCase() +
                      user.subscription_tier.slice(1)}{" "}
                    Plan
                  </p>
                  <div className="flex items-center mb-4">
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mr-2">
                      <div
                        className={`h-2.5 rounded-full ${
                          user.processing_minutes_used /
                            user.processing_minutes_limit >
                          0.9
                            ? "bg-red-600"
                            : user.processing_minutes_used /
                                user.processing_minutes_limit >
                              0.7
                            ? "bg-yellow-500"
                            : "bg-green-500"
                        }`}
                        style={{
                          width: `${Math.min(
                            (user.processing_minutes_used /
                              user.processing_minutes_limit) *
                              100,
                            100
                          )}%`,
                        }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-500 whitespace-nowrap">
                      {user.processing_minutes_used} /{" "}
                      {user.processing_minutes_limit} minutes
                    </span>
                  </div>
                  {user.subscription_end_date &&
                    user.subscription_tier !== "free" && (
                      <p className="text-sm text-gray-500">
                        Your subscription renews on{" "}
                        {new Date(
                          user.subscription_end_date
                        ).toLocaleDateString()}
                      </p>
                    )}
                </div>
              )}
            </div>

            <h2 className="text-xl font-semibold mb-6">Available Plans</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className={`card relative border ${
                    plan.is_popular
                      ? "border-2 border-primary-500"
                      : "border-gray-200"
                  } hover:shadow-lg transition-shadow duration-300`}
                >
                  {plan.is_popular && (
                    <div className="absolute top-0 right-0 bg-primary-500 text-white px-3 py-1 text-sm font-semibold">
                      Popular
                    </div>
                  )}
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                    <p className="text-4xl font-bold mb-1">
                      ${plan.price}
                      {plan.price > 0 && (
                        <span className="text-sm font-normal">/month</span>
                      )}
                    </p>
                    <p className="text-sm text-gray-500 mb-4">
                      {plan.description}
                    </p>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5 text-green-500 mr-2"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                              clipRule="evenodd"
                            />
                          </svg>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={() => handlePlanChange(plan.id)}
                      disabled={isChangingPlan || plan.id === currentPlan}
                      className={`w-full ${
                        plan.id === currentPlan
                          ? "btn btn-disabled"
                          : plan.is_popular
                          ? "btn btn-primary"
                          : "btn btn-outline"
                      }`}
                    >
                      {isChangingPlan
                        ? "Processing..."
                        : plan.id === currentPlan
                        ? "Current Plan"
                        : "Select Plan"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Billing History tab */}
        {activeTab === "billing" && (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold">Billing History</h2>
            </div>

            {/* For demo, show empty state */}
            <div className="p-8 text-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-12 w-12 text-gray-400 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-gray-500 mb-4">
                No billing history available.
              </p>
              <p className="text-sm text-gray-500">
                Your invoice history will appear here once you subscribe to a
                paid plan.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
