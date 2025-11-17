# Gemach Management System – Chasdei Yaakov
**Software Engineering Project – JCT (Course 151060)**

---

## Overview
The Gemach Management System is a full-stack web application designed to manage community loans, repayments, trustees, borrowers, and donations in a structured, transparent, and secure manner.

Administrators can create and update all system data, while trustees, borrowers, and donors have view-only access that aligns with their role and permissions.

The system is developed using Agile methodology and managed through Azure DevOps. It is built with a modern frontend, backend, and database architecture, with cloud deployment planned for later stages.

---

## Project Structure
This project is built as a modular full-stack application consisting of three layers:

### Frontend
- Vue.js (Vite)
- Tailwind CSS (RTL support)
- Axios for REST API communication

### Backend
- Django (Python)
- Django REST Framework
- REST API architecture

### Database
- PostgreSQL 15+
- Integration using `psycopg2-binary`

### DevOps
- Azure Boards (Epics, Features, User Stories, Tasks)
- GitHub / Azure Repos

---

## Implemented Stages

### Stage 1–2 (Current)
- Repository setup, project documentation, and initial architecture.
- Creation of README, repository structure, and Azure DevOps project.
- Establishing development environments (backend, frontend, local DB).
- Defining Epics, Features, and User Stories according to Agile methodology.

### Stage 3 (Sprint 1 – Upcoming)
- Setup of the Django backend project structure.
- Setup of the Vue frontend project with Tailwind CSS.
- Creation of the initial PostgreSQL schema.
- Implementation of a minimal end-to-end working system (basic loan creation flow).
- Basic API endpoints for core functionality.

---

## Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### PostgreSQL Setup
Create a database named:
```
gemach_db
```

Add configuration to `settings.py`:
```python
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
```

---

## Repository Structure
```
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
```

---

## Team
- Yael Farber
- Hila Rosental
- Hila Miller
- Bracha Kalagi

---

## License
Academic project. No external license applied.
