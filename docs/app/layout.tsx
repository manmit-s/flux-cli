import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import 'fumadocs-ui/style.css'
import './global.css'
import { defaultMetadata } from '@/lib/metadata'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

import { RootProvider } from 'fumadocs-ui/provider/next'
import { basePath } from '@/lib/base-path'

export const metadata: Metadata = defaultMetadata

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/flux-cli/favicon.ico" sizes="any" />
      </head>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased bg-background`}>
        <RootProvider
          search={{
            options: {
              type: 'static',
              api: `${basePath}/api/search`,
            },
          }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  )
}
