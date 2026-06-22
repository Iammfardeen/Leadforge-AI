export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex items-center justify-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent font-mono text-sm font-bold text-white">
            L
          </div>
          <span className="text-sm font-medium text-ink">LeadForge AI</span>
        </div>
        {children}
      </div>
    </div>
  );
}
