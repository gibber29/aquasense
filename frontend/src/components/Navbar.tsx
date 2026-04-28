"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export function Droplet() {
  return (
    <span className="inline-flex h-7 w-7 items-center justify-center text-[28px] leading-none drop-shadow-sm">💧</span>
  );
}

export default function Navbar() {
  const router = useRouter();
  const logout = () => {
    localStorage.removeItem("aquasense_token");
    router.push("/login");
  };
  return (
    <header className="h-[86px] border-b border-[#dbe3ee] bg-white">
      <nav className="mx-auto flex h-full max-w-[1620px] items-center justify-between px-8">
        <Link href="/dashboard" className="flex items-center gap-4 text-[26px] font-bold text-[#1261ad]">
          <Droplet />
          <span>AquaSense</span>
        </Link>
        <div className="hidden items-center gap-8 md:flex">
          <Link className="nav-link" href="/dashboard">Dashboard</Link>
          <Link className="nav-link" href="/dashboard#log">Log Usage</Link>
          <Link className="nav-link" href="/history">History</Link>
          <Link className="nav-link" href="/dashboard#predictions">Predictions</Link>
          <Link className="nav-link" href="/dashboard#cost">Cost Estimator</Link>
          <Link className="nav-link" href="/chatbot">Profile</Link>
          <button onClick={logout} className="nav-link text-[#e21b2d]">Logout</button>
        </div>
      </nav>
    </header>
  );
}
