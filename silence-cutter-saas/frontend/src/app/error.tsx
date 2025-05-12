"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        <h1 className="text-3xl font-bold text-red-600 mb-4">
          Something went wrong!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          We apologize for the inconvenience. An unexpected error has occurred.
        </p>
        <div className="space-y-4">
          <button onClick={() => reset()} className="btn btn-primary w-full">
            Try again
          </button>
          <Link href="/" className="btn btn-outline w-full block text-center">
            Return to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
