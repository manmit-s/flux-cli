import { AlertCircle, AlertTriangle, Info, Lightbulb } from 'lucide-react'

interface CalloutProps {
  type?: 'info' | 'warning' | 'error' | 'tip'
  title?: string
  children: React.ReactNode
}

const styles = {
  info: {
    icon: Info,
    border: 'border-flux-blue/30',
    bg: 'bg-flux-blue/5',
    text: 'text-flux-blue',
    accent: '#8bcefc',
  },
  warning: {
    icon: AlertTriangle,
    border: 'border-flux-slate/30',
    bg: 'bg-flux-slate/5',
    text: 'text-flux-slate',
    accent: '#a191f8',
  },
  error: {
    icon: AlertCircle,
    border: 'border-red-500/30',
    bg: 'bg-red-500/5',
    text: 'text-red-400',
    accent: '#f43f5e',
  },
  tip: {
    icon: Lightbulb,
    border: 'border-flux-purple/30',
    bg: 'bg-flux-purple/5',
    text: 'text-flux-purple',
    accent: '#e7aafb',
  },
}

export function Callout({ type = 'info', title, children }: CalloutProps) {
  const style = styles[type]
  const Icon = style.icon

  return (
    <div className={`my-6 rounded-xl border ${style.border} ${style.bg} overflow-hidden`}>
      <div className="flex items-start gap-3 p-4">
        <Icon className={`w-5 h-5 mt-0.5 ${style.text} shrink-0`} />
        <div className="min-w-0">
          {title && <p className={`text-sm font-semibold mb-1 ${style.text}`}>{title}</p>}
          <div className="text-sm text-foreground/80 leading-relaxed">{children}</div>
        </div>
      </div>
    </div>
  )
}
