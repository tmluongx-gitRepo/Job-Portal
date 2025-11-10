import { type ReactElement } from "react";
import Link from "next/link";
import { Home, Search } from "lucide-react";

export default function NotFound(): ReactElement {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <h1 className="text-9xl font-bold text-green-600 mb-4">404</h1>
        <h2 className="text-3xl font-bold text-green-900 mb-4">
          Page Not Found
        </h2>
        <p className="text-green-700 mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center"
          >
            <Home className="w-5 h-5 mr-2" />
            Go Home
          </Link>
          <Link
            href="/jobs"
            className="bg-yellow-100 text-green-700 border border-green-300 px-6 py-3 rounded-lg font-semibold hover:bg-yellow-200 transition-all flex items-center justify-center"
          >
            <Search className="w-5 h-5 mr-2" />
            Search Jobs
          </Link>
        </div>
      </div>
    </div>
  );
}
