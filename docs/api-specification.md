# API Specification

## Overview

The Resume Screening AI System exposes RESTful APIs for three user roles:

- **Public Applicant** – View published job postings and submit job applications.
- **Recruiter** – Register, manage job postings, review applications, view AI evaluation results, and export reports.
- **Administrator** – Manage recruiter accounts and monitor the platform. Administrators cannot access applications, resumes, applicants, or AI evaluation results.

All protected endpoints require JWT Bearer Authentication.

---

# Authentication

## POST /api/auth/recruiters/register

### Purpose

Register a new recruiter account.

### Authentication Required

No

### Request

```json
{
  "name": "John Doe",
  "email": "john@company.com",
  "password": "password123",
  "company": "ABC Technologies"
}
```

### Response

```json
{
  "message": "Recruiter registered successfully"
}
```

### Status Codes

- 201 Created
- 400 Bad Request
- 409 Conflict
- 500 Internal Server Error

---

## POST /api/auth/recruiters/login

### Purpose

Authenticate a recruiter.

### Authentication Required

No

### Request

```json
{
  "email": "john@company.com",
  "password": "password123"
}
```

### Response

```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "Bearer"
}
```

### Status Codes

- 200 OK
- 401 Unauthorized
- 500 Internal Server Error

---

## POST /api/auth/admin/login

### Purpose

Authenticate an administrator.

### Authentication Required

No

### Request

```json
{
  "email": "admin@system.com",
  "password": "password123"
}
```

### Response

```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "Bearer"
}
```

### Status Codes

- 200 OK
- 401 Unauthorized
- 500 Internal Server Error

---

## POST /api/auth/logout

### Purpose

Logout the current user.

### Authentication Required

Yes

### Response

```json
{
  "message": "Logged out successfully"
}
```

### Status Codes

- 200 OK
- 401 Unauthorized

---

# Public APIs

## GET /api/public/jobs

### Purpose

Retrieve all published job postings.

### Authentication Required

No

### Query Parameters

| Parameter | Description |
|-----------|-------------|
| page | Page number |
| limit | Records per page |
| search | Search by job title |
| company | Filter by company |

### Response

```json
{
  "data": [],
  "page": 1,
  "limit": 10,
  "total": 25,
  "total_pages": 3
}
```

### Status Codes

- 200 OK

---

## GET /api/public/jobs/{jobId}

### Purpose

Retrieve a published job posting.

### Authentication Required

No

### Response

```json
{
  "id": "uuid",
  "title": "Backend Developer",
  "description": "...",
  "company": "ABC Technologies",
  "deadline": "2026-08-15",
  "application_url": "https://resume-ai.com/jobs/abc123",
  "qr_code": "base64_encoded_image"
}
```

### Status Codes

- 200 OK
- 404 Not Found

---

## POST /api/jobs/{jobId}/applications

### Purpose

Submit a job application.

### Authentication Required

No

### Request

**multipart/form-data**

- full_name
- email
- phone
- linkedin_url
- github_url
- resume_file

### Response

```json
{
  "application_id": "uuid",
  "message": "Application submitted successfully"
}
```

### Status Codes

- 201 Created
- 400 Bad Request
- 404 Job Not Found

---

# Recruiter APIs

## POST /api/jobs

### Purpose

Create a new job posting.

A newly created job is saved with **DRAFT** status.

### Authentication Required

Recruiter

### Status Codes

- 201 Created
- 400 Bad Request

---

## GET /api/jobs

### Purpose

Retrieve all job postings created by the logged-in recruiter.

### Authentication Required

Recruiter

### Query Parameters

- status
- page
- limit

### Response

```json
{
  "data": [],
  "page": 1,
  "limit": 10,
  "total": 12,
  "total_pages": 2
}
```

### Status Codes

- 200 OK

---

## GET /api/jobs/{jobId}

### Purpose

Retrieve one of the recruiter's job postings.

### Authentication Required

Recruiter

### Status Codes

- 200 OK
- 404 Not Found

---

## PUT /api/jobs/{jobId}

### Purpose

Update a job posting.

### Authentication Required

Recruiter

### Status Codes

- 200 OK
- 404 Not Found

---

## PATCH /api/jobs/{jobId}/status

### Purpose

Update the job status.

### Allowed Values

- DRAFT
- PUBLISHED
- CLOSED

### Authentication Required

Recruiter

### Request

```json
{
  "status": "PUBLISHED"
}
```

### Status Codes

- 200 OK
- 400 Bad Request

---

## DELETE /api/jobs/{jobId}

### Purpose

Soft delete a job posting.

Changes the status to **DELETED**.

### Authentication Required

Recruiter

### Status Codes

- 200 OK
- 404 Not Found

---

## GET /api/jobs/{jobId}/applications

### Purpose

Retrieve applications submitted for a job posting.

### Authentication Required

Recruiter

### Query Parameters

- status
- page
- limit

### Response

```json
{
  "data": [],
  "page": 1,
  "limit": 10,
  "total": 100,
  "total_pages": 10
}
```

### Status Codes

- 200 OK

---

## GET /api/jobs/{jobId}/evaluations

### Purpose

Retrieve AI evaluation results for a job posting.

### Authentication Required

Recruiter

### Query Parameters

- score_min
- score_max
- page
- limit

### Response

```json
{
  "data": [
    {
      "application_id": "uuid",
      "score": 94.5,
      "matching_skills": [
        "Python",
        "FastAPI"
      ],
      "missing_skills": [
        "AWS",
        "Redis"
      ]
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 50,
  "total_pages": 5
}
```

### Status Codes

- 200 OK

---

## GET /api/applications/{applicationId}/evaluation

### Purpose

Retrieve the detailed AI evaluation for an application.

### Authentication Required

Recruiter

### Status Codes

- 200 OK
- 404 Not Found

---

## PATCH /api/applications/{applicationId}/status

### Purpose

Update the recruitment status of an application.

### Allowed Values

- SHORTLISTED
- REJECTED

### Authentication Required

Recruiter

### Request

```json
{
  "status": "SHORTLISTED"
}
```

### Status Codes

- 200 OK
- 404 Not Found

---

## GET /api/applications/{applicationId}/resume

### Purpose

Download the submitted resume.

### Authentication Required

Recruiter

### Response

PDF File

### Status Codes

- 200 OK
- 404 Not Found

---

## GET /api/jobs/{jobId}/export

### Purpose

Export applications and evaluation results as a CSV file.

### Authentication Required

Recruiter

### Query Parameters

- status
- score_min
- score_max

### Response

CSV File

### Status Codes

- 200 OK

---

### Status Codes

- 202 Accepted

---

## GET /api/dashboard

### Purpose

Retrieve recruiter dashboard statistics.

### Authentication Required

Recruiter

### Response

```json
{
  "total_jobs": 12,
  "published_jobs": 8,
  "closed_jobs": 4,
  "total_applications": 145,
  "shortlisted": 18,
  "rejected": 75
}
```

### Status Codes

- 200 OK

---

# Administrator APIs

Administrators manage recruiter accounts and monitor the platform.

Administrators **cannot access applicants, resumes, applications, or AI evaluation results.**

---

## GET /api/admin/recruiters

### Purpose

Retrieve all recruiter accounts.

### Authentication Required

Administrator

### Status Codes

- 200 OK

---

## GET /api/admin/recruiters/{recruiterId}

### Purpose

Retrieve recruiter details.

### Authentication Required

Administrator

### Status Codes

- 200 OK
- 404 Not Found

---

## PUT /api/admin/recruiters/{recruiterId}

### Purpose

Update recruiter information.

### Authentication Required

Administrator

### Status Codes

- 200 OK

---

## PATCH /api/admin/recruiters/{recruiterId}/status

### Purpose

Activate or deactivate a recruiter account.

### Request

```json
{
  "is_active": false
}
```

### Authentication Required

Administrator

### Status Codes

- 200 OK

---

## GET /api/admin/dashboard

### Purpose

Retrieve platform statistics.

### Authentication Required

Administrator

### Response

```json
{
  "total_recruiters": 40,
  "active_recruiters": 35,
  "inactive_recruiters": 5,
  "total_jobs": 180,
  "published_jobs": 95,
  "closed_jobs": 60
}
```

### Status Codes

- 200 OK