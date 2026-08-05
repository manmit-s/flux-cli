'use client'

import { useState } from 'react'
import { Check, Copy, Terminal } from 'lucide-react'
import { motion } from 'motion/react'

interface CodeExampleProps {
  code: string
  language?: string
  title?: string
  description?: string
  output?: string
  showLineNumbers?: boolean
}

export function CodeExample({
  code,
  language = 'bash',
  title,
  description,
  output,
}: CodeExampleProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="my-6 rounded-xl overflow-hidden border border-surface-300/50 bg-surface/30 backdrop-blur-sm"
    >
      {title && (
        <div className="flex items-center gap-2 px-4 py-2 border-b border-surface-300/30 bg-surface-50/50">
          <Terminal className="w-4 h-4 text-flux-blue" />
          <span className="text-sm text-muted-foreground font-medium">{title}</span>
        </div>
      )}

      {description && (
        <div className="px-4 py-3 border-b border-surface-300/20">
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      )}

      <div className="relative group">
<button
          onClick={handleCopy}
          className="absolute top-3 right-3 p-2 rounded-lg bg-surface-300/70 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-all duration-200 hover:bg-surface-400/50 z-10"
          aria-label="Copy code"
        >
          {copied ? (
            <Check className="w-4 h-4 text-flux-green" />
          ) : (
            <Copy className="w-4 h-4 text-muted-foreground" />
          )}
        </button>
        <pre className="p-4 overflow-x-auto text-sm leading-relaxed">
          <code className={`language-${language} text-foreground`}>{code}</code>
        </pre>
      </div>

      {output && (
        <div className="border-t border-surface-300/30">
          <div className="px-4 py-2 bg-surface-50/30">
            <span className="text-xs text-muted-foreground font-medium">Output</span>
          </div>
          <pre className="p-4 text-sm text-flux-green overflow-x-auto">{output}</pre>
        </div>
      )}
    </motion.div>
  )
}
