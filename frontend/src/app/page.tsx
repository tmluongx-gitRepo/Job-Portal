import type { JSX } from "react";

export default function Home(): JSX.Element {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="text-center space-y-8 px-4">
        <h1 className="text-6xl font-bold text-gray-900">Job Portal</h1>
        <p className="text-xl text-gray-600 max-w-2xl">
          Welcome to your full-stack job portal application. Built with Next.js,
          FastAPI, and Docker.
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/jobs"
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Browse Jobs
          </a>
          <a
            href="/api/health"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-white text-indigo-600 rounded-lg border-2 border-indigo-600 hover:bg-indigo-50 transition-colors"
          >
            Check API Status
          </a>
        </div>
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">🚀 Fast Development</h3>
            <p className="text-gray-600">
              Hot reload on both frontend and backend
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">🐳 Docker-First</h3>
            <p className="text-gray-600">
              Consistent environment for all team members
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">💪 Type-Safe</h3>
            <p className="text-gray-600">TypeScript + Python type hints</p>
          </div>
        </div>
      </main>
    </div>
  );
}
