import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useRouter } from "next/router";
import { authAPI } from "@/lib/api";
import jwt_decode from "jwt-decode";

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  subscription_tier: string;
  processing_minutes_used: number;
  processing_minutes_limit: number;
  subscription_end_date?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string
  ) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check if token is valid
  const isTokenValid = () => {
    const token = localStorage.getItem("token");
    if (!token) return false;

    try {
      const decoded: any = jwt_decode(token);
      // Check if token is expired
      return decoded.exp > Date.now() / 1000;
    } catch (error) {
      return false;
    }
  };

  // Load user data from API if token exists
  const loadUser = async () => {
    try {
      setIsLoading(true);
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      console.error("Failed to load user:", error);
      localStorage.removeItem("token");
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Effect to check authentication on mount
  useEffect(() => {
    if (isTokenValid()) {
      loadUser();
    } else {
      localStorage.removeItem("token");
      setUser(null);
      setIsLoading(false);

      // Redirect to login if on protected page
      const path = router.pathname;
      if (
        path !== "/" &&
        path !== "/login" &&
        path !== "/register" &&
        !path.startsWith("/help")
      ) {
        router.push("/login");
      }
    }
  }, [router.pathname]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authAPI.login(email, password);
      const { access_token } = response.data;
      localStorage.setItem("token", access_token);
      await loadUser();
      router.push("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    email: string,
    password: string,
    fullName: string
  ) => {
    setIsLoading(true);
    try {
      await authAPI.register({ email, password, full_name: fullName });
      await login(email, password);
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    router.push("/login");
  };

  const refreshUser = async () => {
    return loadUser();
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
