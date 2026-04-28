export default function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-aqua-50">
      <main className="flex-1 pt-px">{children}</main>
      <footer className="pb-7 text-center text-[15px] font-semibold uppercase tracking-[1.2px] text-slate-500">
        <span className="mr-2 text-lg">💧</span>AquaSense — Monitor. Predict. Conserve.
      </footer>
    </div>
  );
}
