import Link from "next/link";
import { Leaf } from "lucide-react";


export default function Footer(): React.ReactElement {
  return (
    <footer className="bg-green-950 text-white py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-green-600 to-amber-500 rounded-lg flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-lg font-bold">Career Harmony</span>
                <div className="text-xs text-green-300">
                  Work-Life Balance • Professional Growth
                </div>
              </div>
            </div>
            <p className="text-green-300 text-sm">
              Redefining how we think about work, one meaningful connection at a
              time.
            </p>
          </div>

          {/* For Job Seekers */}
          <div>
            <h4 className="font-semibold text-white mb-4">For Job Seekers</h4>
            <ul className="space-y-2 text-sm text-green-300">
              <li>
                <Link
                  href="/jobs"
                  className="hover:text-white transition-colors"
                >
                  Find Jobs
                </Link>
              </li>
              <li>
                <Link
                  href="/signup"
                  className="hover:text-white transition-colors"
                >
                  Create Profile
                </Link>
              </li>
            </ul>
          </div>

          {/* For Employers */}
          <div>
            <h4 className="font-semibold text-white mb-4">For Employers</h4>
            <ul className="space-y-2 text-sm text-green-300">
              <li>
                <Link
                  href="/job-posting"
                  className="hover:text-white transition-colors"
                >
                  Post Jobs
                </Link>
              </li>
              <li>
                <Link
                  href="/employer-dashboard"
                  className="hover:text-white transition-colors"
                >
                  Find Talent
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold text-white mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-green-300">
              <li>
                <Link
                  href="/about"
                  className="hover:text-white transition-colors"
                >
                  About Us
                </Link>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-green-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-green-300 text-sm">
            © 2025 Career Harmony. All rights reserved.
          </p>
          <div className="flex space-x-6 text-sm text-green-300 mt-4 md:mt-0">
            <span>Made with 💚 for everyone seeking meaningful work</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
