"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import RecruiterNavbar from "@/components/layout/RecruiterNavbar";
import {
  getJobDetails,
  getJobApplications,
  downloadResumePdf,
  updateApplicationStatus,
  RecruiterJob,
  JobApplicationItem,
} from "@/services/recruiterService";

export default function JobApplicationsPage() {
  const params = useParams();
  const jobId = params?.id as string;

  const [job, setJob] = useState<RecruiterJob | null>(null);
  const [applications, setApplications] = useState<JobApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters & Pagination
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalApps, setTotalApps] = useState<number>(0);

  // Fetch Job details
  useEffect(() => {
    if (!jobId) return;

    const fetchJob = async () => {
      try {
        const jobData = await getJobDetails(jobId);
        setJob(jobData);
      } catch (err: any) {
        setError(err?.message || "Failed to load job details.");
      }
    };

    fetchJob();
  }, [jobId]);

  // Fetch Applications
  const fetchApplications = useCallback(async () => {
    if (!jobId) return;
    setLoading(true);
    setError(null);

    try {
      const data = await getJobApplications(jobId, page, 10, statusFilter);
      setApplications(data.items || []);
      setTotalPages(data.total_pages || 1);
      setTotalApps(data.total || 0);
    } catch (err: any) {
      setError(err?.message || "Failed to load applications.");
    } finally {
      setLoading(false);
    }
  }, [jobId, page, statusFilter]);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  // Download Resume Handler
  const handleDownloadResume = async (appId: string, filename: string) => {
    setDownloadingId(appId);
    setError(null);
    try {
      await downloadResumePdf(appId, filename || `resume_${appId}.pdf`);
    } catch (err: any) {
      setError(err?.message || "Failed to download resume.");
    } finally {
      setDownloadingId(null);
    }
  };

  // Status Update Handler
  const handleStatusChange = async (
    appId: string,
    newStatus: "submitted" | "under_review" | "shortlisted" | "interview" | "rejected"
  ) => {
    setActionLoadingId(appId);
    setError(null);
    setSuccessMessage(null);

    try {
      await updateApplicationStatus(appId, newStatus);
      setSuccessMessage(`Application status updated to ${newStatus.replace("_", " ")}.`);
      setTimeout(() => setSuccessMessage(null), 3000);

      // Optimistically update local application state
      setApplications((prev) =>
        prev.map((app) => (app.id === appId ? { ...app, status: newStatus } : app))
      );
    } catch (err: any) {
      setError(err?.message || "Failed to update application status.");
      // Refetch to sync with server state
      fetchApplications();
    } finally {
      setActionLoadingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "submitted":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 border border-blue-200 dark:border-blue-800/60">
            <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
            Submitted
          </span>
        );
      case "under_review":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 dark:bg-amber-950/60 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
            Under Review
          </span>
        );
      case "shortlisted":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-purple-50 px-2.5 py-0.5 text-xs font-semibold text-purple-700 dark:bg-purple-950/60 dark:text-purple-400 border border-purple-200 dark:border-purple-800/60">
            <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
            Shortlisted
          </span>
        );
      case "interview":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Interview
          </span>
        );
      case "rejected":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700 dark:bg-rose-950/60 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
            Rejected
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center rounded-full bg-zinc-100 px-2.5 py-0.5 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
            {status}
          </span>
        );
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 flex flex-col">
        <RecruiterNavbar />

        <main className="flex-1 mx-auto max-w-7xl w-full px-4 py-8 sm:px-6 lg:px-8">
          {/* Breadcrumb & Navigation */}
          <div className="mb-6 flex items-center justify-between">
            <Link
              href="/jobs"
              className="inline-flex items-center gap-2 text-xs font-medium text-zinc-500 hover:text-indigo-600 dark:text-zinc-400 dark:hover:text-indigo-400 transition-colors"
            >
              <span>←</span> Back to All Jobs
            </Link>
          </div>

          {/* Job Overview Banner */}
          <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-xs dark:border-zinc-800 dark:bg-zinc-900 mb-8">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-3 mb-2">
                  <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                    {job ? job.title : "Loading Job..."}
                  </h1>
                  {job && (
                    <span className="capitalize rounded-full bg-zinc-100 px-2.5 py-0.5 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                      {job.status}
                    </span>
                  )}
                </div>

                {job && (
                  <div className="flex flex-wrap items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400">
                    {job.location && (
                      <span className="flex items-center gap-1">
                        📍 <span className="capitalize">{job.location}</span>
                      </span>
                    )}
                    {job.deadline && (
                      <span className="flex items-center gap-1">
                        ⏰ Deadline: {job.deadline}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      📅 Posted: {new Date(job.created_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-100 dark:border-indigo-900/50 px-4 py-2.5 text-center">
                  <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                    {totalApps}
                  </div>
                  <div className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400">
                    Total Applications
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Notifications */}
          {error && (
            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-400">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700 dark:border-emerald-900/60 dark:bg-emerald-950/40 dark:text-emerald-400">
              {successMessage}
            </div>
          )}

          {/* Status Filters Toolbar */}
          <div className="bg-white dark:bg-zinc-900 p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs mb-6 flex flex-wrap items-center gap-1.5">
            {[
              { id: "all", label: "All" },
              { id: "submitted", label: "Submitted" },
              { id: "under_review", label: "Under Review" },
              { id: "shortlisted", label: "Shortlisted" },
              { id: "interview", label: "Interview" },
              { id: "rejected", label: "Rejected" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setStatusFilter(tab.id);
                  setPage(1);
                }}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  statusFilter === tab.id
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Applications List */}
          {loading ? (
            <div className="grid gap-4">
              {[1, 2, 3].map((n) => (
                <div
                  key={n}
                  className="animate-pulse rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900"
                >
                  <div className="h-5 w-40 rounded bg-zinc-200 dark:bg-zinc-800 mb-3" />
                  <div className="h-4 w-60 rounded bg-zinc-100 dark:bg-zinc-800/60 mb-4" />
                  <div className="h-8 w-32 rounded bg-zinc-200 dark:bg-zinc-800" />
                </div>
              ))}
            </div>
          ) : applications.length === 0 ? (
            /* Empty State */
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-300 bg-white py-16 px-4 text-center dark:border-zinc-800 dark:bg-zinc-900">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400 mb-4">
                📄
              </div>
              <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
                No applications found
              </h3>
              <p className="mt-1 max-w-sm text-sm text-zinc-500 dark:text-zinc-400">
                {statusFilter !== "all"
                  ? `No applications currently in '${statusFilter.replace("_", " ")}' stage.`
                  : "No candidates have applied to this job posting yet."}
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {applications.map((app) => {
                const candidate = app.candidate;
                const resume = app.resume;
                const isActionLoading = actionLoadingId === app.id;
                const isDownloading = downloadingId === app.id;

                return (
                  <div
                    key={app.id}
                    className="rounded-xl border border-zinc-200 bg-white p-6 transition-all hover:border-zinc-300 hover:shadow-sm dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      {/* Candidate Details */}
                      <div className="space-y-2.5 flex-1">
                        <div className="flex flex-wrap items-center gap-3">
                          <h3 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
                            {candidate?.full_name || "Anonymous Applicant"}
                          </h3>
                          {getStatusBadge(app.status)}
                        </div>

                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-600 dark:text-zinc-400">
                          {candidate?.email && (
                            <a
                              href={`mailto:${candidate.email}`}
                              className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                            >
                              ✉ {candidate.email}
                            </a>
                          )}
                          {candidate?.phone && (
                            <a
                              href={`tel:${candidate.phone}`}
                              className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                            >
                              📞 {candidate.phone}
                            </a>
                          )}
                          {candidate?.linkedin_url && (
                            <a
                              href={
                                candidate.linkedin_url.startsWith("http")
                                  ? candidate.linkedin_url
                                  : `https://${candidate.linkedin_url}`
                              }
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-indigo-600 hover:underline dark:text-indigo-400 font-medium"
                            >
                              LinkedIn ↗
                            </a>
                          )}
                          {candidate?.github_url && (
                            <a
                              href={
                                candidate.github_url.startsWith("http")
                                  ? candidate.github_url
                                  : `https://${candidate.github_url}`
                              }
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-indigo-600 hover:underline dark:text-indigo-400 font-medium"
                            >
                              GitHub ↗
                            </a>
                          )}
                          <span className="text-zinc-400 dark:text-zinc-500">
                            Submitted: {new Date(app.created_at).toLocaleString()}
                          </span>
                        </div>

                        {app.message && (
                          <div className="mt-2 rounded-lg bg-zinc-50 p-3 text-xs text-zinc-700 dark:bg-zinc-800/60 dark:text-zinc-300 border border-zinc-200/60 dark:border-zinc-700/60">
                            <span className="font-semibold text-zinc-900 dark:text-zinc-200">Note:</span>{" "}
                            {app.message}
                          </div>
                        )}
                      </div>

                      {/* Resume Download & Actions */}
                      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0 pt-2 md:pt-0">
                        {/* Download Resume Button */}
                        <button
                          onClick={() =>
                            handleDownloadResume(app.id, resume?.file_name || "resume.pdf")
                          }
                          disabled={isDownloading}
                          className="flex items-center justify-center gap-2 rounded-lg border border-zinc-300 bg-white px-3.5 py-2 text-xs font-semibold text-zinc-800 shadow-xs hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:bg-zinc-700 transition-colors"
                        >
                          {isDownloading ? (
                            <>
                              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
                              Downloading...
                            </>
                          ) : (
                            <>
                              <span>📄</span> Download Resume
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Status Workflow Action Bar */}
                    <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800/80 flex flex-wrap items-center justify-between gap-3">
                      <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
                        Workflow Actions:
                      </span>

                      <div className="flex flex-wrap items-center gap-2">
                        {/* SUBMITTED actions */}
                        {app.status === "submitted" && (
                          <>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "under_review")}
                              className="rounded-md bg-amber-50 border border-amber-200 px-3 py-1 text-xs font-semibold text-amber-800 hover:bg-amber-100 dark:bg-amber-950/60 dark:border-amber-800 dark:text-amber-300 transition-colors disabled:opacity-50"
                            >
                              ➡️ Move to Under Review
                            </button>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "rejected")}
                              className="rounded-md bg-rose-50 border border-rose-200 px-3 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:bg-rose-950/60 dark:border-rose-800 dark:text-rose-400 transition-colors disabled:opacity-50"
                            >
                              ✕ Reject
                            </button>
                          </>
                        )}

                        {/* UNDER_REVIEW actions */}
                        {app.status === "under_review" && (
                          <>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "shortlisted")}
                              className="rounded-md bg-purple-50 border border-purple-200 px-3 py-1 text-xs font-semibold text-purple-800 hover:bg-purple-100 dark:bg-purple-950/60 dark:border-purple-800 dark:text-purple-300 transition-colors disabled:opacity-50"
                            >
                              ⭐ Shortlist Candidate
                            </button>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "rejected")}
                              className="rounded-md bg-rose-50 border border-rose-200 px-3 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:bg-rose-950/60 dark:border-rose-800 dark:text-rose-400 transition-colors disabled:opacity-50"
                            >
                              ✕ Reject
                            </button>
                          </>
                        )}

                        {/* SHORTLISTED actions */}
                        {app.status === "shortlisted" && (
                          <>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "interview")}
                              className="rounded-md bg-emerald-50 border border-emerald-200 px-3 py-1 text-xs font-semibold text-emerald-800 hover:bg-emerald-100 dark:bg-emerald-950/60 dark:border-emerald-800 dark:text-emerald-300 transition-colors disabled:opacity-50"
                            >
                              🎙️ Invite to Interview
                            </button>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "rejected")}
                              className="rounded-md bg-rose-50 border border-rose-200 px-3 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:bg-rose-950/60 dark:border-rose-800 dark:text-rose-400 transition-colors disabled:opacity-50"
                            >
                              ✕ Reject
                            </button>
                          </>
                        )}

                        {/* INTERVIEW actions */}
                        {app.status === "interview" && (
                          <>
                            <button
                              disabled={isActionLoading}
                              onClick={() => handleStatusChange(app.id, "rejected")}
                              className="rounded-md bg-rose-50 border border-rose-200 px-3 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:bg-rose-950/60 dark:border-rose-800 dark:text-rose-400 transition-colors disabled:opacity-50"
                            >
                              ✕ Reject
                            </button>
                          </>
                        )}

                        {/* REJECTED */}
                        {app.status === "rejected" && (
                          <span className="text-xs text-zinc-400 dark:text-zinc-500 italic">
                            Application closed (Rejected)
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex items-center justify-between border-t border-zinc-200 dark:border-zinc-800 pt-4">
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                Showing page <span className="font-semibold">{page}</span> of{" "}
                <span className="font-semibold">{totalPages}</span> ({totalApps} total applications)
              </p>

              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1 || loading}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="rounded-lg border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                >
                  Previous
                </button>
                <button
                  disabled={page >= totalPages || loading}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="rounded-lg border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
