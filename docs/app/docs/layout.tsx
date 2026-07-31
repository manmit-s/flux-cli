import { DocsLayout } from 'fumadocs-ui/layouts/docs'
import type { ReactNode } from 'react'
import { pageTree } from '@/lib/source'

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={pageTree}
      nav={{
        title: 'Flux-CLI',
        transparentMode: 'top',
      }}
      sidebar={{
        defaultOpenLevel: 1,
      }}
      themeSwitch={{
        enabled: true,
      }}
    >
      {children}
    </DocsLayout>
  )
}
