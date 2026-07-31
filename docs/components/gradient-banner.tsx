'use client'

import { motion } from 'motion/react'

interface GradientBannerProps {
  children: React.ReactNode
  className?: string
}

export function GradientBanner({ children, className = '' }: GradientBannerProps) {
  return (
    <div className={`relative overflow-hidden rounded-2xl ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-flux-purple/10 via-flux-slate/10 to-flux-cyan/10" />
      <div className="absolute top-0 -left-32 w-64 h-64 bg-flux-purple/20 rounded-full blur-3xl" />
      <div className="absolute bottom-0 -right-32 w-64 h-64 bg-flux-cyan/20 rounded-full blur-3xl" />
      <div className="relative z-10 p-8 md:p-12">{children}</div>
    </div>
  )
}

export function AnimatedGradientBanner({ children, className = '' }: GradientBannerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`relative overflow-hidden rounded-2xl ${className}`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-flux-purple/10 via-flux-slate/10 to-flux-cyan/10" />
      <motion.div
        className="absolute top-0 -left-32 w-64 h-64 bg-flux-purple/20 rounded-full blur-3xl"
        animate={{ x: [0, 30, 0], y: [0, -20, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-0 -right-32 w-64 h-64 bg-flux-cyan/20 rounded-full blur-3xl"
        animate={{ x: [0, -30, 0], y: [0, 20, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div className="relative z-10 p-8 md:p-12">{children}</div>
    </motion.div>
  )
}
