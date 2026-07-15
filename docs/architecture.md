# System Architecture

## Overview

The system follows a three-tier architecture.

### Frontend
- **React application**: Provides an intuitive user interface for recruiters to upload resumes, view extracted candidate details, and see ranked applicants.

### Backend
- **FastAPI REST API**: Handles incoming HTTP requests, serves endpoints for resume uploading and processing orchestration, manages user authentication, and interfaces with both the database and the machine learning services.

### Database
- **PostgreSQL**: Stores relational application data including user accounts, metadata for uploaded resumes, parsed profile entities, and finalized applicant rankings.

### Machine Learning
- **Resume analysis service**: A pipeline responsible for processing raw resumes (e.g., PDF/DOCX), extracting structured fields via Natural Language Processing (NLP), and scoring applicants against job descriptions.

---

## Architecture Diagram

```mermaid
flowchart LR

Recruiter --> React

React --> FastAPI

FastAPI --> PostgreSQL

FastAPI --> ResumeParser

ResumeParser --> NLPModel

NLPModel --> RankingEngine

RankingEngine --> PostgreSQL