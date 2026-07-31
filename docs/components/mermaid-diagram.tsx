'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'motion/react'

interface MermaidDiagramProps {
  chart: string
  title?: string
  caption?: string
}

export function MermaidDiagram({ chart, title, caption }: MermaidDiagramProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const renderMermaid = async () => {
      if (!ref.current) return
      try {
        const mermaid = (await import('mermaid')).default
        mermaid.initialize({
          theme: 'dark',
          themeVariables: {
            primaryColor: '#1c1c26',
            primaryTextColor: '#e2e8f0',
            primaryBorderColor: '#2e2e3a',
            lineColor: '#8bcefc',
            secondaryColor: '#111118',
            tertiaryColor: '#0a0a0f',
            fontFamily: 'var(--font-inter), system-ui, sans-serif',
            fontSize: '14px',
            edgeLabelBackground: '#1c1c26',
          },
          sequence: {
            showSequenceNumbers: true,
          },
        })

        const { svg } = await mermaid.render('mermaid-' + Math.random().toString(36).slice(2), chart)
        if (ref.current) {
          ref.current.innerHTML = svg
        }
      } catch (error) {
        console.error('Mermaid rendering error:', error)
        if (ref.current) {
          ref.current.innerHTML = `<pre class="text-red-400 text-sm p-4 bg-surface-200 rounded-lg border border-red-500/30">Failed to render diagram. Please verify the Mermaid syntax.</pre>`
        }
      }
    }

    renderMermaid()
  }, [chart])

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="my-8"
    >
      {title && <h3 className="text-lg font-semibold text-foreground mb-3">{title}</h3>}
      <div className="glass-card p-6 overflow-x-auto">
        <div ref={ref} className="mermaid flex justify-center" />
      </div>
      {caption && <p className="text-sm text-muted-foreground mt-2 text-center">{caption}</p>}
    </motion.div>
  )
}
