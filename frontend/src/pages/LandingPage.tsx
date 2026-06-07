import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  MessageSquare, LayoutDashboard, Package, Shield, ArrowRight,
  Cpu, BarChart3, Users, CheckCircle
} from 'lucide-react';
import ShinyText from '../components/ui/ShinyText';

const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_105406_16f4600d-7a92-4292-b96e-b19156c7830a.mp4';

const features = [
  {
    icon: MessageSquare,
    title: 'AI-Powered Chat',
    desc: 'Natural language asset management. Ask your AI agent to assign, track, or audit assets conversationally.',
    color: 'from-brand-500 to-cyan-500',
  },
  {
    icon: LayoutDashboard,
    title: 'Enterprise Dashboard',
    desc: 'Real-time analytics with status tracking, category breakdowns, and actionable audit insights.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: Package,
    title: 'Asset Lifecycle',
    desc: 'Full CRUD with workflow automation — assign, return, audit, and clear assets seamlessly.',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    icon: Shield,
    title: 'Audit Compliance',
    desc: 'Complete audit trail logging every action. Stay compliant and transparent with detailed history.',
    color: 'from-amber-500 to-orange-500',
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
};

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Video Background */}
      <div className="fixed inset-0 z-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          src={VIDEO_URL}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-surface-950/90 via-surface-950/80 to-surface-950" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Nav */}
        <nav className="flex items-center justify-between max-w-7xl mx-auto px-6 py-5">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-brand-500/30">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-white">
              Assets<span className="gradient-text">Tracking</span> Agent
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="btn-ghost hidden sm:flex items-center gap-2 text-sm">
              Dashboard
            </Link>
            <Link to="/chat" className="btn-primary flex items-center gap-2 text-sm">
              <MessageSquare className="w-4 h-4" /> Launch Agent
            </Link>
          </div>
        </nav>

        {/* Hero */}
        <section className="max-w-7xl mx-auto px-6 pt-16 pb-24 md:pt-24 md:pb-32">
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div variants={item} className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-sm font-medium mb-6">
              <Cpu className="w-3.5 h-3.5" /> AI-Powered Enterprise Platform
            </motion.div>

            <motion.h1 variants={item} className="text-4xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6">
              <span className="text-white">Intelligent </span>
              <ShinyText text="Asset" className="text-4xl md:text-6xl lg:text-7xl font-bold" />
              <br />
              <span className="text-white">Management</span>
            </motion.h1>

            <motion.p variants={item} className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Transform asset tracking with AI-driven conversations. Assign, audit, and manage
              hardware through an intelligent agent that understands your needs.
            </motion.p>

            <motion.div variants={item} className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
              <Link to="/chat" className="btn-primary flex items-center gap-2 text-base px-8 py-3.5 shadow-xl shadow-brand-500/20">
                <MessageSquare className="w-5 h-5" /> Talk to AI Agent
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link to="/dashboard" className="btn-secondary flex items-center gap-2 text-base px-8 py-3.5">
                <LayoutDashboard className="w-5 h-5" /> View Dashboard
              </Link>
            </motion.div>
          </motion.div>
        </section>

        {/* Features */}
        <section className="max-w-7xl mx-auto px-6 pb-24">
          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-100px' }}
            className="grid md:grid-cols-2 gap-6"
          >
            {features.map((feat) => {
              const Icon = feat.icon;
              return (
                <motion.div
                  key={feat.title}
                  variants={item}
                  whileHover={{ y: -4 }}
                  className="glass-card-hover p-8 group"
                >
                  <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${feat.color} flex items-center justify-center mb-5 shadow-lg group-hover:shadow-xl transition-shadow`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{feat.title}</h3>
                  <p className="text-slate-400 leading-relaxed">{feat.desc}</p>
                </motion.div>
              );
            })}
          </motion.div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/5 py-8">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-slate-500 text-sm">
              <Cpu className="w-4 h-4" />
              <span>© 2025 AssetsTracking Agent. Enterprise Asset Management.</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-slate-500">
              <Link to="/dashboard" className="hover:text-brand-400 transition-colors">Dashboard</Link>
              <Link to="/chat" className="hover:text-brand-400 transition-colors">AI Agent</Link>
              <Link to="/assets" className="hover:text-brand-400 transition-colors">Assets</Link>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
