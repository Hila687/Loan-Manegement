🏦 Gemach Management System – Chasdei Yaakov

Software Engineering Project – JCT (Course 151060)

📌 Overview

The Gemach Management System is a full-stack web application designed to manage community loans, repayments, trustees, borrowers, and donations in a secure and transparent way.
Administrators have full control over all system data, while trustees, borrowers, and donors receive view-only access relevant to their role.

The project is developed using Agile methodology, managed entirely through Azure DevOps, and implemented with a modern frontend, backend, and cloud-ready architecture.

🎯 Project Objectives

Digitize and centralize the Gemach’s loan-management workflow

Provide accurate, secure, and role-based access to sensitive data

Support automatic payment schedules and reporting features

Deliver a production-ready architecture that supports cloud deployment

Maintain high standards of maintainability, reliability, and usability

🧠 System Architecture

The system follows a Frontend → Backend → Database layered architecture.

Frontend

Vue.js (Vite)

Tailwind CSS with full RTL support

Axios for REST API communication

Backend

Django (Python)

Django REST Framework

PostgreSQL integration via psycopg2-binary

Database

PostgreSQL

Local development DB for early sprints

Cloud DB support for deployment (Azure, Render, Supabase, etc.)

DevOps

Azure DevOps Boards — backlog, sprints, tasks, user stories

Azure Repos or GitHub — version control

Azure Pipelines (planned) — CI/CD

Wiki documentation and dashboards

🛠 Development Setup
✔ Local Development (Sprints 1–2)

Local environment is used during early development for faster iteration.

Backend setup:

cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py runserver


Frontend setup:

cd frontend
npm install
npm run dev


Local PostgreSQL setup:
Create database gemach_db and update settings.py accordingly.

☁ Future Cloud Deployment (Later Sprints)

The system is designed to be easily deployed to cloud environments.

Supported future deployment providers:

Azure App Service (recommended for Django)

Render

Supabase / Azure Database for PostgreSQL

Netlify/Vercel for frontend hosting

Production environment will include:

Cloud-hosted PostgreSQL instance

Backend deployment with environment variables (no hardcoded credentials)

CI/CD pipeline via Azure Pipelines

Frontend built via Vite and deployed to a static hosting provider

Cloud-specific configuration will be added in upcoming sprints.

🗂 Repository Structure
gemach-system/
│
├── backend/
│   ├── gemach_backend/
│   ├── apps/
│   ├── requirements.txt
│   └── manage.py
│
└── frontend/
    ├── src/
    ├── public/
    └── package.json

📅 Agile Workflow

Managed entirely through Azure DevOps:

Epics → Features → User Stories → Tasks

2-week sprints

Daily team sync

Retrospectives

Dashboard tracking of progress and velocity

👥 Team

Yael Farber

Hila Rosental

Hila Miller

Bracha Kalagi

📄 License

Internal academic project — no external licensing currently applied.
