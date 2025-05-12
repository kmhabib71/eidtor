import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-6">
          Page Not Found
        </h2>
        <p className="text-lg text-gray-600 mb-8">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <div className="space-y-4">
          <Link href="/" className="btn btn-primary w-full block text-center">
            Return to Home
          </Link>
          <Link
            href="/help"
            className="btn btn-outline w-full block text-center"
          >
            Get Help
          </Link>
        </div>
      </div>
    </div>
  );
}
