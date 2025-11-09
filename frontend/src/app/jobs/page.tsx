import type { JSX } from "react";

export default function JobsPage(): JSX.Element {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Browse Jobs</h1>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600">
            Job listings will appear here. Connect to the backend API to fetch
            jobs.
          </p>
        </div>
      </div>
    </div>
  );
}
