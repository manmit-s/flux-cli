import { searchAPI } from '@/lib/search'

export const revalidate = false
export const dynamic = 'force-static'

export const GET = searchAPI.staticGET
