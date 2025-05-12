import { useState, useEffect } from "react";
import { NextPage } from "next";
import Link from "next/link";
import { useRouter } from "next/router";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/contexts/AuthContext";
import { videosAPI } from "@/lib/api";

interface Video {
  id: string;
  title: string;
  description: string;
  duration: number;
  file_size: number;
  status: string;
  created_at: string;
  updated_at: string;
  thumbnail_url?: string;
  output_url?: string;
  silence_removed_seconds?: number;
}

const DashboardPage: NextPage = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [recentVideos, setRecentVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch recent videos
  useEffect(() => {
    const fetchRecentVideos = async () => {
      if (!isAuthenticated) return;

      try {
        setIsLoading(true);
        const response = await videosAPI.getVideos(1, 5);
        setRecentVideos(response.data.items);
      } catch (err) {
        console.error("Failed to fetch recent videos:", err);
        setError("Failed to load recent videos. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecentVideos();
  }, [isAuthenticated]);

  // Format date to readable format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(date);
  };

  // Format seconds to minutes and seconds
  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  // Format bytes to human readable format
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  // Calculate usage percentage
  const usagePercentage = user
    ? (user.processing_minutes_used / user.processing_minutes_limit) * 100
    : 0;

  if (authLoading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard - Silence Cutter">
      <div className="bg-gray-50 min-h-screen py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

          {/* Usage Stats */}
          <div className="bg-white shadow-sm rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Usage Statistics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 rounded-md p-4">
                <p className="text-sm text-gray-500 mb-1">Subscription Plan</p>
                <p className="text-xl font-medium text-gray-900">
                  {user?.subscription_tier.charAt(0).toUpperCase() +
                    user?.subscription_tier.slice(1) || "Free"}
                </p>
                {user?.subscription_end_date && (
                  <p className="text-xs text-gray-500 mt-2">
                    Renews on {formatDate(user.subscription_end_date)}
                  </p>
                )}
              </div>

              <div className="bg-gray-50 rounded-md p-4">
                <p className="text-sm text-gray-500 mb-1">Processing Minutes</p>
                <p className="text-xl font-medium text-gray-900">
                  {user?.processing_minutes_used || 0} /{" "}
                  {user?.processing_minutes_limit || 0} minutes
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div
                    className={`h-2.5 rounded-full ${
                      usagePercentage > 90
                        ? "bg-red-600"
                        : usagePercentage > 70
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    }`}
                    style={{
                      width: `${Math.min(usagePercentage, 100)}%`,
                    }}
                  ></div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-md p-4">
                <p className="text-sm text-gray-500 mb-1">Processed Videos</p>
                <p className="text-xl font-medium text-gray-900">
                  {recentVideos.filter((v) => v.status === "completed").length}
                </p>
              </div>
            </div>
            {user?.subscription_tier === "free" && (
              <div className="mt-6">
                <Link
                  href="/subscription"
                  className="btn btn-primary inline-block"
                >
                  Upgrade your plan
                </Link>
              </div>
            )}
          </div>

          {/* Quick Upload */}
          <div className="bg-white shadow-sm rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Upload
            </h2>
            <p className="text-gray-600 mb-4">
              Upload a new video to have its silence automatically removed.
            </p>
            <Link href="/videos/upload" className="btn btn-primary">
              Upload Video
            </Link>
          </div>

          {/* Recent Videos */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Recent Videos
              </h2>
              <Link
                href="/videos"
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                View all
              </Link>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {isLoading ? (
              <p className="text-gray-500">Loading videos...</p>
            ) : recentVideos.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">
                  You haven't uploaded any videos yet.
                </p>
                <Link href="/videos/upload" className="btn btn-primary">
                  Upload your first video
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Title
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Duration
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Status
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Date
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {recentVideos.map((video) => (
                      <tr key={video.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {video.title}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">
                            {formatDuration(video.duration)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                            ${
                              video.status === "completed"
                                ? "bg-green-100 text-green-800"
                                : video.status === "failed"
                                ? "bg-red-100 text-red-800"
                                : video.status === "processing"
                                ? "bg-blue-100 text-blue-800"
                                : "bg-yellow-100 text-yellow-800"
                            }`}
                          >
                            {video.status.charAt(0).toUpperCase() +
                              video.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">
                            {formatDate(video.created_at)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <Link
                            href={`/videos/${video.id}`}
                            className="text-primary-600 hover:text-primary-900 mr-4"
                          >
                            View
                          </Link>
                          {video.status === "completed" && video.output_url && (
                            <a
                              href={video.output_url}
                              className="text-primary-600 hover:text-primary-900"
                              download
                            >
                              Download
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DashboardPage;
