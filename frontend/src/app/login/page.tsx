"use client";

import {
  useState,
  type FormEvent,
  type ChangeEvent,
  type ReactElement,
} from "react";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, Eye, EyeOff, Heart } from "lucide-react";
import { authApi, type ApiError } from "@/lib/api";

export default function LoginPage(): ReactElement {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleSubmit = async (e: FormEvent): Promise<void> => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await authApi.login({
        email: formData.email,
        password: formData.password,
      });

      // Redirect based on account type
      const accountType = response.user.account_type;
      const redirectPath =
        accountType === "employer" ? "/employer-dashboard" : "/dashboard";
      router.push(redirectPath);
    } catch (err) {
      console.error("Login error:", err);
      const apiError = err as ApiError;

      // Handle specific error cases
      if (apiError.status === 401) {
        setError("Invalid email or password. Please try again.");
      } else if (apiError.status === 503) {
        setError(
          "Authentication service is temporarily unavailable. Please try again later."
        );
      } else {
        setError(apiError.message || "Login failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/3 left-1/3 w-64 h-64 bg-green-200/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/3 right-1/3 w-64 h-64 bg-amber-200/20 rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-sm w-full space-y-8 relative z-10">
          {/* Page Content Header */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-green-900 mb-2">
              Welcome Back
            </h2>
            <p className="text-green-700 mb-8">
              Continue cultivating your purposeful career
            </p>
          </div>

          {/* Login Form */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-green-200 p-8">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-green-500" />
                  </div>
                  <input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-green-500" />
                  </div>
                  <input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-12 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-green-500 hover:text-green-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-green-500 hover:text-green-600" />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={formData.rememberMe}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-400"
                  />
                  <span className="text-sm text-green-700">Remember me</span>
                </label>

                <Link
                  href="/forgot-password"
                  className="text-sm text-green-700 hover:text-green-800 underline transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Heart className="w-5 h-5 mr-2" />
                {isSubmitting ? "Signing in..." : "Sign In"}
              </button>
            </form>

            {/* Sign-up link */}
            <div className="mt-6 text-center">
              <p className="text-sm text-green-700">
                New to Career Harmony?{" "}
                <Link
                  href="/signup"
                  className="font-medium text-green-800 underline hover:text-green-900 transition-colors"
                >
                  Join our community
                </Link>
              </p>
            </div>
          </div>

          {/* Welcome Back Message */}
          <div className="bg-white/50 backdrop-blur-sm rounded-xl border border-green-200 p-6 text-center">
            <div className="flex justify-center mb-3">
              <div className="w-8 h-8 bg-gradient-to-r from-green-100 to-amber-100 rounded-full flex items-center justify-center">
                <Heart className="w-4 h-4 text-green-600" />
              </div>
            </div>
            <h3 className="font-semibold text-green-800 mb-2">
              Welcome Back to Your Journey
            </h3>
            <p className="text-sm text-green-700">
              Ready to continue building a career that honors your whole self?
              Your community is here to support your growth.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
