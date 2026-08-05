'use client'

import { motion } from 'motion/react'

const FLUX_ASCII = [
  '██╗    ███████╗██╗     ██╗   ██╗██╗  ██╗',
  '╚██╗   ██╔════╝██║     ██║   ██║╚██╗██╔╝',
  ' ╚██╗  █████╗  ██║     ██║   ██║ ╚███╔╝ ',
  ' ██╔╝  ██╔══╝  ██║     ██║   ██║ ██╔██╗ ',
  '██╔╝   ██║     ███████╗╚██████╔╝██╔╝ ██╗',
  '╚═╝    ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝',
]

const GRADIENT_COLORS = [
  '#884d90ff',  // deep purple
  '#c76f9dff',  // muted mauve
  '#F6DBC0',  // warm peach / cream
  '#F8F4E9',  // off-white / ivory
  '#c66fd1ff',  // deep purple
]

function interpolateColor(colors: string[], factor: number): string {
  if (factor <= 0) return colors[0]
  if (factor >= 1) return colors[colors.length - 1]

  const numSegments = colors.length - 1
  const segment = factor * numSegments
  const idx = Math.min(Math.floor(segment), numSegments - 1)
  const t = segment - idx

  const hexToRgb = (hex: string) => {
    const h = hex.replace('#', '')
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]
  }

  const rgbToHex = (r: number, g: number, b: number) =>
    `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`

  const [r1, g1, b1] = hexToRgb(colors[idx])
  const [r2, g2, b2] = hexToRgb(colors[idx + 1])

  const r = Math.round(r1 + (r2 - r1) * t)
  const g = Math.round(g1 + (g2 - g1) * t)
  const b = Math.round(b1 + (b2 - b1) * t)

  return rgbToHex(r, g, b)
}

interface AsciiLogoProps {
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

export function AsciiLogo({ size = 'md', animated = true }: AsciiLogoProps) {
  const fontSize =
    size === 'sm'
      ? 'text-[8px] sm:text-xs'
      : size === 'lg'
        ? 'text-[10px] sm:text-base md:text-lg'
        : 'text-[9px] sm:text-sm'
  const maxLen = Math.max(...FLUX_ASCII.map((l) => l.length))

  return (
    <div className={`font-mono ${fontSize} leading-tight`}>
      {FLUX_ASCII.map((line, lineIdx) => (
        <div key={lineIdx} className="whitespace-pre">
          {Array.from(line).map((char, charIdx) => {
            const factor = charIdx / Math.max(1, maxLen - 1)
            const color = interpolateColor(GRADIENT_COLORS, factor)

            if (animated) {
              return (
                <motion.span
                  key={`${lineIdx}-${charIdx}`}
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    delay: lineIdx * 0.05 + charIdx * 0.005,
                    duration: 0.3,
                    ease: 'easeOut',
                  }}
                  style={{ color, fontWeight: 700 }}
                >
                  {char}
                </motion.span>
              )
            }

            return (
              <span key={`${lineIdx}-${charIdx}`} style={{ color, fontWeight: 700 }}>
                {char}
              </span>
            )
          })}
        </div>
      ))}
    </div>
  )
}
