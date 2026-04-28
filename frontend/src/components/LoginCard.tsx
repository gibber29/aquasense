"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Droplet } from "@/components/Navbar";

export default function LoginCard({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [city, setCity] = useState("Delhi");
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      if (mode === "register") {
        await api.register({ name, email, password, city });
      }
      const result = await api.login(email, password);
      localStorage.setItem("aquasense_token", result.access_token);
      router.push("/dashboard");
    } catch {
      setError(mode === "login" ? "Invalid email or password. Register an account first if you are new." : "Registration failed. Try a different email.");
    }
  };

  return (
    <form onSubmit={submit} className="login-panel mx-auto mt-[61px] w-[496px] max-w-[calc(100vw-32px)] px-[30px] pb-[34px] pt-[31px]">
      <div className="mb-[37px] text-center">
        <div className="flex items-center justify-center gap-4 text-[36px] font-semibold text-[#1261ad]">
          <Droplet />
          <span>AquaSense</span>
        </div>
        <p className="mt-3 text-[21px] text-slate-600">Monitor. Predict. Conserve.</p>
      </div>
      <div className="space-y-[27px]">
        {mode === "register" && (
          <>
            <label className="block">
              <span className="mb-3 block text-[15px] font-bold uppercase tracking-[1px] text-slate-600">Name</span>
              <input className="field" value={name} onChange={(event) => setName(event.target.value)} required />
            </label>
            <label className="block">
              <span className="mb-3 block text-[15px] font-bold uppercase tracking-[1px] text-slate-600">City</span>
              <input className="field" value={city} onChange={(event) => setCity(event.target.value)} required />
            </label>
          </>
        )}
        <label className="block">
          <span className="mb-3 block text-[15px] font-bold uppercase tracking-[1px] text-slate-600">Email Address</span>
          <input className="field" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label className="block">
          <span className="mb-3 block text-[15px] font-bold uppercase tracking-[1px] text-slate-600">Password</span>
          <input className="field bg-white" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        <button className="blue-button w-full" type="submit">{mode === "login" ? "Log In" : "Register"}</button>
        {error && <p className="text-sm font-semibold text-red-600">{error}</p>}
      </div>
      <p className="mt-[31px] text-center text-[20px] text-slate-600">
        {mode === "login" ? "Don't have an account? " : "Already have an account? "}
        <a className="text-[#2d84df]" href={mode === "login" ? "/register" : "/login"}>
          {mode === "login" ? "Register here" : "Log in"}
        </a>
      </p>
    </form>
  );
}
