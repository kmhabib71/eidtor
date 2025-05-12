import { useState, useEffect } from "react";
import { NextPage } from "next";
import { useRouter } from "next/router";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/contexts/AuthContext";
import { SubscriptionPlan } from "@/types";

const CheckoutPage: NextPage = () => {
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");

  const { user, isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const router = useRouter();

  // Get the plan ID from the URL query parameter
  useEffect(() => {
    if (router.query.plan) {
      const planId = router.query.plan as string;

      // Fetch plan details (mock data for now)
      const plans: SubscriptionPlan[] = [
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
      ];

      const plan = plans.find((p) => p.id === planId);
      if (plan) {
        setSelectedPlan(plan);
      } else {
        setError("Invalid plan selected.");
      }

      setIsLoading(false);
    }
  }, [router.query.plan]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthLoading && !isAuthenticated) {
      router.push("/login?redirect=checkout");
    }
  }, [isAuthenticated, isAuthLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedPlan) return;

    try {
      setIsProcessing(true);
      setError("");

      // TODO: Implement actual payment processing with Stripe
      await new Promise((resolve) => setTimeout(resolve, 2000)); // Simulate API call

      // Redirect to success page
      router.push("/checkout/success");
    } catch (err) {
      setError("Payment processing failed. Please try again.");
      setIsProcessing(false);
    }
  };

  if (isAuthLoading || isLoading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </Layout>
    );
  }

  if (!selectedPlan) {
    return (
      <Layout title="Checkout - Silence Cutter">
        <div className="min-h-screen py-12">
          <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-sm">
            <h1 className="text-2xl font-bold text-red-600 mb-4">
              Plan Selection Error
            </h1>
            <p className="text-gray-700 mb-6">
              {error ||
                "No plan was selected. Please choose a subscription plan to continue."}
            </p>
            <button
              onClick={() => router.push("/subscription")}
              className="btn btn-primary w-full"
            >
              Go to Subscription Plans
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Checkout - Silence Cutter">
      <div className="bg-gray-50 min-h-screen py-12">
        <div className="max-w-3xl mx-auto px-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Complete Your Subscription
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
            {/* Order Summary */}
            <div className="md:col-span-2 bg-white p-6 rounded-lg shadow-sm h-fit">
              <h2 className="text-lg font-semibold mb-4">Order Summary</h2>
              <div className="border-t border-gray-200 pt-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">
                    {selectedPlan.name} Plan
                  </span>
                  <span className="font-medium">
                    ${selectedPlan.price}/month
                  </span>
                </div>
                <div className="flex justify-between py-2 text-sm text-gray-500">
                  <span>Tax</span>
                  <span>$0.00</span>
                </div>
                <div className="border-t border-gray-200 pt-2 mt-2">
                  <div className="flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span>${selectedPlan.price}/month</span>
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <h3 className="font-medium text-gray-900">
                    What's included:
                  </h3>
                  <ul className="space-y-3">
                    {selectedPlan.features.map((feature, index) => (
                      <li key={index} className="flex items-center text-sm">
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
                </div>
              </div>
            </div>

            {/* Payment Form */}
            <div className="md:col-span-3 bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-semibold mb-6">
                Payment Information
              </h2>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="mb-6">
                  <label
                    htmlFor="cardName"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Name on card
                  </label>
                  <input
                    type="text"
                    id="cardName"
                    className="input"
                    placeholder="Full name as displayed on card"
                    required
                  />
                </div>

                <div className="mb-6">
                  <label
                    htmlFor="cardNumber"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Card number
                  </label>
                  <input
                    type="text"
                    id="cardNumber"
                    className="input"
                    placeholder="xxxx xxxx xxxx xxxx"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div>
                    <label
                      htmlFor="expiryDate"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Expiry date
                    </label>
                    <input
                      type="text"
                      id="expiryDate"
                      className="input"
                      placeholder="MM/YY"
                      required
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="cvc"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      CVC
                    </label>
                    <input
                      type="text"
                      id="cvc"
                      className="input"
                      placeholder="123"
                      required
                    />
                  </div>
                </div>

                <div className="mb-6">
                  <label
                    htmlFor="billingAddress"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Billing address
                  </label>
                  <input
                    type="text"
                    id="billingAddress"
                    className="input"
                    placeholder="Street address"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div>
                    <label
                      htmlFor="city"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      City
                    </label>
                    <input type="text" id="city" className="input" required />
                  </div>
                  <div>
                    <label
                      htmlFor="postalCode"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Postal code
                    </label>
                    <input
                      type="text"
                      id="postalCode"
                      className="input"
                      required
                    />
                  </div>
                </div>

                <div className="mb-6">
                  <label
                    htmlFor="country"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Country
                  </label>
                  <select id="country" className="input" required>
                    <option value="" disabled selected>
                      Select country
                    </option>
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="GB">United Kingdom</option>
                    <option value="AU">Australia</option>
                    <option value="DE">Germany</option>
                    <option value="FR">France</option>
                    <option value="JP">Japan</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="flex items-center mb-6">
                  <input
                    id="savePaymentInfo"
                    name="savePaymentInfo"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label
                    htmlFor="savePaymentInfo"
                    className="ml-2 block text-sm text-gray-900"
                  >
                    Save this payment information for next time
                  </label>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-full"
                  disabled={isProcessing}
                >
                  {isProcessing
                    ? "Processing..."
                    : `Pay $${selectedPlan.price}/month`}
                </button>

                <p className="text-xs text-gray-500 mt-4 text-center">
                  By completing your purchase you agree to our{" "}
                  <a
                    href="/terms"
                    className="text-primary-600 hover:text-primary-800"
                  >
                    Terms of Service
                  </a>{" "}
                  and{" "}
                  <a
                    href="/privacy"
                    className="text-primary-600 hover:text-primary-800"
                  >
                    Privacy Policy
                  </a>
                  .
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CheckoutPage;
