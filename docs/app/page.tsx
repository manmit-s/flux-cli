'use client'

import { motion } from 'motion/react'
import {
  Bot,
  Braces,
  GitBranch,
  Hammer,
  Layers,
  Shield,
  Terminal,
  Zap,
} from 'lucide-react'
import Link from 'next/link'
import { AsciiLogo } from '@/components/ascii-logo'
import { FeatureCard } from '@/components/feature-card'

const features = [
  {
    icon: Bot,
    title: 'Multi-Turn Agent Loop',
    description:
      'Sophisticated reasoning engine that autonomously plans, executes tools, and iteratively refines solutions through multiple turns of intelligent decision-making.',
  },
  {
    icon: Braces,
    title: '11 Built-in Tools',
    description:
      'Read, write, edit files, execute shell commands, search code, browse the web, manage tasks, and store persistent memory — all through a unified tool interface.',
  },
  {
    icon: Layers,
    title: 'MCP Integration',
    description:
      'Model Context Protocol support with stdio and SSE transports. Connect external servers and extend the agent with custom capabilities seamlessly.',
  },
  {
    icon: Shield,
    title: 'Safety & Approval',
    description:
      'Configurable approval policies from fully automatic (YOLO) to strict confirmation. Smart detection of dangerous commands and path validation built in.',
  },
  {
    icon: GitBranch,
    title: 'Lifecycle Hooks',
    description:
      'Shell-based event triggers for every stage — before/after agent, tool execution, and error handling. Extend and integrate with your existing workflows.',
  },
  {
    icon: Zap,
    title: 'Streaming Responses',
    description:
      'Real-time token streaming with incremental tool call events. Live Markdown rendering and syntax-highlighted output in a beautiful Rich-powered TUI.',
  },
  {
    icon: Hammer,
    title: 'Context Compression',
    description:
      'Intelligent conversation history management with automatic compression at 80% context window. Tool output pruning keeps the most relevant information accessible.',
  },
  {
    icon: Terminal,
    title: 'Sub-Agent Delegation',
    description:
      'Spawn specialized sub-agents for codebase investigation and code review. Isolated context and focused tool access for complex multi-step tasks.',
  },
]

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Navigation */}
      <div className="fixed top-6 inset-x-0 z-50 flex justify-center px-6 pointer-events-none">
        <nav className="pointer-events-auto bg-surface-50/80 backdrop-blur-xl border border-surface-300/50 rounded-full px-6 h-14 flex items-center justify-between gap-12 shadow-2xl">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-sm font-bold text-flux-purple tracking-wide">Flux-CLI</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/docs/introduction" className="text-sm font-medium text-muted-foreground hover:text-flux-purple transition-colors">
              Docs
            </Link>
            <Link
              href="https://github.com/manmit-s/flux-cli"
              className="text-sm font-medium text-muted-foreground hover:text-flux-purple transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </Link>
            <Link
              href="/docs/quick-start"
              className="px-5 py-2.5 text-sm font-bold rounded-full bg-flux-purple text-black hover:opacity-90 transition-all duration-200"
            >
              Get Started
            </Link>
          </div>
        </nav>
      </div>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 hero-glow">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <AsciiLogo size="lg" />
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-8 text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed"
          >
            A powerful agentic AI coding CLI built from scratch with Python and
            Rich TUI — inspired by Claude Code CLI and Gemini CLI. Featuring
            multi-tool orchestration, streaming responses, and a plugin
            architecture.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-4"
          >
            <Link
              href="/docs/quick-start"
              className="px-8 py-3 text-sm font-bold rounded-full bg-flux-purple text-black hover:opacity-90 transition-colors shadow-lg shadow-flux-purple/20"
            >
              Quick Start →
            </Link>
            <Link
              href="/docs/architecture"
              className="px-8 py-3 text-sm font-medium rounded-full bg-surface-200 border border-surface-300/50 hover:bg-surface-300/50 hover:border-flux-purple/30 transition-all"
            >
              View Architecture
            </Link>
            <Link
              href="https://github.com/manmit-s/flux-cli"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3 text-sm font-medium rounded-full bg-surface-200 border border-surface-300/50 hover:bg-surface-300/50 hover:border-flux-purple/30 transition-all"
            >
              GitHub →
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-flux-purple mb-4">
              Everything You Need in an AI Coding Agent
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Built from the ground up with a focus on extensibility, safety,
              and developer experience.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <FeatureCard key={feature.title} {...feature} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* Getting Started Section */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="bg-surface/30 border border-surface-300/30 rounded-3xl p-12 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-flux-purple mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
              Install Flux-CLI and start building with AI-powered assistance
              in minutes.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/docs/installation"
                className="px-8 py-3 text-sm font-bold rounded-full bg-flux-purple text-black hover:opacity-90 transition-colors shadow-lg shadow-flux-purple/20"
              >
                Installation Guide
              </Link>
              <Link
                href="/docs/cli-commands"
                className="px-8 py-3 text-sm font-medium rounded-full bg-surface-300/50 hover:bg-surface-400/50 transition-colors border border-surface-300/50"
              >
                CLI Reference
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-surface-300/30">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-flux-purple tracking-wide">Flux-CLI</span>
            <span className="text-sm text-muted-foreground">— MIT License</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/docs/introduction" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Documentation
            </Link>
            <Link
              href="https://github.com/manmit-s/flux-cli"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </Link>
            <Link href="/docs/contributing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Contributing
            </Link>
            <Link href="/docs/license" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              License
            </Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
