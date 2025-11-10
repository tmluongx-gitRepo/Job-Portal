import Link from "next/link";
import { Leaf } from "lucide-react";


export default function Header(): React.ReactElement {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-green-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-3">
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-amber-500 rounded-lg flex items-center justify-center">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-2xl font-bold bg-gradient-to-r from-green-700 to-green-800 bg-clip-text text-transparent">
                Career Harmony
              </span>
              <div className="text-xs text-green-600">
                Work-Life Balance • Professional Growth
              </div>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            <Link
              href="/#solutions"
              className="text-green-700 hover:text-green-800 font-medium transition-colors"
            >
              Solutions
            </Link>
            <Link
              href="/jobs"
              className="text-green-700 hover:text-green-800 font-medium transition-colors"
            >
              Career Search
            </Link>
            <Link
              href="/about"
              className="text-green-700 hover:text-green-800 font-medium transition-colors"
            >
              About Us
            </Link>
          </nav>

          <div className="flex items-center space-x-4">
            <Link href="/login" className="text-green-700 hover:text-green-800 font-medium transition-colors">
              Sign In
            </Link>
            <Link href="/signup" className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-2 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all shadow-sm">
              Join Our Community
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
