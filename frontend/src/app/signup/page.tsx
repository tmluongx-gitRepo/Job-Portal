'use client';

import { useState } from 'react';

import Link from 'next/link';
import { User, Mail, Lock, Eye, EyeOff, Heart, Users } from 'lucide-react';

export default function SignupPage(): React.ReactElement {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    accountType: 'jobseeker',
    agreeToTerms: false,
    subscribeToUpdates: true
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement signup functionality
    console.log('Form submitted:', formData);
    alert('Welcome to Career Harmony! 🌱');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-green-200/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-amber-200/20 rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-md w-full space-y-8 relative z-10">
          {/* Page Content Header */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-green-900 mb-2">
              Join Our Community
            </h2>
            <p className="text-green-700 mb-8">
              Start cultivating a career that honors your whole self
            </p>
          </div>

          {/* Sign-up Form */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-green-200 p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Account Type Selection */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-3">
                  I&apos;m looking to...
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <label className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    formData.accountType === 'jobseeker' 
                      ? 'border-green-500 bg-gradient-to-br from-green-50 to-amber-50' 
                      : 'border-green-200 bg-white/50'
                  }`}>
                    <input
                      type="radio"
                      name="accountType"
                      value="jobseeker"
                      checked={formData.accountType === 'jobseeker'}
                      onChange={handleInputChange}
                      className="sr-only"
                    />
                    <div className="flex flex-col items-center text-center w-full">
                      <User className="w-6 h-6 text-green-600 mb-2" />
                      <span className="font-medium text-green-800">Find Work</span>
                      <span className="text-xs text-green-600">Job Seeker</span>
                    </div>
                  </label>
                  <label className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    formData.accountType === 'employer' 
                      ? 'border-green-500 bg-gradient-to-br from-green-50 to-amber-50' 
                      : 'border-green-200 bg-white/50'
                  }`}>
                    <input
                      type="radio"
                      name="accountType"
                      value="employer"
                      checked={formData.accountType === 'employer'}
                      onChange={handleInputChange}
                      className="sr-only"
                    />
                    <div className="flex flex-col items-center text-center w-full">
                      <Users className="w-6 h-6 text-green-600 mb-2" />
                      <span className="font-medium text-green-800">Hire Talent</span>
                      <span className="text-xs text-green-600">Employer</span>
                    </div>
                  </label>
                </div>
              </div>

              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    First Name
                  </label>
                  <input
                    name="firstName"
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="Your first name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Last Name
                  </label>
                  <input
                    name="lastName"
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="Your last name"
                    required
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-green-500" />
                  </div>
                  <input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-green-500" />
                  </div>
                  <input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-12 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="Create a secure password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-green-500 hover:text-green-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-green-500 hover:text-green-600" />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-green-500" />
                  </div>
                  <input
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-12 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                    placeholder="Confirm your password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-green-500 hover:text-green-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-green-500 hover:text-green-600" />
                    )}
                  </button>
                </div>
              </div>

              {/* Checkboxes */}
              <div className="space-y-3">
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    name="agreeToTerms"
                    checked={formData.agreeToTerms}
                    onChange={handleInputChange}
                    className="mt-1 w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-400"
                    required
                  />
                  <span className="text-sm text-green-700">
                    I agree to the{' '}
                    <Link href="/terms" className="text-green-800 underline hover:text-green-900">
                      Terms of Service
                    </Link>
                    {' '}and{' '}
                    <Link href="/privacy" className="text-green-800 underline hover:text-green-900">
                      Privacy Policy
                    </Link>
                  </span>
                </label>
                
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    name="subscribeToUpdates"
                    checked={formData.subscribeToUpdates}
                    onChange={handleInputChange}
                    className="mt-1 w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-400"
                  />
                  <span className="text-sm text-green-700">
                    Send me updates about new opportunities and community events (you can unsubscribe anytime)
                  </span>
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2 transition-all flex items-center justify-center"
              >
                <Heart className="w-5 h-5 mr-2" />
                Join Career Harmony
              </button>
            </form>

            {/* Sign-in link */}
            <div className="mt-6 text-center">
              <p className="text-sm text-green-700">
                Already have an account?{' '}
                <Link href="/login" className="font-medium text-green-800 underline hover:text-green-900 transition-colors">
                  Sign in here
                </Link>
              </p>
            </div>
          </div>

          {/* Community Promise */}
          <div className="bg-white/50 backdrop-blur-sm rounded-xl border border-green-200 p-6 text-center">
            <div className="flex justify-center mb-3">
              <div className="w-8 h-8 bg-gradient-to-r from-green-100 to-amber-100 rounded-full flex items-center justify-center">
                <Heart className="w-4 h-4 text-green-600" />
              </div>
            </div>
            <h3 className="font-semibold text-green-800 mb-2">Our Community Promise</h3>
            <p className="text-sm text-green-700">
              We respect your privacy, honor your worth, and believe your well-being matters more than profit. 
              Your data won&apos;t be sold, and you&apos;ll always be treated as a whole human being.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}



