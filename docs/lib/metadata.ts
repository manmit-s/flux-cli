import type { Metadata } from 'next'

export const siteConfig = {
  name: 'Flux-CLI',
  description:
    'A powerful agentic AI coding CLI built with Python and Rich TUI — featuring multi-tool orchestration, streaming responses, sub-agent delegation, MCP server integration, and safety approval policies.',
  url: 'https://manmit-s.github.io/flux-cli/docs',
  ogImage: 'https://manmit-s.github.io/flux-cli/og-image.png',
  author: 'Manmit',
  links: {
    github: 'https://github.com/manmit-s/flux-cli',
  },
}

export const defaultMetadata: Metadata = {
  title: {
    default: 'Flux-CLI — AI Agentic Coding CLI',
    template: '%s | Flux-CLI',
  },
  description: siteConfig.description,
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: siteConfig.url,
    siteName: siteConfig.name,
    title: 'Flux-CLI — AI Agentic Coding CLI',
    description: siteConfig.description,
    images: [
      {
        url: siteConfig.ogImage,
        width: 1200,
        height: 630,
        alt: siteConfig.name,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Flux-CLI — AI Agentic Coding CLI',
    description: siteConfig.description,
    images: [siteConfig.ogImage],
  },
  robots: {
    index: true,
    follow: true,
  },
}
