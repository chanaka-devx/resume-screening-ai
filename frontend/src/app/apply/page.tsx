"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

interface JobSummary {
  id: string;
  title: string;
  location: string | null;
  deadline: string | null;
}

function ApplyContent() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get("job_id");

  // Job state
  const [job, setJob] = useState<JobSummary | null>(null);

  // Form inputs
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);

  // Process & UI state
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Fetch job details if job_id is present
  useEffect(() => {
    if (!jobId) return;

    const fetchJob = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/v1/public/jobs/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          setJob(data);
        }
      } catch {
        // non-blocking
      }
    };

    fetchJob();
  }, [jobId, apiUrl]);

  // Main Form Submit Handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!jobId) {
      setError("No job selected. Please select a job from the listings.");
      return;
    }

    if (!file) {
      setError("Please upload your resume in PDF format.");
      return;
    }

    setSubmitting(true);
    setStatusMessage("Uploading resume...");

    try {
      // Step 1: Upload Resume to R2 and DB
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch(`${apiUrl}/api/v1/resumes/upload`, {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadRes.json();
      if (!uploadRes.ok) {
        throw new Error(uploadData?.detail || "Failed to upload resume.");
      }

      const applicantId = uploadData.applicant?.id;
      const resumeId = uploadData.resume?.id;

      if (!applicantId || !resumeId) {
        throw new Error("Invalid response received from server.");
      }

      // Step 2: Update applicant details with the user-entered ones
      setStatusMessage("Saving applicant details...");
      const patchRes = await fetch(
        `${apiUrl}/api/v1/resumes/applicant/${applicantId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            full_name: fullName,
            email: email,
            phone: phone || null,
          }),
        }
      );

      if (!patchRes.ok) {
        const patchData = await patchRes.json();
        throw new Error(
          patchData?.detail || "Failed to update applicant details."
        );
      }

      // Step 3: Submit final application
      setStatusMessage("Submitting application...");
      const appRes = await fetch(`${apiUrl}/api/v1/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobId,
          resume_id: resumeId,
          message: message.trim() || null,
        }),
      });

      const appData = await appRes.json();
      if (!appRes.ok) {
        throw new Error(appData?.detail || "Failed to submit application.");
      }

      setIsSuccess(true);
    } catch (err: any) {
      setError(err?.message || "An unexpected error occurred.");
    } finally {
      setSubmitting(false);
      setStatusMessage(null);
    }
  };

  if (isSuccess) {
    return (
      <div className="mx-auto max-w-xl py-12">
        <div className="rounded-2xl border border-zinc-200 bg-white p-8 text-center shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-green-100 text-green-600 dark:bg-green-950/60 dark:text-green-400">
            <svg
              className="h-8 w-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
            Application Submitted!
          </h2>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            Thank you, <strong className="text-zinc-900 dark:text-zinc-100">{fullName}</strong>.
            Your application for{" "}
            <strong className="text-zinc-900 dark:text-zinc-100">
              {job?.title || "the selected position"}
            </strong>{" "}
            has been successfully received and our AI screening system is evaluating your resume.
          </p>

          <div className="mt-8 flex justify-center gap-3">
            <Link
              href="/"
              className="rounded-xl bg-zinc-900 px-6 py-2.5 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
            >
              Browse More Jobs
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl py-8">
      {/* Job Summary Banner */}
      {job && (
        <div className="mb-6 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Applying for
          </span>
          <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
            {job.title}
          </h2>
          {job.location && (
            <span className="mt-1 inline-block text-xs font-medium text-zinc-600 dark:text-zinc-400">
              📍 {job.location}
            </span>
          )}
        </div>
      )}

      {/* Main Application Form */}
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 sm:p-8">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
          Job Application
        </h1>
        <p className="mt-1 mb-6 text-sm text-zinc-600 dark:text-zinc-400">
          Please fill in your contact information and upload your resume.
        </p>

        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/50 dark:text-red-400">
            {error}
          </div>
        )}

        {statusMessage && (
          <div className="mb-6 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700 dark:border-blue-900 dark:bg-blue-950/50 dark:text-blue-300">
            {statusMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="fullName"
              className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
            >
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              id="fullName"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. John Doe"
              className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3.5 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
          </div>

          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
              >
                Email Address <span className="text-red-500">*</span>
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3.5 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>

            <div>
              <label
                htmlFor="phone"
                className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
              >
                Contact Number <span className="text-red-500">*</span>
              </label>
              <input
                id="phone"
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3.5 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="message"
              className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
            >
              Cover Note / Message <span className="text-xs text-zinc-400">(optional)</span>
            </label>
            <textarea
              id="message"
              rows={3}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Tell us why you're a great fit for this position..."
              className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3.5 py-2 text-sm text-zinc-900 shadow-sm focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            />
          </div>

          <div>
            <label
              htmlFor="resume"
              className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
            >
              Upload Resume (PDF) <span className="text-red-500">*</span>
            </label>
            <div className="mt-1 flex justify-center rounded-xl border-2 border-dashed border-zinc-300 px-6 py-6 dark:border-zinc-700">
              <div className="text-center">
                <svg
                  className="mx-auto h-10 w-10 text-zinc-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="mt-2 flex text-sm text-zinc-600 dark:text-zinc-400">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer font-medium text-zinc-900 underline hover:text-zinc-700 dark:text-zinc-100"
                  >
                    <span>{file ? "Change file" : "Select a PDF file"}</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      accept=".pdf,application/pdf"
                      className="sr-only"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setFile(e.target.files[0]);
                        }
                      }}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                  PDF up to 5MB
                </p>
                {file && (
                  <div className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-zinc-100 px-2.5 py-1 text-xs font-semibold text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200">
                    📄 {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </div>
                )}
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-xl bg-zinc-900 py-3 text-sm font-semibold text-white shadow-sm hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 cursor-pointer disabled:cursor-not-allowed"
          >
            {submitting ? (statusMessage || "Submitting Application...") : "Submit Application"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function ApplyPage() {
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

      <main className="px-4">
        <Suspense fallback={<div className="py-20 text-center text-sm">Loading application form...</div>}>
          <ApplyContent />
        </Suspense>
      </main>
    </div>
  );
}
