import { Suspense, type ReactElement } from "react";
import { RefreshCw } from "lucide-react";

export default function JobApplicationSetupLayout({
  children,
}: {
  children: React.ReactNode;
}): ReactElement {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
          <div className="text-center">
            <RefreshCw className="w-12 h-12 mx-auto text-green-600 animate-spin mb-4" />
            <p className="text-green-800">Loading...</p>
          </div>
        </div>
      }
    >
      {children}
    </Suspense>
  );
}
