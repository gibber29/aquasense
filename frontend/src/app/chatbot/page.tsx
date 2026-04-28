"use client";

import { FormEvent, useState } from "react";
import { Bot, Send } from "lucide-react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

type Message = { role: "user" | "bot"; text: string };

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", text: "Hi, I am AquaBot. Ask why usage spiked, what tomorrow may look like, or how to lower your bill." }
  ]);
  const [loading, setLoading] = useState(false);

  const send = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const message = String(form.get("message") || "").trim();
    if (!message) return;
    setMessages((items) => [...items, { role: "user", text: message }]);
    event.currentTarget.reset();
    setLoading(true);
    try {
      const result = await api.chat(message);
      setMessages((items) => [...items, { role: "bot", text: result.answer }]);
    } catch {
      setMessages((items) => [...items, { role: "bot", text: "I need you to log in first so I can read your AquaSense data." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <main className="mx-auto max-w-[900px] px-6 pb-32 pt-8">
        <div className="metric-card overflow-hidden">
          <div className="flex items-center gap-3 bg-[#3b8edb] p-5 text-white">
            <div className="flex h-12 w-12 animate-pulse items-center justify-center rounded-full bg-white/20"><Bot /></div>
            <div><h1 className="text-2xl font-bold">AquaBot</h1><p className="text-sm text-blue-50">Context-aware conservation assistant</p></div>
          </div>
          <div className="h-[520px] space-y-4 overflow-y-auto bg-aqua-50 p-5">
            {messages.map((message, index) => (
              <div key={index} className={`max-w-[75%] rounded-lg p-4 shadow-panel ${message.role === "user" ? "ml-auto bg-[#3b8edb] text-white" : "bg-white text-slate-700"}`}>
                {message.text}
              </div>
            ))}
            {loading && <div className="w-fit rounded-lg bg-white p-4 shadow-panel">Thinking...</div>}
          </div>
          <form onSubmit={send} className="flex gap-3 border-t bg-white p-4">
            <input name="message" className="h-12 flex-1 rounded-md border px-4" placeholder="Why was my usage high yesterday?" />
            <button className="flex h-12 w-12 items-center justify-center rounded-md bg-[#3b8edb] text-white" aria-label="Send"><Send size={20} /></button>
          </form>
        </div>
      </main>
    </AppShell>
  );
}
