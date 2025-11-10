"use client";

import { type ReactElement } from "react";
import Link from "next/link";
import { AlertCircle, RefreshCw, Home } from "lucide-react";

export default function Error({
  error: _error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): ReactElement {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <AlertCircle className="w-20 h-20 text-amber-600 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-green-900 mb-4">
          Something went wrong
        </h2>
        <p className="text-green-700 mb-8">
          We encountered an error while processing your request. Please try
          again.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={reset}
            className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center"
          >
            <RefreshCw className="w-5 h-5 mr-2" />
            Try Again
          </button>
          <Link
            href="/"
            className="bg-yellow-100 text-green-700 border border-green-300 px-6 py-3 rounded-lg font-semibold hover:bg-yellow-200 transition-all flex items-center justify-center"
          >
            <Home className="w-5 h-5 mr-2" />
            Go Home
          </Link>
        </div>
      </div>
    </div>
  );
}
