import { createMDX } from 'fumadocs-mdx/next'
import type { NextConfig } from 'next'

const withMDX = createMDX()

const config: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  basePath: '/flux-cli',
  assetPrefix: '/flux-cli/',
  // Required for static export
  trailingSlash: true,
}

export default withMDX(config)
