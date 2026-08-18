"use client";

import { useState } from "react";
import LoginForm from "./login";
import SignupForm from "./signup";

export default function AuthPage() {
  const [isSignUp, setIsSignUp] = useState(false);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-100 p-4 dark:bg-zinc-900">
      <div className="w-full max-w-md overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        {/* Navigation Tabs */}
        <div className="flex border-b border-zinc-200 bg-zinc-50/50 p-1.5 dark:border-zinc-800 dark:bg-zinc-900/50">
          <button
            type="button"
            onClick={() => setIsSignUp(false)}
            className={`flex-1 rounded-xl py-2 text-sm font-medium transition-all duration-300 cursor-pointer ${
              !isSignUp
                ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-800 dark:text-zinc-50"
                : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
            }`}
          >
            Log In
          </button>
          <button
            type="button"
            onClick={() => setIsSignUp(true)}
            className={`flex-1 rounded-xl py-2 text-sm font-medium transition-all duration-300 cursor-pointer ${
              isSignUp
                ? "bg-white text-zinc-900 shadow-sm dark:bg-zinc-800 dark:text-zinc-50"
                : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200"
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Sliding Forms Container */}
        <div className="relative overflow-hidden">
          <div
            className={`flex w-[200%] transition-transform duration-500 ease-in-out ${
              isSignUp ? "-translate-x-1/2" : "translate-x-0"
            }`}
          >
            {/* Left Panel: Login */}
            <div className="w-1/2 flex-shrink-0 p-6">
              <LoginForm onSwitchToSignup={() => setIsSignUp(true)} />
            </div>

            {/* Right Panel: Signup */}
            <div className="w-1/2 flex-shrink-0 p-6">
              <SignupForm onSwitchToLogin={() => setIsSignUp(false)} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
