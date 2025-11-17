# Gemach Management System – Chasdei Yaakov
**Software Engineering Project – JCT (Course 151060)**

---

## Overview
The Gemach Management System is a full-stack web application…

---

## Project Structure
The project is built as a modular full-stack application…

### Frontend

Vue.js (Vite)

Tailwind CSS

Axios

### Backend

Django (Python)

Django REST Framework

REST API

### Database

PostgreSQL 15+

psycopg2-binary

### DevOps

Azure Boards

GitHub / Azure Repos

CI/CD (planned)

---

## Implemented Stages

### **Stage 1–2 (Current)**

Repository setup

Documentation

Initial architecture

Defining Epics, Features, User Stories

### **Stage 3 (Sprint 1 – Upcoming)**

Django project setup

Vue setup

Initial DB schema

Basic end-to-end flow

---

## Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
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
Create database:
```
gemach_db
```

Settings:
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
├── frontend/
└── README.md
```

---

## Team

Yael Farber

Hila Rosental

Hila Miller

Bracha Kalagi

---

## License
Academic project.
