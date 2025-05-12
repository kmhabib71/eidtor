// User interface
export interface User {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: string;
  subscription_end_date?: string;
  processing_minutes_used: number;
  processing_minutes_limit: number;
  created_at: string;
  updated_at: string;
}

// Video interface
export interface Video {
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

// Subscription plan interface
export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  description: string;
  features: string[];
  processing_minutes: number;
  max_resolution: string;
  is_popular?: boolean;
}

// Pagination interface
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// API response interface
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
