import { type ReactElement } from "react";
import {
  MapPin,
  DollarSign,
  Bookmark,
  BookmarkCheck,
  Building2,
  Clock,
  Heart,
  Sparkles,
  Users,
  Filter,
} from "lucide-react";

interface Job {
  id: string | number; // Support both for backwards compatibility
  title: string;
  company: string;
  location: string;
  type: string;
  salary: string | null;
  posted: string;
  description: string;
  requirements: string[];
  benefits: string[];
  values: string[] | null;
  cultureFit: string[] | null;
  hasApplied?: boolean;
  appliedDate?: string;
}

interface JobListingProps {
  job: Job;
  isSaved: boolean;
  isExpanded: boolean;
  saveMessage?: string;
  onSave: () => void;
  onToggleExpand: () => void;
}

export default function JobListing({
  job,
  isSaved,
  isExpanded,
  saveMessage,
  onSave,
  onToggleExpand,
}: JobListingProps): ReactElement {
  return (
    <div className="bg-white/70 backdrop-blur-sm border border-green-200 rounded-xl shadow-sm hover:shadow-md transition-all p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-semibold text-green-900 mb-1">
                {job.title}
              </h3>
              <div className="flex items-center space-x-4 text-sm text-green-600 mb-2">
                <span className="flex items-center">
                  <Building2 className="w-4 h-4 mr-1" />
                  {job.company}
                </span>
                <span className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  {job.location}
                </span>
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {job.type}
                </span>
              </div>
            </div>

            {/* Save Button */}
            <div className="relative">
              <button
                onClick={onSave}
                className={`p-2 rounded-lg transition-all ${
                  isSaved
                    ? "bg-yellow-100 text-green-700 hover:bg-yellow-200"
                    : "bg-green-50 text-green-600 hover:bg-green-100"
                }`}
              >
                {isSaved ? (
                  <BookmarkCheck className="w-5 h-5" />
                ) : (
                  <Bookmark className="w-5 h-5" />
                )}
              </button>

              {/* Save Message */}
              {saveMessage && (
                <div className="absolute top-full right-0 mt-2 bg-green-800 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap z-10">
                  {saveMessage}
                </div>
              )}
            </div>
          </div>

          {/* Salary and Applied Badge */}
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {job.salary ? (
                <span className="inline-flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  <DollarSign className="w-4 h-4 mr-1" />
                  {job.salary}
                </span>
              ) : (
                <span className="inline-flex items-center bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                  <DollarSign className="w-4 h-4 mr-1" />
                  Salary not disclosed
                </span>
              )}
              <span className="text-sm text-green-600">
                Posted {job.posted}
              </span>
            </div>

            {/* Applied Badge */}
            {job.hasApplied && (
              <div className="flex items-center">
                <span className="inline-flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium border border-blue-200">
                  ✓ Already Applied
                </span>
                {job.appliedDate && (
                  <span className="ml-2 text-xs text-gray-500">
                    {(() => {
                      // Parse the date string consistently to avoid hydration mismatch
                      const date = new Date(job.appliedDate + "T00:00:00");
                      const months = [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                      ];
                      const month = months[date.getMonth()];
                      const day = date.getDate();
                      return `${month} ${day}`;
                    })()}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Description */}
          <p className="text-green-800 mb-4 leading-relaxed">
            {job.description}
          </p>

          {/* Desktop: Always show full content */}
          <div className="hidden md:block">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <h4 className="font-medium text-green-800 mb-2">
                  What they&apos;re looking for:
                </h4>
                <ul className="space-y-1">
                  {job.requirements.map((req, index) => (
                    <li
                      key={index}
                      className="text-sm text-green-700 flex items-start"
                    >
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-green-800 mb-2">
                  What they offer:
                </h4>
                <ul className="space-y-1">
                  {job.benefits.map((benefit, index) => (
                    <li
                      key={index}
                      className="text-sm text-green-700 flex items-start"
                    >
                      <Heart className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-green-500" />
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-green-800 mb-2">
                  Company Values:
                </h4>
                {job.values ? (
                  <ul className="space-y-1">
                    {job.values.map((value, index) => (
                      <li
                        key={index}
                        className="text-sm text-green-700 flex items-start"
                      >
                        <Sparkles className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-amber-500" />
                        {value}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">
                    Values not available
                  </p>
                )}
              </div>

              <div>
                <h4 className="font-medium text-green-800 mb-2">
                  Culture Fit Hints:
                </h4>
                {job.cultureFit ? (
                  <ul className="space-y-1">
                    {job.cultureFit.map((hint, index) => (
                      <li
                        key={index}
                        className="text-sm text-green-700 flex items-start"
                      >
                        <Users className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-green-500" />
                        {hint}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">
                    Culture info not available
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Mobile: Truncated view with expand option */}
          <div className="md:hidden">
            {!isExpanded ? (
              <div className="space-y-3 mb-4">
                {/* Show only first requirement and benefit */}
                <div className="grid grid-cols-1 gap-3">
                  <div>
                    <h4 className="font-medium text-green-800 mb-1">
                      Looking for:
                    </h4>
                    <div className="text-sm text-green-700 flex items-start">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {job.requirements[0]}
                      {job.requirements.length > 1 && (
                        <span className="ml-2 text-green-500">
                          +{job.requirements.length - 1} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-green-800 mb-1">Offers:</h4>
                    <div className="text-sm text-green-700 flex items-start">
                      <Heart className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-green-500" />
                      {job.benefits[0]}
                      {job.benefits.length > 1 && (
                        <span className="ml-2 text-green-500">
                          +{job.benefits.length - 1} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={onToggleExpand}
                  className="text-green-600 text-sm font-medium hover:text-green-800 transition-colors"
                >
                  View more details
                </button>
              </div>
            ) : (
              <div className="space-y-4 mb-4">
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <h4 className="font-medium text-green-800 mb-2">
                      What they&apos;re looking for:
                    </h4>
                    <ul className="space-y-1">
                      {job.requirements.map((req, index) => (
                        <li
                          key={index}
                          className="text-sm text-green-700 flex items-start"
                        >
                          <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {req}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-medium text-green-800 mb-2">
                      What they offer:
                    </h4>
                    <ul className="space-y-1">
                      {job.benefits.map((benefit, index) => (
                        <li
                          key={index}
                          className="text-sm text-green-700 flex items-start"
                        >
                          <Heart className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-green-500" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {job.values && (
                    <div>
                      <h4 className="font-medium text-green-800 mb-2">
                        Company Values:
                      </h4>
                      <ul className="space-y-1">
                        {job.values.map((value, index) => (
                          <li
                            key={index}
                            className="text-sm text-green-700 flex items-start"
                          >
                            <Sparkles className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-amber-500" />
                            {value}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {job.cultureFit && (
                    <div>
                      <h4 className="font-medium text-green-800 mb-2">
                        Culture Fit Hints:
                      </h4>
                      <ul className="space-y-1">
                        {job.cultureFit.map((hint, index) => (
                          <li
                            key={index}
                            className="text-sm text-green-700 flex items-start"
                          >
                            <Users className="w-3 h-3 mt-1 mr-2 flex-shrink-0 text-green-500" />
                            {hint}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <button
                  onClick={onToggleExpand}
                  className="text-green-600 text-sm font-medium hover:text-green-800 transition-colors flex items-center"
                >
                  Show less
                  <Filter className="w-4 h-4 ml-1 rotate-180" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          {job.hasApplied ? (
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                disabled
                className="bg-gray-100 text-gray-500 px-6 py-2 rounded-lg font-semibold cursor-not-allowed flex items-center justify-center"
              >
                ✓ Applied
              </button>
              <button className="bg-yellow-100 text-green-700 border border-green-300 px-6 py-2 rounded-lg font-medium hover:bg-yellow-200 transition-all">
                Update Application
              </button>
            </div>
          ) : (
            <>
              <button className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-2 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center">
                Apply Now
              </button>
              <button className="bg-yellow-100 text-green-700 border border-green-300 px-6 py-2 rounded-lg font-medium hover:bg-yellow-200 transition-all">
                Learn More
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
