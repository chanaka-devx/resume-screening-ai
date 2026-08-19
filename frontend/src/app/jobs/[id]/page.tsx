"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface JobDetails {
  id: string;
  title: string;
  description: string;
  location: "on-site" | "hybrid" | "remote" | null;
  deadline: string | null;
  posted_at: string;
}

export default function JobDetailsPage() {
  const params = useParams();
  const id = params?.id as string;

  const [job, setJob] = useState<JobDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchJob = async () => {
      setLoading(true);
      setError(null);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/api/v1/public/jobs/${id}`);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data?.detail || "Failed to load job details.");
        }

        setJob(data);
      } catch (err: any) {
        setError(err?.message || "An unexpected error occurred.");
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
  }, [id]);

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      {/* Header / Navbar */}
      <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
          <Link href="/" className="text-xl font-bold tracking-tight">
            Resume Screening AI
          </Link>
          <Link
            href="/auth"
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            Recruiter Portal
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-4xl px-4 py-8">
        {/* Back Link */}
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
          >
            ← Back to all jobs
          </Link>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="py-20 text-center text-sm text-zinc-500 dark:text-zinc-400">
            Loading job details...
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900 dark:bg-red-950/50">
            <h2 className="text-lg font-semibold text-red-800 dark:text-red-300">
              Unable to load job
            </h2>
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
            <div className="mt-4">
              <Link
                href="/"
                className="inline-flex rounded-lg bg-red-800 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 dark:bg-red-900 dark:hover:bg-red-800"
              >
                Browse other openings
              </Link>
            </div>
          </div>
        )}

        {/* Job Detail Card */}
        {!loading && !error && job && (
          <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 sm:p-8">
            {/* Title & Actions */}
            <div className="flex flex-col justify-between gap-4 border-b border-zinc-200 pb-6 dark:border-zinc-800 sm:flex-row sm:items-center">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-3xl">
                  {job.title}
                </h1>
                <div className="mt-2.5 flex flex-wrap items-center gap-3 text-sm text-zinc-500 dark:text-zinc-400">
                  {job.location && (
                    <span className="inline-flex items-center rounded-md bg-zinc-100 px-2.5 py-0.5 text-xs font-semibold uppercase text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200">
                      {job.location}
                    </span>
                  )}
                  {job.deadline && (
                    <span>
                      Deadline: {new Date(job.deadline).toLocaleDateString()}
                    </span>
                  )}
                  <span>•</span>
                  <span>
                    Posted on {new Date(job.posted_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <Link
                href={`/apply?job_id=${job.id}`}
                className="inline-flex items-center justify-center rounded-xl bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
              >
                Apply for this Job
              </Link>
            </div>

            {/* Description Section */}
            <div className="pt-6">
              <h2 className="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                Job Description
              </h2>
              <div className="prose prose-zinc dark:prose-invert max-w-none whitespace-pre-wrap text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                {job.description}
              </div>
            </div>

            {/* Bottom Apply CTA */}
            <div className="mt-10 border-t border-zinc-200 pt-6 dark:border-zinc-800 flex justify-end">
              <Link
                href={`/apply?job_id=${job.id}`}
                className="rounded-xl bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
              >
                Apply for this Job
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
