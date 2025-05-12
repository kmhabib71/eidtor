import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { useRouter } from "next/router";
import { videosAPI } from "@/lib/api";

interface VideoUploaderProps {
  onUploadSuccess?: (videoId: string) => void;
  onUploadError?: (error: string) => void;
}

const VideoUploader: React.FC<VideoUploaderProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];

      // Validate file type
      if (!selectedFile.type.startsWith("video/")) {
        setError("Please select a valid video file");
        return;
      }

      setFile(selectedFile);
      setError("");

      // Auto-fill title from filename
      if (!title) {
        const fileName = selectedFile.name.replace(/\.[^/.]+$/, ""); // Remove extension
        setTitle(fileName);
      }
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];

      // Validate file type
      if (!droppedFile.type.startsWith("video/")) {
        setError("Please drop a valid video file");
        return;
      }

      setFile(droppedFile);
      setError("");

      // Auto-fill title from filename
      if (!title) {
        const fileName = droppedFile.name.replace(/\.[^/.]+$/, ""); // Remove extension
        setTitle(fileName);
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a video to upload");
      return;
    }

    if (!title.trim()) {
      setError("Please enter a title for your video");
      return;
    }

    setIsUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    if (description) formData.append("description", description);

    try {
      const response = await videosAPI.uploadVideo(formData);

      if (onUploadSuccess) {
        onUploadSuccess(response.data.id);
      } else {
        router.push(`/videos/${response.data.id}`);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        "Failed to upload video. Please try again.";
      setError(errorMessage);

      if (onUploadError) {
        onUploadError(errorMessage);
      }
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold mb-4">Upload Video</h2>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleUpload}>
        <div
          className={`border-2 border-dashed rounded-lg p-8 mb-6 text-center cursor-pointer
            ${
              isDragging
                ? "border-primary-500 bg-primary-50"
                : "border-gray-300 hover:border-primary-500"
            }
            ${file ? "bg-green-50 border-green-300" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleBrowseClick}
        >
          <input
            type="file"
            className="hidden"
            accept="video/*"
            onChange={handleFileSelect}
            ref={fileInputRef}
          />

          {file ? (
            <div>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-12 w-12 text-green-500 mx-auto mb-4"
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
              <p className="text-lg font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500 mt-1">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              <button
                type="button"
                className="mt-4 text-sm text-red-600 hover:text-red-800"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
              >
                Remove file
              </button>
            </div>
          ) : (
            <div>
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
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="text-lg font-medium text-gray-900">
                Drag and drop your video here
              </p>
              <p className="text-sm text-gray-500 mt-1">
                or click to browse your files
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Supports MP4, MOV, AVI, WebM (max 500 MB)
              </p>
            </div>
          )}
        </div>

        <div className="mb-4">
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Title*
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input"
            placeholder="Enter a title for your video"
            required
          />
        </div>

        <div className="mb-6">
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Description (optional)
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input"
            rows={3}
            placeholder="Enter a description for your video"
          />
        </div>

        {isUploading ? (
          <div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
              <div
                className="bg-primary-600 h-2.5 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 text-center">
              Uploading... {uploadProgress}%
            </p>
          </div>
        ) : (
          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={!file || isUploading}
          >
            Upload Video
          </button>
        )}
      </form>
    </div>
  );
};

export default VideoUploader;
