import { getPage, getPages } from '@/lib/source'
import defaultMdxComponents from 'fumadocs-ui/mdx'
import { Callout } from '@/components/callout'
import { FeatureCard } from '@/components/feature-card'
import { MermaidDiagram } from '@/components/mermaid-diagram'
import { CodeExample } from '@/components/code-example'
import { AsciiLogo } from '@/components/ascii-logo'
import { GradientBanner } from '@/components/gradient-banner'
import { CopyButton } from '@/components/copy-button'
import type { Metadata } from 'next'
import { DocsPage } from 'fumadocs-ui/page'
import { notFound } from 'next/navigation'

export default async function Page({ params }: { params: Promise<{ slug?: string[] }> }) {
  const resolvedParams = await params
  const slug = resolvedParams.slug ?? ['introduction']
  const page = getPage(slug)

  if (!page) {
    notFound()
  }

  const MDX = page.data.body

  return (
    <DocsPage
      toc={page.data.toc}
      breadcrumb={{
        enabled: true,
        includePage: true,
      }}
      tableOfContent={{
        enabled: true,
        style: 'clerk',
      }}
    >
      <MDX components={{ ...defaultMdxComponents, Callout, FeatureCard, MermaidDiagram, CodeExample, AsciiLogo, GradientBanner, CopyButton }} />
    </DocsPage>
  )
}

export async function generateStaticParams() {
  return getPages().map((page) => ({
    slug: page.slugs,
  }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug?: string[] }> }) {
  const resolvedParams = await params
  const slug = resolvedParams.slug ?? ['introduction']
  const page = getPage(slug)

  if (!page) return {}

  return {
    title: page.data.title,
    description: page.data.description,
  } satisfies Metadata
}
