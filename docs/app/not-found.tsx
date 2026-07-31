import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-6xl font-bold text-flux-purple mb-4">404</div>
        <h1 className="text-2xl font-bold text-foreground mb-2">Page Not Found</h1>
        <p className="text-muted-foreground mb-8">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link
          href="/"
          className="px-6 py-3 text-sm font-semibold rounded-xl bg-gradient-to-r from-flux-purple via-flux-slate to-flux-cyan text-white hover:opacity-90 transition-opacity inline-block"
        >
          Return Home
        </Link>
      </div>
    </main>
  )
}
