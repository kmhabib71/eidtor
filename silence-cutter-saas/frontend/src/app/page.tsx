import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-sm lg:flex">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to Silence Cutter
        </h1>
      </div>

      <div className="text-center mb-12">
        <p className="text-xl mb-6">
          Automatically detect and remove silent parts from your videos, making
          them more engaging and concise.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link href="/dashboard" className="btn btn-primary">
            Go to Dashboard
          </Link>
          <Link href="/subscription" className="btn btn-outline">
            View Plans
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Upload & Process</h2>
          <p>
            Upload your videos and our advanced AI will automatically detect and
            remove silence.
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Save Time</h2>
          <p>
            Reduce video length by removing unnecessary silence, making your
            content more engaging.
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-3">Multiple Plans</h2>
          <p>
            Choose from our Free, Pro, and Enterprise plans to suit your video
            processing needs.
          </p>
        </div>
      </div>
    </main>
  );
}
