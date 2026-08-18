"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface LoginFormProps {
  onSwitchToSignup?: () => void;
}

export default function LoginForm({ onSwitchToSignup }: LoginFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Login failed. Please check your credentials.");
      }

      if (data?.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("token_type", data.token_type || "bearer");
      }

      setSuccess("Login successful! Redirecting...");
      setTimeout(() => {
        router.push("/dashboard");
      }, 1000);
    } catch (err: any) {
      setError(err?.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <h2 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-zinc-50">
        Welcome Back
      </h2>
      <p className="mb-6 text-sm text-zinc-600 dark:text-zinc-400">
        Enter your credentials to access your recruiter account.
      </p>

      {error && (
        <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-700 border border-red-200 dark:bg-red-950/50 dark:text-red-400 dark:border-red-900">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 rounded bg-green-50 p-3 text-sm text-green-700 border border-green-200 dark:bg-green-950/50 dark:text-green-400 dark:border-green-900">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="login-email"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
          >
            Email Address
          </label>
          <input
            id="login-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="recruiter@company.com"
            className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>

        <div>
          <label
            htmlFor="login-password"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
          >
            Password
          </label>
          <input
            id="login-password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="mt-1 block w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 cursor-pointer disabled:cursor-not-allowed"
        >
          {loading ? "Logging in..." : "Log In"}
        </button>
      </form>

      {onSwitchToSignup && (
        <div className="mt-6 text-center text-sm text-zinc-600 dark:text-zinc-400">
          Don&apos;t have an account?{" "}
          <button
            type="button"
            onClick={onSwitchToSignup}
            className="font-medium text-zinc-900 underline hover:text-zinc-700 dark:text-zinc-100 dark:hover:text-zinc-300 cursor-pointer"
          >
            Sign up
          </button>
        </div>
      )}
    </div>
  );
}
