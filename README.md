Gemach Management System – Chasdei Yaakov

Software Engineering Project – JCT (Course 151060)

Overview

The Gemach Management System is a full-stack web application designed to manage community loans, repayments, trustees, borrowers, and donations.
The system provides secure, role-based access control: administrators can create and update all data, while trustees, borrowers, and donors have view-only access to the information relevant to their role.

This project is developed using Agile methodology and managed through Azure DevOps.
The system is built with a modern frontend, backend, and database architecture, with planned cloud deployment in later stages.

Project Structure

The project is built as a modular full-stack application consisting of three layers:

Frontend: Vue.js (Vite), Tailwind CSS (RTL support), Axios

Backend: Django (Python), Django REST Framework, REST API

Database: PostgreSQL 15+ with integration via psycopg2-binary

DevOps: Azure Boards, GitHub/Azure Repos, planned CI/CD pipelines

Documentation: Azure Wiki, dashboards, and sprint-based tracking

Implemented Stages
Stage 1–2 (Current)

Repository setup, project documentation, and initial architecture.

Creation of README, repository structure, and Azure DevOps project.

Establishing development environments (backend, frontend, local DB).

Definition of Epics, Features, and User Stories according to Agile methodology.

Stage 3 (Sprint 1 – Upcoming)

Setup of the Django backend project structure.

Setup of Vue frontend project with Tailwind CSS.

Creation of initial PostgreSQL schema (borrowers, loans, trustees, donors).

Implementation of a minimal end-to-end working system (first loan creation flow).

Basic API endpoints for core functionality.

Stage 4–6 (Later Sprints)

Complete CRUD functionality for all entities.

Auto-generated payment schedules.

Automatic status updates for loans and payments.

Reports and dashboards for admins.

Expanded user permissions and validations.

Initial cloud deployment.

Technologies
Frontend

Vue.js (Vite)

Tailwind CSS

Axios for API communication

Backend

Python 3.12+

Django 5

Django REST Framework

PostgreSQL integration (psycopg2-binary)

Database

PostgreSQL 15+

Managed locally via pgAdmin

Cloud-ready structure for future deployment

DevOps & Tools

Azure DevOps (Boards, Wiki, Pipelines)

Git (GitHub / Azure Repos)

Postman / Insomnia for API testing

Development Setup
Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Frontend Setup
cd frontend
npm install
npm run dev

PostgreSQL Setup

Create a local database named:

gemach_db


Configure it in settings.py as follows:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gemach_db',
        'USER': 'postgres',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

Future Deployment

In later sprints, the system will be deployed to a cloud environment.

Planned deployment stack:

Backend: Azure App Service / Render

Database: Azure PostgreSQL / Supabase

Frontend: Netlify / Vercel / Azure Static Web Apps

CI/CD: Azure Pipelines with automated testing and deployment

Repository Structure
Loan-Management/
│
├── backend/
│   ├── gemach_backend/
│   ├── apps/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md

Team

Yael Farber

Hila Rosental

Hila Miller

Bracha Kalagi

License

This is an academic project. No external license is currently applied.
