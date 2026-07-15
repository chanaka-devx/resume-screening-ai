# Functional Requirements

FR-01
Users can upload PDF resumes.

FR-02
The system extracts text from uploaded resumes.

FR-03
The system identifies skills, education, and experience.

FR-04
Recruiters can upload a job description.

FR-05
The system compares resumes against the job description.

FR-06
The system calculates a relevance score for each candidate based on the uploaded job description.

FR-07
Only authenticated recruiters can view candidate rankings and relevance scores.

FR-08
Recruiters can sort candidates by relevance score.

FR-09
Recruiters can search and filter candidates.

FR-10
Recruiters can download candidate evaluation reports.

FR-11
Recruiters can delete candidate records.

FR-12
The system stores candidate profiles and evaluation results.

# Non Functional Requirements

Performance
Matching should complete within 5 seconds.
Availability
99% uptime.
Security
JWT Authentication
Passwords encrypted.
Usability
Simple recruiter dashboard.
Scalability
Support at least 10,000 resumes.
Reliability
Automatic error handling.
Maintainability
Modular architecture.
Portability
Docker deployment.