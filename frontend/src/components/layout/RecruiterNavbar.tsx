"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function RecruiterNavbar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_type");
    router.push("/auth");
  };

  const isJobsTab = pathname.startsWith("/jobs");

  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/95 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/95">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-8">
          <Link href="/jobs" className="flex items-center gap-2.5 group">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 font-bold text-white shadow-sm transition-transform group-hover:scale-105">
              R
            </div>
            <span className="text-lg font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
              Resume Screening <span className="text-indigo-600 dark:text-indigo-400">AI</span>
            </span>
          </Link>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1">
            <Link
              href="/jobs"
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                isJobsTab
                  ? "bg-zinc-100 text-indigo-600 dark:bg-zinc-800 dark:text-indigo-400 font-semibold"
                  : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-zinc-100"
              }`}
            >
              Jobs
            </Link>
            <Link
              href="/"
              target="_blank"
              className="rounded-md px-3 py-1.5 text-sm font-medium text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-zinc-100"
            >
              Public Board ↗
            </Link>
          </nav>
        </div>

        {/* User / Logout */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs text-zinc-600 dark:border-zinc-800 dark:bg-zinc-800/60 dark:text-zinc-300">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Recruiter Portal
          </div>

          <button
            onClick={handleLogout}
            className="rounded-md border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-100 hover:text-zinc-900 transition-colors dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white"
          >
            Log Out
          </button>
        </div>
      </div>
    </header>
  );
}
