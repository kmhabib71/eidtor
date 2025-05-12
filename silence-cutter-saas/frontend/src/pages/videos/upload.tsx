import { NextPage } from "next";
import { useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/layout/Layout";
import VideoUploader from "@/components/videos/VideoUploader";
import { useAuth } from "@/contexts/AuthContext";

const VideoUploadPage: NextPage = () => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <Layout title="Upload Video - Silence Cutter">
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </Layout>
    );
  }

  // Check if user has reached their upload limit
  const hasReachedProcessingLimit =
    user && user.processing_minutes_used >= user.processing_minutes_limit;

  return (
    <Layout title="Upload Video - Silence Cutter">
      <div className="bg-gray-50 min-h-screen py-8">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            Upload a New Video
          </h1>

          <div className="mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4">
                Video Processing Guidelines
              </h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                <li>Supported formats: MP4, MOV, AVI, WebM</li>
                <li>Maximum file size: 500 MB</li>
                <li>
                  Maximum resolution:{" "}
                  {user?.subscription_tier === "enterprise"
                    ? "4K (3840×2160)"
                    : user?.subscription_tier === "pro"
                    ? "1080p (1920×1080)"
                    : "720p (1280×720)"}
                </li>
                <li>
                  You have{" "}
                  <span className="font-medium">
                    {Math.max(
                      0,
                      user?.processing_minutes_limit -
                        user?.processing_minutes_used
                    )}{" "}
                    minutes
                  </span>{" "}
                  of processing time remaining this month
                </li>
              </ul>
            </div>
          </div>

          {hasReachedProcessingLimit ? (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-6 rounded-lg shadow-sm">
              <h2 className="text-lg font-semibold mb-2">
                Processing Limit Reached
              </h2>
              <p className="mb-4">
                You've used all of your processing minutes for this month. To
                upload more videos, please consider upgrading your plan or wait
                until your processing minutes refresh.
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={() => router.push("/subscription")}
                  className="btn btn-primary"
                >
                  Upgrade Plan
                </button>
                <button
                  onClick={() => router.push("/dashboard")}
                  className="btn btn-outline"
                >
                  Return to Dashboard
                </button>
              </div>
            </div>
          ) : (
            <VideoUploader
              onUploadSuccess={(videoId) => {
                router.push(`/videos/${videoId}`);
              }}
            />
          )}
        </div>
      </div>
    </Layout>
  );
};

export default VideoUploadPage;
