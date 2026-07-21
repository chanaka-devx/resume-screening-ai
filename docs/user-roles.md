# User Roles

## Overview

The Resume Screening AI System supports three types of users:

- Recruiter
- Administrator
- Public Applicant

Each role has specific responsibilities and access permissions to ensure secure and controlled access to the system.

---

# Recruiter

Recruiters are responsible for creating job postings, reviewing applicants, and managing the recruitment process.

## Permissions

### Authentication

- Register a recruiter account
- Login
- Logout

### Job Management

- Create job postings
- Edit own job postings
- View own job postings
- Change job status (Draft, Published, Closed)
- Soft delete own job postings

### Application Management

- View applications submitted to their job postings
- View applicant information for their job postings
- Download submitted resumes
- Update application status
  - Shortlisted
  - Rejected

### AI Evaluation

- View AI evaluation results
- View matching skills
- View missing skills
- View AI-generated explanations

### Reports

- Export application and evaluation results as CSV
- View recruiter dashboard statistics

## Restrictions

Recruiters cannot:

- Manage other recruiter accounts
- Access other recruiters' job postings
- Access administrator features
- Modify AI models or evaluation logic
- Change system configuration

---

# Administrator

Administrators manage the platform and recruiter accounts.

## Permissions

### Recruiter Management

- View all recruiter accounts
- View recruiter details
- Update recruiter information
- Activate or deactivate recruiter accounts

### Platform Management

- View all job postings
- View platform dashboard and statistics

## Restrictions

Administrators cannot:

- View applicants
- View applications
- Download resumes
- View AI evaluation results
- Change application status
- Submit applications on behalf of applicants

---

# Public Applicant

Applicants do not create accounts or log into the system.

They interact with the platform through public endpoints.

## Permissions

- View published job postings
- View job posting details
- Apply for published job postings
- Upload a resume during application submission

## Restrictions

Applicants cannot:

- Create an account
- Login
- Edit submitted applications
- Replace uploaded resumes
- View application status
- View AI evaluation results
- View recruiter information

---

# Permission Matrix

| Feature | Public Applicant | Recruiter | Administrator |
|---------|------------------|-----------|---------------|
| Register Recruiter | ✗ | ✓ | ✗ |
| Login | ✗ | ✓ | ✓ |
| View Published Jobs | ✓ | ✓ | ✓ |
| Apply for Job | ✓ | ✗ | ✗ |
| Create Job Posting | ✗ | ✓ | ✗ |
| Edit Job Posting | ✗ | ✓ | ✗ |
| Publish / Close Job | ✗ | ✓ | ✗ |
| Delete Job Posting | ✗ | ✓ | ✗ |
| View Own Job Postings | ✗ | ✓ | ✗ |
| View Applications | ✗ | ✓ | ✗ |
| View Applicants | ✗ | ✓ | ✗ |
| Download Resume | ✗ | ✓ | ✗ |
| View AI Evaluations | ✗ | ✓ | ✗ |
| Update Application Status | ✗ | ✓ | ✗ |
| Export CSV | ✗ | ✓ | ✗ |
| View Recruiter Dashboard | ✗ | ✓ | ✗ |
| View Recruiters | ✗ | ✗ | ✓ |
| Update Recruiters | ✗ | ✗ | ✓ |
| Activate/Deactivate Recruiters | ✗ | ✗ | ✓ |
| View Platform Dashboard | ✗ | ✗ | ✓ |
| View All Job Postings | ✗ | ✗ | ✓ |
| View Applications | ✗ | ✓ | ✗ |
| View AI Results | ✗ | ✓ | ✗ |

---

# Authentication Summary

| Endpoint | Authentication |
|----------|----------------|
| Recruiter Register | None |
| Recruiter Login | None |
| Admin Login | None |
| Public Job APIs | None |
| Submit Application | None |
| Recruiter APIs | Recruiter JWT |
| Administrator APIs | Administrator JWT |

---

# Role Summary

## Recruiter

Owns the recruitment process by creating job postings, reviewing applicants, managing applications, and making hiring decisions based on AI-assisted evaluations.

## Administrator

Maintains the platform by managing recruiter accounts and monitoring overall system activity without accessing confidential applicant or evaluation data.

## Public Applicant

Can browse published job opportunities and submit applications with a resume but does not have access to authenticated features or recruitment outcomes.