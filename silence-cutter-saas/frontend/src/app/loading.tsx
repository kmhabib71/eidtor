export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="relative inline-flex">
          <div className="w-8 h-8 bg-primary-500 rounded-full opacity-60 animate-ping"></div>
          <div className="w-8 h-8 bg-primary-500 rounded-full absolute top-0 left-0 opacity-30 animate-pulse"></div>
        </div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
