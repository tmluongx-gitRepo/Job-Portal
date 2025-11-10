'use client';

import { useState } from 'react';
import { RefreshCw } from 'lucide-react';


const healthyReminders = [
  'Your worth is not defined by your job title or salary.',
  'Rejection is redirection—the right opportunity is waiting for you.',
  'It\'s okay to take breaks and rest during your job search.',
  'Your skills and experience have value, even if one employer doesn\'t recognize it.',
  'Job hunting is a process, not a reflection of your capabilities.',
  'You deserve work that respects your boundaries and wellbeing.',
  'Every "no" brings you closer to the right "yes".',
  'Your career journey is valid, regardless of how long it takes.',
  'It\'s perfectly normal to feel discouraged—give yourself grace.',
  'You are more than your resume or LinkedIn profile.',
  'Quality over quantity—better to apply to fewer jobs if your mental health is already frayed.',
  'Your mental health matters more than landing any particular job.',
  'Rejection does not diminish your value as a person.',
  'Take care of yourself first—everything else can wait.',
  'Your path is uniquely yours—comparison robs you of joy.'
];

export default function HealthyReminders(): React.ReactElement {
  const [currentReminder, setCurrentReminder] = useState(healthyReminders[0]);

  const generateReminder = (): void => {
    const randomIndex = Math.floor(Math.random() * healthyReminders.length);
    setCurrentReminder(healthyReminders[randomIndex]);
  };

  return (
    <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-md border border-green-200 p-6 max-w-2xl mx-auto mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-green-800">Healthy Reminders™</h3>
        <button 
          onClick={generateReminder}
          className="flex items-center space-x-2 text-green-600 hover:text-green-800 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="text-sm">New Reminder</span>
        </button>
      </div>
      <div className="bg-gradient-to-r from-green-50 to-amber-50 border border-green-200 rounded-lg p-4">
        <p className="text-green-800 font-medium italic">&quot;{currentReminder}&quot;</p>
      </div>
      <p className="text-xs text-green-600 mt-2">
        *Remember that job hunting outcomes are not a reflection of your personal worth.
      </p>
    </div>
  );
}

