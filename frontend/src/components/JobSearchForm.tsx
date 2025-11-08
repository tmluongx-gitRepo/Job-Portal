'use client';

import { useState } from 'react';
import { Search, Target } from 'lucide-react';

export default function JobSearchForm() {
  const [searchTerm, setSearchTerm] = useState('');
  const [location, setLocation] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log('Search:', { searchTerm, location });
  };

  return (
    <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-green-200 p-6 max-w-4xl mx-auto mb-8">
      <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-500 w-5 h-5" />
          <input
            type="text"
            placeholder="Search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent text-lg bg-white/80"
          />
        </div>
        
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="Location (City, State)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent text-lg bg-white/80"
          />
        </div>
        
        <button 
          type="submit"
          className="bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center shadow-sm"
        >
          <Target className="w-5 h-5 mr-2" />
          Search Future Growth Opportunities
        </button>
      </form>
    </div>
  );
}

