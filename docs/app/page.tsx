'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, useScroll, useSpring } from 'motion/react'
import {
  Bot,
  Braces,
  GitBranch,
  Github,
  Hammer,
  Layers,
  Shield,
  Terminal,
  Zap,
  ArrowRight,
  Sparkles,
  ChevronRight,
} from 'lucide-react'
import Link from 'next/link'
import { AsciiLogo } from '@/components/ascii-logo'

const features = [
  {
    icon: Bot,
    title: 'Multi-Turn Agent Loop',
    description:
      'Think of it as having a thoughtful pair programmer. The agent plans its approach, pulls in the right tools, and iterates until things click — no babysitting required.',
  },
  {
    icon: Braces,
    title: '11 Built-in Tools',
    description:
      'Everything you\'d reach for in a coding session — reading files, running commands, searching code, browsing docs, jotting down notes. All under one roof, no context switching.',
  },
  {
    icon: Layers,
    title: 'MCP Integration',
    description:
      'Got custom tools or external services? Hook them right in via MCP. Works over stdio or SSE, so you can extend the agent with whatever you need — your setup, your rules.',
  },
  {
    icon: Shield,
    title: 'Safety & Approval',
    description:
      'From "just do it" YOLO mode to "ask me first" confirmations. The agent flags risky commands, checks paths, and keeps you in the loop — because trust is earned, not assumed.',
  },
  {
    icon: GitBranch,
    title: 'Lifecycle Hooks',
    description:
      'Want to run something before the agent kicks off? After a tool fires? On errors? Shell-based hooks let you plug into every stage. Feels like custom middleware for your workflow.',
  },
  {
    icon: Zap,
    title: 'Streaming Responses',
    description:
      'Watch things unfold in real time. Tokens stream in, tool calls fire mid-response, and everything renders beautifully with Markdown and syntax highlighting. No staring at a spinner.',
  },
  {
    icon: Hammer,
    title: 'Context Compression',
    description:
      'Long conversations? No sweat. When the context window fills up, the agent intelligently summarizes and prunes — keeping what matters and trimming the fluff so you never hit the ceiling.',
  },
  {
    icon: Terminal,
    title: 'Sub-Agent Delegation',
    description:
      'Some tasks deserve their own sandbox. Spin up sub-agents for deep codebase dives or isolated code reviews — each with focused context, so the main thread stays clean and fast.',
  },
]

function PremiumFeatureCard({
  icon: Icon,
  title,
  description,
  index,
}: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description: string
  index: number
}) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    setHoverPos({
      x: ((e.clientX - rect.left) / rect.width) * 100,
      y: ((e.clientY - rect.top) / rect.height) * 100,
    })
  }

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{
        duration: 0.6,
        delay: (index % 4) * 0.1,
        ease: [0.22, 1, 0.36, 1],
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative"
    >
      <div
        className="absolute -inset-[1px] rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background:
            'linear-gradient(var(--border-angle, 0deg), var(--accent-purple), var(--accent-mauve), var(--accent-peach), var(--accent-purple))',
          animation: 'border-rotate 4s linear infinite',
        }}
      />

      <div className="relative h-full rounded-2xl bg-[var(--card-bg)] p-7 border border-[var(--border)] group-hover:border-transparent transition-all duration-500 overflow-hidden">
        <div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
          style={{
            background: `radial-gradient(400px circle at ${hoverPos.x}% ${hoverPos.y}%, color-mix(in srgb, var(--accent-purple) 15%, transparent), transparent 40%)`,
          }}
        />

        <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none" />

        <div className="relative z-10">
          <div className="flex items-center justify-between mb-5">
            <div className="relative">
              <div className="absolute inset-0 bg-[var(--accent-purple)] blur-xl opacity-0 group-hover:opacity-40 transition-opacity duration-500" />
              <div className="relative w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--accent-purple)]/20 to-[var(--accent-mauve)]/10 border border-[var(--border)] flex items-center justify-center group-hover:scale-110 group-hover:border-[var(--accent-mauve)] transition-all duration-500">
                <Icon className="w-5 h-5 text-[var(--accent-peach)]" />
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-300" />
          </div>

          <h3 className="text-lg font-bold text-foreground mb-3 tracking-tight">
            {title}
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {description}
          </p>
        </div>
      </div>
    </motion.div>
  )
}

export default function HomePage() {
  const heroRef = useRef<HTMLElement>(null)
  const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 })
  const { scrollYProgress } = useScroll()
  const smoothProgress = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  })

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      if (!heroRef.current) return
      const rect = heroRef.current.getBoundingClientRect()
      setMousePos({
        x: Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)),
        y: Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height)),
      })
    }
    window.addEventListener('mousemove', handleMouse)
    return () => window.removeEventListener('mousemove', handleMouse)
  }, [])

  return (
    <main className="min-h-screen bg-background text-foreground overflow-x-hidden relative">
      <style jsx global>{`
        @property --border-angle {
          syntax: '<angle>';
          inherits: false;
          initial-value: 0deg;
        }
        @keyframes border-rotate {
          to { --border-angle: 360deg; }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-12px) rotate(0.5deg); }
        }
        @keyframes gradient-x {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes pulse-ring {
          0% { transform: scale(0.95); opacity: 0.8; }
          50% { transform: scale(1.05); opacity: 0.4; }
          100% { transform: scale(0.95); opacity: 0.8; }
        }
        .gradient-text {
          background: linear-gradient(
            135deg,
            var(--accent-peach) 0%,
            var(--accent-mauve) 50%,
            var(--accent-purple) 100%
          );
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          background-size: 200% 200%;
          animation: gradient-x 6s ease infinite;
        }
        .shine-button {
          position: relative;
          overflow: hidden;
          isolation: isolate;
        }
        .shine-button::after {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(
            110deg,
            transparent 30%,
            rgba(255, 255, 255, 0.15) 50%,
            transparent 70%
          );
          transform: translateX(-100%);
          transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
          z-index: -1;
        }
        .shine-button:hover::after {
          transform: translateX(100%);
        }
        .dot-pattern {
          background-image: radial-gradient(circle, var(--border) 1px, transparent 1px);
          background-size: 24px 24px;
        }
      `}</style>

      {/* Scroll Progress Bar */}
      <motion.div
        className="fixed top-0 inset-x-0 h-[2px] bg-gradient-to-r from-[var(--accent-purple)] via-[var(--accent-mauve)] to-[var(--accent-peach)] origin-left z-[100] shadow-[0_0_10px_var(--accent-purple)]"
        style={{ scaleX: smoothProgress }}
      />

      {/* Navigation */}
      <div className="fixed top-4 sm:top-6 inset-x-0 z-50 flex justify-center px-4 sm:px-6 pointer-events-none">
        <motion.nav
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="pointer-events-auto relative px-4 sm:px-7 h-14 sm:h-16 flex items-center justify-between gap-3 sm:gap-8 max-w-4xl w-full rounded-full"
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(20px) saturate(180%)',
            WebkitBackdropFilter: 'blur(20px) saturate(180%)',
            border: '1px solid color-mix(in srgb, var(--border) 60%, transparent)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
          }}
        >
          <Link href="/" className="flex items-center gap-2 shrink-0 group">
            <div className="relative">
              <div className="absolute inset-0 bg-[var(--accent-purple)] blur-md opacity-60 group-hover:opacity-100 transition-opacity" />
              <Sparkles className="relative w-4 h-4 text-[var(--accent-peach)]" />
            </div>
            <span className="text-sm font-bold text-foreground tracking-wide">
              Flux-CLI
            </span>
          </Link>

          <div className="flex items-center gap-1 sm:gap-4">
            <Link
              href="/docs/introduction"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors whitespace-nowrap relative group px-2 py-1"
            >
              Docs
              <span className="absolute -bottom-0.5 left-2 right-2 w-auto h-px bg-[var(--accent-peach)] scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left" />
            </Link>

            <Link
              href="https://github.com/manmit-s/flux-cli"
              className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-[var(--border)] text-muted-foreground hover:text-[var(--accent-peach)] hover:border-[var(--accent-mauve)] transition-all duration-300"
              style={{ background: 'rgba(255, 255, 255, 0.03)' }}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm font-medium">GitHub</span>
            </Link>

            <Link
              href="/docs/quick-start"
              className="shine-button ml-1 px-4 sm:px-6 py-2 sm:py-2.5 text-sm font-bold rounded-full bg-[var(--accent-purple)] text-[var(--accent-ivory)] hover:bg-[var(--accent-mauve)] transition-colors whitespace-nowrap shadow-lg shadow-[var(--accent-purple)]/30"
            >
              Get Started
            </Link>
          </div>
        </motion.nav>
      </div>

      {/* Hero Section */}
      <section ref={heroRef} className="relative pt-40 pb-24 px-6 overflow-hidden">
        <motion.div
          className="absolute inset-0 pointer-events-none opacity-60"
          animate={{
            background: `radial-gradient(800px circle at ${mousePos.x * 100}% ${mousePos.y * 100}%, color-mix(in srgb, var(--accent-purple) 25%, transparent), transparent 50%)`,
          }}
          transition={{ type: 'tween', ease: 'linear', duration: 0.15 }}
        />

        <div
          className="absolute inset-0 pointer-events-none opacity-40"
          style={{
            background:
              'radial-gradient(ellipse at top, color-mix(in srgb, var(--accent-mauve) 20%, transparent), transparent 60%)',
          }}
        />

        <div className="absolute inset-0 dot-pattern opacity-20 pointer-events-none [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />

        <div className="relative max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[var(--border)] text-xs font-medium text-muted-foreground mb-8"
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent-peach)] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--accent-peach)]" />
            </span>
            <span>Now in active development</span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="mb-2"
            style={{ animation: 'float 6s ease-in-out infinite' }}
          >
            <AsciiLogo size="lg" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-6 max-w-3xl mx-auto leading-[1.1]"
          >
            The AI coding agent that{' '}
            <span className="gradient-text">actually ships code</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.35 }}
            className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed"
          >
            An extensible AI coding agent for the terminal featuring multi-tool
            orchestration, MCP integration, lifecycle hooks, and streaming
            responses.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-3"
          >
            <Link
              href="/docs/quick-start"
              className="shine-button group inline-flex items-center gap-2 px-8 py-3.5 text-sm font-bold rounded-full bg-[var(--accent-purple)] text-[var(--accent-ivory)] hover:bg-[var(--accent-mauve)] transition-colors shadow-xl shadow-[var(--accent-purple)]/30"
            >
              Quick Start
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <Link
              href="/docs/architecture"
              className="inline-flex items-center gap-2 px-8 py-3.5 text-sm font-medium rounded-full border border-[var(--border)] hover:border-[var(--accent-mauve)] transition-all text-foreground hover:bg-[rgba(255,255,255,0.03)]"
              style={{ backdropFilter: 'blur(10px)' }}
            >
              View Architecture
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.65 }}
            className="mt-14 inline-flex items-center gap-3 px-5 py-3 rounded-xl border border-[var(--border)] font-mono text-sm"
            style={{
              background: 'rgba(0, 0, 0, 0.4)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <span className="flex gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[var(--accent-peach)] opacity-80" />
              <span className="w-2.5 h-2.5 rounded-full bg-[var(--accent-mauve)] opacity-80" />
              <span className="w-2.5 h-2.5 rounded-full bg-[var(--accent-purple)] opacity-80" />
            </span>
            <span className="text-muted-foreground">$</span>
            <span className="text-foreground">pip install flux-cli-ai</span>
            <span className="ml-1 inline-block w-2 h-4 bg-[var(--accent-peach)] animate-pulse" />
          </motion.div>
        </div>
      </section>

      {/* Animated Divider */}
      <div className="relative h-px max-w-5xl mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[var(--border)] to-transparent" />
        <motion.div
          initial={{ x: '-100%' }}
          whileInView={{ x: '100%' }}
          viewport={{ once: true }}
          transition={{ duration: 2, ease: 'easeInOut' }}
          className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-[var(--accent-peach)] to-transparent"
        />
      </div>

      {/* Features Grid */}
      <section className="relative py-28 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="text-center mb-20"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[var(--border)] text-[11px] font-medium text-muted-foreground uppercase tracking-wider mb-5"
              style={{ background: 'rgba(255, 255, 255, 0.02)' }}
            >
              <Sparkles className="w-3 h-3 text-[var(--accent-peach)]" />
              Core Capabilities
            </motion.div>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-5">
              Everything you need in an{' '}
              <span className="gradient-text">AI coding agent</span>
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Composable architecture focused on extensibility, safety, and developer experience.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <PremiumFeatureCard key={feature.title} {...feature} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* Stats Band */}
      <section className="relative py-20 px-6 border-y border-[var(--border)]">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'linear-gradient(180deg, transparent, color-mix(in srgb, var(--accent-purple) 5%, transparent), transparent)',
          }}
        />
        <div className="max-w-6xl mx-auto relative">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '11+', label: 'Built-in Tools' },
              { value: 'MCP', label: 'Protocol Native' },
              { value: '<100ms', label: 'First Token' },
              { value: 'MIT', label: 'Open Source' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Getting Started CTA */}
      <section className="relative py-28 px-4 sm:px-6 overflow-hidden">
        <div className="max-w-5xl mx-auto relative">
          <div className="absolute inset-0 -z-10">
            <div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full opacity-20 blur-3xl"
              style={{
                background:
                  'radial-gradient(circle, var(--accent-purple), transparent 60%)',
                animation: 'pulse-ring 4s ease-in-out infinite',
              }}
            />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="relative rounded-3xl overflow-hidden"
          >
            <div
              className="absolute -inset-[1px] rounded-3xl"
              style={{
                background:
                  'linear-gradient(var(--border-angle, 0deg), var(--accent-purple), var(--accent-mauve), var(--accent-peach), var(--accent-purple))',
                animation: 'border-rotate 6s linear infinite',
              }}
            />

            <div
              className="relative p-10 sm:p-16 text-center rounded-3xl"
              style={{
                background:
                  'linear-gradient(135deg, color-mix(in srgb, var(--card-bg) 90%, var(--accent-purple) 10%), var(--card-bg))',
                backdropFilter: 'blur(20px)',
              }}
            >
              <div className="absolute inset-0 dot-pattern opacity-10 [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />

              <div className="relative">
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{
                    type: 'spring',
                    stiffness: 200,
                    damping: 15,
                    delay: 0.2,
                  }}
                  className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[var(--accent-purple)] to-[var(--accent-mauve)] mb-6 shadow-lg shadow-[var(--accent-purple)]/30"
                >
                  <Zap className="w-7 h-7 text-[var(--accent-ivory)]" />
                </motion.div>

                <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                  Ready to <span className="gradient-text">get started</span>?
                </h2>
                <p className="text-muted-foreground mb-10 max-w-xl mx-auto text-lg leading-relaxed">
                  Install Flux-CLI and start building with AI-powered assistance
                  in minutes.
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                  <Link
                    href="/docs/installation"
                    className="shine-button group inline-flex items-center gap-2 px-8 py-3.5 text-sm font-bold rounded-full bg-[var(--accent-purple)] text-[var(--accent-ivory)] hover:bg-[var(--accent-mauve)] transition-colors shadow-xl shadow-[var(--accent-purple)]/30"
                  >
                    Installation Guide
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                  <Link
                    href="/docs/cli-commands"
                    className="inline-flex items-center gap-2 px-8 py-3.5 text-sm font-medium rounded-full border border-[var(--border)] hover:border-[var(--accent-mauve)] transition-all text-foreground hover:bg-[rgba(255,255,255,0.03)]"
                  >
                    CLI Reference
                  </Link>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-14 px-4 sm:px-6 border-t border-[var(--border)]">
        <div
          className="absolute inset-0 pointer-events-none opacity-40"
          style={{
            background:
              'linear-gradient(0deg, transparent, color-mix(in srgb, var(--accent-purple) 3%, transparent))',
          }}
        />
        <div className="max-w-7xl mx-auto relative">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-[var(--accent-purple)] blur-md opacity-50" />
                <Sparkles className="relative w-4 h-4 text-[var(--accent-peach)]" />
              </div>
              <span className="text-sm font-bold text-foreground tracking-wide">
                Flux-CLI
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--card-bg)] border border-[var(--border)] text-muted-foreground font-medium">
                MIT
              </span>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-x-7 gap-y-3">
              {[
                { href: '/docs/introduction', label: 'Documentation' },
                {
                  href: 'https://github.com/manmit-s/flux-cli',
                  label: 'GitHub',
                  external: true,
                },
                { href: '/docs/contributing', label: 'Contributing' },
                { href: '/docs/license', label: 'License' },
              ].map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  target={link.external ? '_blank' : undefined}
                  rel={link.external ? 'noopener noreferrer' : undefined}
                  className="group relative text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.label}
                  <span className="absolute -bottom-1 left-0 w-0 h-px bg-[var(--accent-peach)] group-hover:w-full transition-all duration-300" />
                </Link>
              ))}
            </div>
          </div>
          <div className="mt-10 pt-6 border-t border-[var(--border)] text-center">
            <p className="text-xs text-muted-foreground">
              © 2025 Flux-CLI. Crafted with care for developers.
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}