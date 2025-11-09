import Link from 'next/link';
import {
  Heart,
  Users,
  Lightbulb,
  Target,
  Star,
  Shield,
  Zap,
  Globe,
  ArrowRight,
} from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Hero Section */}
      <section className="py-16 lg:py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="bg-gradient-to-r from-green-100 to-amber-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Heart className="w-10 h-10 text-green-600" />
            </div>
            <h1 className="text-4xl lg:text-5xl font-bold text-green-900 mb-6">
              Redefining How We Think About Work
            </h1>
            <p className="text-xl text-green-700 max-w-3xl mx-auto leading-relaxed">
              Career Harmony was born from a simple belief: every person deserves
              dignity in their job search, and every company deserves to find
              talent that truly fits their culture and values.
            </p>
          </div>

          {/* Mission Statement */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-green-200 p-8 mb-16">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-green-900 mb-4">
                Our Mission
              </h2>
              <p className="text-lg text-green-700 leading-relaxed max-w-4xl mx-auto">
                To create a job portal that treats people as whole human beings,
                not just resumes. We believe in matching not just skills and
                requirements, but values, culture, and life goals. By providing
                smarter, more intuitive tools, we make hiring more efficient for
                employers while creating a more dignified experience for job
                seekers. Career Harmony is where meaningful work meets meaningful
                lives.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-16 bg-white/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-green-900 mb-4">
              What We Stand For
            </h2>
            <p className="text-green-700 text-lg">
              The principles that guide everything we do
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Human Dignity */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Heart className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-green-900 mb-3">
                Human Dignity
              </h3>
              <p className="text-green-700">
                Every person has inherent worth. We design experiences that
                affirm value rather than exploit vulnerability during the job
                search process.
              </p>
            </div>

            {/* Authentic Connections */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-green-900 mb-3">
                Authentic Connections
              </h3>
              <p className="text-green-700">
                We focus on genuine cultural and values alignment, not just
                checking boxes. True career harmony happens when people and
                companies are authentically matched.
              </p>
            </div>

            {/* Work-Life Integration */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-green-900 mb-3">
                Work-Life Harmony
              </h3>
              <p className="text-green-700">
                We believe work should enhance life, not consume it. We help
                people find roles that respect boundaries and support personal
                growth.
              </p>
            </div>

            {/* Transparent Process */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-green-900 mb-3">
                Radical Transparency
              </h3>
              <p className="text-green-700">
                Clear salary ranges, honest job descriptions, and realistic
                expectations. We believe transparency benefits everyone in the
                hiring process.
              </p>
            </div>

            {/* Inclusive Design */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Globe className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-green-900 mb-3">
                Inclusive by Design
              </h3>
              <p className="text-green-700">
                Our platform is built to welcome all people, regardless of
                background, career stage, or life circumstances. Everyone
                deserves opportunity.
              </p>
            </div>

            {/* Sustainable Growth */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Lightbulb className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-green-900 mb-3">
                Sustainable Growth
              </h3>
              <p className="text-green-700">
                We support career paths that are sustainable for both individuals
                and organizations, focusing on long-term success over quick fixes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Approach Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-green-900 mb-4">
              How We're Different
            </h2>
            <p className="text-green-700 text-lg">
              A fundamentally human-centered approach to job matching
            </p>
          </div>

          <div className="grid grid-cols-1 gap-12 items-center max-w-4xl mx-auto">
            <div>
              <h3 className="text-2xl font-semibold text-green-900 mb-6 text-center">
                Our Approach
              </h3>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="bg-green-100 rounded-full p-2 mt-1">
                    <Heart className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-800 mb-1">
                      Dignity-First Design
                    </h4>
                    <p className="text-green-700 text-sm">
                      Our interface reminds you of your worth, not your
                      deficiencies. Supportive messaging throughout your journey.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-green-100 rounded-full p-2 mt-1">
                    <Target className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-800 mb-1">
                      Values-Based Matching
                    </h4>
                    <p className="text-green-700 text-sm">
                      Beyond skills matching, we help connect people and
                      companies whose values and culture naturally align.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-green-100 rounded-full p-2 mt-1">
                    <Users className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-800 mb-1">
                      Better Tools for Everyone
                    </h4>
                    <p className="text-green-700 text-sm">
                      Smart, intuitive tools that make hiring more efficient for
                      employers while creating a more dignified experience for
                      job seekers.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-green-100 rounded-full p-2 mt-1">
                    <Star className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-green-800 mb-1">
                      Progress Celebration
                    </h4>
                    <p className="text-green-700 text-sm">
                      We celebrate growth and development for everyone,
                      recognizing that career success is about progress, not
                      perfection.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="py-16 bg-white/40">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-green-900 mb-4">
              Our Story
            </h2>
            <p className="text-green-700 text-lg">Why Career Harmony exists</p>
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-green-200 p-8">
            <div className="prose prose-green max-w-none">
              <p className="text-green-700 text-lg leading-relaxed mb-6">
                Career Harmony was created by people who experienced the
                traditional job search process and knew there had to be a better
                way. We saw talented individuals lose confidence in systems that
                seemed designed to highlight their inadequacies rather than their
                potential.
              </p>

              <p className="text-green-700 text-lg leading-relaxed mb-6">
                We witnessed companies struggling to find cultural fits because
                traditional platforms focused on keyword matching rather than
                human connection. We saw the toll that dehumanizing application
                processes took on everyone involved.
              </p>

              <p className="text-green-700 text-lg leading-relaxed">
                So we decided to build something different. A platform that
                remembers we're all human beings seeking meaningful work and
                meaningful connections. Career Harmony isn't just about finding
                a job—it's about finding where you belong.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-2xl text-white p-8 lg:p-12">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Experience the Difference?
            </h2>
            <p className="text-xl mb-8 text-green-100">
              Join a community that believes in the dignity and potential of every
              person.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/signup"
                className="bg-white text-green-700 px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition-all flex items-center justify-center"
              >
                I'm Looking for Work
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
              <Link
                href="/signup"
                className="bg-green-800 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-900 transition-all flex items-center justify-center"
              >
                I'm Hiring Talent
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

