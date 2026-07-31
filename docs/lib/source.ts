import { docs, meta } from '../.source/server'
import { loader } from 'fumadocs-core/source'
import { toFumadocsSource } from 'fumadocs-mdx/runtime/server'

export const { getPage, getPages, pageTree } = loader({
  baseUrl: '/docs',
  source: toFumadocsSource(docs, meta),
})
