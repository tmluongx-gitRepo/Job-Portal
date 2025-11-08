import React from 'react';

interface SolutionCardProps {
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  title: string;
  description: string;
  note: string;
  iconColor?: string;
}

export default function SolutionCard({ 
  icon: Icon, 
  title, 
  description, 
  note,
  iconColor = 'text-green-600'
}: SolutionCardProps) {
  return (
    <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-sm border border-green-200 p-8 hover:shadow-md transition-all">
      <div className="w-16 h-16 bg-gradient-to-br from-green-100 to-amber-100 rounded-xl flex items-center justify-center mb-6">
        <Icon className={`w-8 h-8 ${iconColor}`} />
      </div>
      <h3 className="text-2xl font-bold text-green-900 mb-4">{title}</h3>
      <p className="text-green-700 leading-relaxed mb-4">{description}</p>
      <p className="text-sm text-green-600 italic">{note}</p>
    </div>
  );
}

