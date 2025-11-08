import { Sun, Leaf, Globe, TrendingUp, Users, Zap, ArrowRight } from 'lucide-react';
import JobSearchForm from '../components/JobSearchForm';
import HealthyReminders from '../components/HealthyReminders';
import JobCard from '../components/JobCard';
import SolutionCard from '../components/SolutionCard';

export default function Home() {
  const featuredJobs = [
    {
      title: 'Sustainability Director',
      company: 'EcoGrowth Co.',
      location: 'Portland, OR',
      salary: '$85k - $105k + Impact Bonus',
      description: 'Lead regenerative practices that heal communities while growing sustainable business solutions...',
      tags: ['#Regenerative', '#Community'],
      icon: Leaf,
    },
    {
      title: 'Community Tech Lead',
      company: 'Bright Future Labs',
      location: 'Remote + Local Hubs',
      salary: '$95k - $120k',
      description: 'Build technology that empowers communities and creates equitable access to digital resources...',
      tags: ['#TechForGood', '#Collaborative'],
      icon: Sun,
      iconColor: 'text-amber-600',
    },
    {
      title: 'Regenerative Business Strategist',
      company: 'Living Systems Inc',
      location: 'Boulder, CO',
      salary: '$105k - $135k',
      description: 'Design business models that thrive by giving back more than they take from the world...',
      tags: ['#SystemsThinking', '#Purpose'],
      icon: Globe,
    },
  ];

  const solutions = [
    {
      icon: TrendingUp,
      title: 'Purpose-Driven Talent Matching',
      description: 'Connect with opportunities that align your skills with your values, creating meaningful work that contributes to a thriving world.',
      note: '*Because your career should feed your soul, not just your bank account',
    },
    {
      icon: Users,
      title: 'Community-Centered Networks',
      description: 'Build authentic relationships with like-minded professionals who share your commitment to creating positive change in the world.',
      note: '*Real connections that grow into lasting partnerships',
    },
    {
      icon: Zap,
      title: 'Holistic Growth Platform',
      description: 'Develop your whole self through work that challenges you professionally while nurturing your personal growth and well-being.',
      note: '*Career development that honors your humanity',
      iconColor: 'text-amber-600',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Hero Section */}
      <section className="pt-12 pb-16 bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-green-900 mb-6 leading-tight">
              Cultivate Your Career
              <span className="block bg-gradient-to-r from-amber-600 to-green-600 bg-clip-text text-transparent">
                In Harmony with Your Best Self
              </span>
            </h1>
            
            <div className="flex justify-center mb-6">
              <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-100 to-amber-100 rounded-full text-green-800 text-sm font-medium border border-green-200">
                <Sun className="w-4 h-4 mr-2" />
                Work That Nurtures Career and Soul
              </div>
            </div>
            
            <p className="text-xl text-green-700 mb-8 max-w-3xl mx-auto leading-relaxed">
              <em>Work in harmony:</em> Find careers that honor your whole self—where you don't have to sacrifice 
              your wellbeing, values, or dignity just to make a living.
            </p>

            <JobSearchForm />

            <HealthyReminders />

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-3xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-700">247K</div>
                <div className="text-green-600">Purpose-Driven Professionals</div>
                <div className="text-sm text-green-500">*Real humans creating real change</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-700">98%</div>
                <div className="text-green-600">Workplace Satisfaction</div>
                <div className="text-sm text-green-500">*When work aligns with values</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-700">∞</div>
                <div className="text-green-600">Potential for Good</div>
                <div className="text-sm text-green-500">*Together we grow stronger</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Job Listings */}
      <section className="py-16 bg-white/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-green-900 mb-4">
              Meaningful Career Opportunities
            </h2>
            <p className="text-green-700 text-xl">
              (Work that nourishes your soul and the world)
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {featuredJobs.map((job, index) => (
              <JobCard key={index} {...job} />
            ))}
          </div>

          <div className="text-center mt-12">
            <button className="bg-white/80 backdrop-blur-sm text-green-700 border-2 border-green-600 px-8 py-4 rounded-xl font-semibold hover:bg-green-600 hover:text-white transition-all flex items-center mx-auto shadow-sm">
              Explore More Opportunities
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        </div>
      </section>

      {/* Solutions Section */}
      <section id="solutions" className="py-16 bg-gradient-to-r from-green-50 to-amber-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-green-900 mb-4">
              Sustainable Workforce Solutions
            </h2>
            <p className="text-green-700 text-xl">(Growing people and community together)</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {solutions.map((solution, index) => (
              <SolutionCard key={index} {...solution} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-green-800 to-green-900">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Grow Your Purpose-Driven Career?
          </h2>
          <p className="text-xl text-green-100 mb-8 leading-relaxed">
            Join a community of professionals cultivating meaningful work that nurtures people, communities, and our planet.
          </p>
          <p className="text-green-200 mb-8">
            <em>(Side effects may include: deep fulfillment, authentic relationships, and helping heal the world)</em>
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-green-800 px-8 py-4 rounded-xl font-bold text-lg hover:bg-green-50 transition-colors">
              Search Future Growth Opportunities
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
