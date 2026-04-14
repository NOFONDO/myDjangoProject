# AgriConnect — Complete Django Backend Setup Guide
# Final Year Project · Secure REST API

============================================================
## TABLE OF CONTENTS
============================================================
1. Project Structure Overview
2. Step-by-Step Environment Setup
3. File-by-File Code (all files listed in order)
4. Security Checklist
5. How to Run
6. How to Connect Frontend
============================================================


## STEP 1 — FINAL FOLDER STRUCTURE
============================================================

Your project root will look exactly like this:

    agriconnect/                        ← project root (git repo)
    │
    ├── frontend/                       ← your existing HTML/CSS/JS files go here
    │   ├── index.html
    │   ├── products.html
    │   ├── product-details.html
    │   ├── register.html
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── upload.html
    │   ├── styles.css
    │   └── script.js
    │
    ├── backend/                        ← Django project lives here
    │   ├── manage.py
    │   ├── requirements.txt
    │   ├── .env                        ← SECRET keys (never commit this)
    │   ├── .env.example                ← safe template to commit
    │   ├── .gitignore
    │   │
    │   ├── config/                     ← Django project config (settings, urls)
    │   │   ├── __init__.py
    │   │   ├── settings/
    │   │   │   ├── __init__.py
    │   │   │   ├── base.py             ← shared settings
    │   │   │   ├── development.py      ← dev overrides
    │   │   │   └── production.py       ← production overrides
    │   │   ├── urls.py                 ← root URL router
    │   │   └── wsgi.py
    │   │
    │   ├── apps/
    │   │   ├── users/                  ← custom user app
    │   │   │   ├── __init__.py
    │   │   │   ├── admin.py
    │   │   │   ├── apps.py
    │   │   │   ├── models.py           ← CustomUser model
    │   │   │   ├── serializers.py      ← register/login serializers
    │   │   │   ├── views.py            ← auth endpoints
    │   │   │   ├── urls.py
    │   │   │   └── permissions.py      ← IsFarmer, IsBuyer helpers
    │   │   │
    │   │   └── products/               ← products app
    │   │       ├── __init__.py
    │   │       ├── admin.py
    │   │       ├── apps.py
    │   │       ├── models.py           ← Product, Order models
    │   │       ├── serializers.py
    │   │       ├── views.py            ← product CRUD endpoints
    │   │       └── urls.py
    │   │
    │   └── media/                      ← uploaded images saved here (git-ignored)
    │
    └── README.md


## STEP 2 — ENVIRONMENT SETUP (run these commands one by one)
============================================================

### 2.1 Check Python is installed
    python --version        # must be 3.10 or higher
    # If not installed: https://www.python.org/downloads/

### 2.2 Create the folder structure
    mkdir agriconnect
    cd agriconnect
    mkdir frontend backend
    # Move your existing HTML/CSS/JS files into frontend/

### 2.3 Create and activate virtual environment
    cd backend
    python -m venv venv

    # On Windows:
    venv\Scripts\activate

    # On Mac/Linux:
    source venv/bin/activate

    # You should see (venv) in your terminal prompt

### 2.4 Install all dependencies
    pip install -r requirements.txt
    # (requirements.txt content is listed in the next section)

### 2.5 Create Django project and apps
    django-admin startproject config .
    mkdir apps
    cd apps
    python ../manage.py startapp users
    python ../manage.py startapp products
    cd ..

### 2.6 Create the .env file
    # Copy the .env.example file and fill in your values
    cp .env.example .env

### 2.7 Run migrations
    python manage.py makemigrations users
    python manage.py makemigrations products
    python manage.py migrate

### 2.8 Create a superuser (admin account)
    python manage.py createsuperuser

### 2.9 Start the development server
    python manage.py runserver
    # Visit: http://127.0.0.1:8000/api/
    # Admin: http://127.0.0.1:8000/admin/
