import Navbar from "@/components/Navbar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-aqua-50">
      <Navbar />
      <div className="flex-1">{children}</div>
      <footer className="pb-7 text-center text-[15px] font-semibold uppercase tracking-[1.2px] text-slate-500">
        <span className="mr-2 text-lg">💧</span>AquaSense — Monitor. Predict. Conserve.
      </footer>
      <a
        aria-label="Open AquaBot"
        href="/chatbot"
        className="fixed bottom-8 right-8 flex h-[70px] w-[70px] items-center justify-center rounded-full bg-[#348cdd] text-[30px] shadow-lg transition hover:scale-105"
      >
        💧
      </a>
    </div>
  );
}
