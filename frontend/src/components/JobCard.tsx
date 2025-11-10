import React from 'react';


interface JobCardProps {
  title: string;
  company: string;
  location: string;
  salary: string;
  description: string;
  tags: string[];
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  iconColor?: string;
}

export default function JobCard({ 
  title, 
  company, 
  location, 
  salary, 
  description, 
  tags, 
  icon: Icon,
  iconColor = 'text-green-600'
}: JobCardProps) {
  return (
    <div className="bg-white/80 backdrop-blur-sm border border-green-200 rounded-xl shadow-sm hover:shadow-md transition-all p-6 hover:border-green-300">
      <div className="flex items-start space-x-4 mb-4">
        <div className="w-12 h-12 bg-gradient-to-br from-green-100 to-amber-100 rounded-lg flex items-center justify-center">
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-green-900 mb-1">{title}</h3>
          <p className="text-green-700 font-medium">{company}</p>
          <p className="text-green-600 text-sm">{location}</p>
        </div>
      </div>
      <p className="text-lg font-bold text-green-800 mb-4">{salary}</p>
      <p className="text-green-700 mb-4">{description}</p>
      <div className="flex flex-wrap gap-2 mb-4">
        {tags.map((tag, index) => (
          <span 
            key={index}
            className="bg-gradient-to-r from-green-100 to-amber-100 text-green-800 px-3 py-1 rounded-full text-sm border border-green-200"
          >
            {tag}
          </span>
        ))}
      </div>
      <button className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all">
        Cultivate Change
      </button>
    </div>
  );
}

