import Link from 'next/link';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col relative w-full overflow-x-hidden">
      {/* Background Hero Elements */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[10%] -right-[10%] w-[60%] h-[60%] bg-[var(--primary-container)]/5 rounded-full blur-[120px]"></div>
        <div className="absolute top-[40%] -left-[10%] w-[40%] h-[50%] bg-[var(--secondary-container)]/5 rounded-full blur-[100px]"></div>
      </div>

      {/* Top Navigation */}
      <header className="relative z-50 flex justify-between items-center px-6 h-20 w-full">
        <div className="flex items-center gap-2">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8 text-[var(--primary)]">
            <circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
          </svg>
          <span className="font-display text-xl font-bold tracking-tight text-[var(--primary)]">TripVerse AI</span>
        </div>
      </header>

      {/* Main Form Content */}
      <main className="relative z-10 flex-grow flex items-center justify-center px-6 py-16">
        {children}
      </main>

      {/* Footer */}
      <footer className="w-full py-2 px-8 mt-auto border-t border-[var(--outline-variant)]/20 bg-white/50 backdrop-blur-sm z-50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 py-6">
          <div className="text-xs text-[var(--on-surface-variant)] uppercase tracking-widest">
            © 2024 TripVerse AI. Intelligent Serenity in Travel.
          </div>
          <div className="flex gap-6">
            <Link href="#" className="text-xs text-[var(--outline)] hover:text-[var(--primary)] transition-colors">Privacy</Link>
            <Link href="#" className="text-xs text-[var(--outline)] hover:text-[var(--primary)] transition-colors">Terms</Link>
            <Link href="#" className="text-xs text-[var(--outline)] hover:text-[var(--primary)] transition-colors">Support</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
