import { fetchWithAuth } from "./api";

export interface RecruiterJob {
  id: string;
  recruiter_id: string;
  title: string;
  description: string;
  location: "on-site" | "hybrid" | "remote" | null;
  deadline: string | null;
  status: "draft" | "published" | "closed" | "deleted";
  created_at: string;
  updated_at: string;
}

export interface RecruiterJobListResponse {
  items: RecruiterJob[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface CandidateInfo {
  id: string;
  full_name: string;
  email: string;
  phone: string | null;
  linkedin_url: string | null;
  github_url: string | null;
}

export interface ApplicationResumeInfo {
  id: string;
  file_name: string;
  file_path: string;
}

export interface JobApplicationItem {
  id: string;
  job_id: string;
  resume_id: string;
  message: string | null;
  status: "submitted" | "under_review" | "shortlisted" | "interview" | "rejected";
  created_at: string;
  updated_at: string;
  candidate: CandidateInfo;
  resume: ApplicationResumeInfo;
}

export interface JobApplicationListResponse {
  items: JobApplicationItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ── Fetch recruiter jobs ─────────────────────────────────────────────────────
export async function getRecruiterJobs(
  page: number = 1,
  limit: number = 10,
  statusFilter?: string,
  search?: string
): Promise<RecruiterJobListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });

  if (statusFilter && statusFilter !== "all") {
    params.append("status", statusFilter);
  }

  if (search && search.trim()) {
    params.append("search", search.trim());
  }

  const response = await fetchWithAuth(`/api/v1/jobs?${params.toString()}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail || "Failed to fetch jobs.");
  }

  return data;
}

// ── Fetch single job details ─────────────────────────────────────────────────
export async function getJobDetails(jobId: string): Promise<RecruiterJob> {
  const response = await fetchWithAuth(`/api/v1/jobs/${jobId}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail || "Failed to load job details.");
  }

  return data;
}

// ── Fetch applications for a job ─────────────────────────────────────────────
export async function getJobApplications(
  jobId: string,
  page: number = 1,
  limit: number = 10,
  statusFilter?: string
): Promise<JobApplicationListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });

  if (statusFilter && statusFilter !== "all") {
    params.append("status", statusFilter);
  }

  const response = await fetchWithAuth(
    `/api/v1/jobs/${jobId}/applications?${params.toString()}`
  );
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail || "Failed to fetch applications.");
  }

  return data;
}

// ── Download candidate resume PDF ────────────────────────────────────────────
export async function downloadResumePdf(
  applicationId: string,
  defaultFilename: string = "resume.pdf"
): Promise<void> {
  const response = await fetchWithAuth(
    `/api/v1/applications/${applicationId}/resume`
  );

  if (!response.ok) {
    let errorMsg = "Failed to download resume.";
    try {
      const data = await response.json();
      errorMsg = data?.detail || errorMsg;
    } catch {
      // binary response or not json
    }
    throw new Error(errorMsg);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = downloadUrl;
  anchor.download = defaultFilename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  window.URL.revokeObjectURL(downloadUrl);
}

// ── Update application status ────────────────────────────────────────────────
export async function updateApplicationStatus(
  applicationId: string,
  newStatus: "submitted" | "under_review" | "shortlisted" | "interview" | "rejected"
): Promise<any> {
  const response = await fetchWithAuth(
    `/api/v1/applications/${applicationId}/status`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status: newStatus }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.detail || "Failed to update application status.");
  }

  return data;
}
