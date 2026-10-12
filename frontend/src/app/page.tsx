"use client";
import Link from "next/link";

export default function LaunchPage() {
  return (
    <main className="relative min-h-dvh flex items-center justify-center text-white">
      <div className="text-center space-y-6">
        <h1 className="text-4xl md:text-6xl font-semibold tracking-wide">天文agent</h1>
        <p className="text-white/80">探索宇宙，从这里开始</p>
        <Link
          href="/home"
          className="inline-flex items-center rounded-md bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 text-sm font-medium transition shadow"
        >
          进入首页
        </Link>
      </div>
    </main>
  );
}
