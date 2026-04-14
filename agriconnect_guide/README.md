# AgriConnect — Backend README
# Final Year Project · Secure Django REST API

==============================================================
## COMPLETE STEP-BY-STEP SETUP (READ TOP TO BOTTOM)
==============================================================

## STEP 1 — Create the folder structure
--------------------------------------------------------------
Open a terminal and run these commands:

    mkdir agriconnect
    cd agriconnect
    mkdir frontend backend

Move all your HTML/CSS/JS files into the frontend/ folder.


## STEP 2 — Set up Python virtual environment
--------------------------------------------------------------
A virtual environment keeps your project's packages separate
from the rest of your computer. Always use one.

    cd backend
    python -m venv venv

    # Activate it:
    # Windows:
    venv\Scripts\activate

    # Mac/Linux:
    source venv/bin/activate

    # You will see (venv) at the start of your prompt.
    # Every time you open a new terminal, activate the venv first!


## STEP 3 — Install dependencies
--------------------------------------------------------------
    pip install -r requirements.txt

This installs: Django, DRF, CORS headers, token auth,
rate limiting, brute force protection, image handling, etc.


## STEP 4 — Create the Django project scaffolding
--------------------------------------------------------------
Run these in the backend/ folder with venv activated:

    # Create the config package (project settings + urls)
    django-admin startproject config .

    # NOTE: The dot (.) at the end is important —
    # it puts manage.py in the current folder, not a subfolder.

    # Create the apps folder and apps
    mkdir apps
    mkdir apps\users    (Windows)
    mkdir apps/users    (Mac/Linux)
    mkdir apps\products (Windows)
    mkdir apps/products (Mac/Linux)

    # Create the apps using Django
    python manage.py startapp users apps/users
    python manage.py startapp products apps/products

    # Create the logs folder (for security logging)
    mkdir logs


## STEP 5 — Copy all the provided code files
--------------------------------------------------------------
Replace the auto-generated files with the ones in this guide:

    backend/
    ├── manage.py                       ← replace with provided
    ├── requirements.txt                ← provided
    ├── .env.example                    ← provided
    ├── .gitignore                      ← provided
    │
    ├── config/
    │   ├── __init__.py                 ← leave empty
    │   ├── urls.py                     ← replace with provided
    │   ├── wsgi.py                     ← replace with provided
    │   └── settings/
    │       ├── __init__.py             ← leave empty
    │       ├── base.py                 ← provided
    │       ├── development.py          ← provided
    │       └── production.py          ← provided
    │
    └── apps/
        ├── __init__.py                 ← leave empty
        ├── users/
        │   ├── __init__.py             ← leave empty
        │   ├── admin.py                ← replace with provided
        │   ├── apps.py                 ← replace with provided
        │   ├── models.py               ← replace with provided
        │   ├── serializers.py          ← provided (new file)
        │   ├── views.py                ← replace with provided
        │   ├── urls.py                 ← provided (new file)
        │   ├── permissions.py          ← provided (new file)
        │   └── utils.py                ← provided (new file)
        │
        └── products/
            ├── __init__.py             ← leave empty
            ├── admin.py                ← replace with provided
            ├── apps.py                 ← replace with provided
            ├── models.py               ← replace with provided
            ├── serializers.py          ← provided (new file)
            ├── views.py                ← replace with provided
            └── urls.py                 ← provided (new file)


## STEP 6 — Create the .env file
--------------------------------------------------------------
    # In the backend/ folder:
    cp .env.example .env

    # Now open .env and set your SECRET_KEY.
    # Generate a key by running:
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

    # Paste the output as the value of SECRET_KEY in .env


## STEP 7 — Run migrations
--------------------------------------------------------------
Migrations create the database tables from your models.
You must run makemigrations for each app, then migrate.

    python manage.py makemigrations users
    python manage.py makemigrations products
    python manage.py migrate

    # You should see:  Running migrations: OK


## STEP 8 — Create a superuser (admin account)
--------------------------------------------------------------
    python manage.py createsuperuser

    # It will ask for:
    # Phone number: (e.g. +237600000000)
    # Name: (e.g. Admin)
    # Password: (must be 8+ chars)


## STEP 9 — Add initial categories (via admin panel)
--------------------------------------------------------------
    # Start the server:
    python manage.py runserver

    # Open: http://127.0.0.1:8000/admin/
    # Log in with your superuser credentials
    # Go to Products → Categories → Add Category
    # Add: Vegetables, Fruits, Grains, Legumes, Oils, Spices, Livestock


## STEP 10 — Replace script.js in your frontend
--------------------------------------------------------------
Copy frontend_script_updated.js to your frontend/ folder
and rename it to script.js (replacing the old one).

This version makes real API calls to your Django backend.


## STEP 11 — Test the full flow
--------------------------------------------------------------
Keep the Django server running:
    python manage.py runserver

Open your frontend using VS Code Live Server (port 5500):
    http://127.0.0.1:5500/frontend/index.html

Test this order:
    1. Open register.html → create a Farmer account
    2. Log in → you should be redirected to dashboard
    3. Open upload.html → list a product
    4. Open products.html → you should see your product
    5. Log out
    6. Register a Buyer account
    7. Browse products → click View Details → click Buy Now


==============================================================
## FULL API REFERENCE
==============================================================

Base URL: http://127.0.0.1:8000/api/

Authentication: Add this header to protected requests:
    Authorization: Token <your_token_here>

------------------------------------------------------------------
AUTH ENDPOINTS
------------------------------------------------------------------

POST   /api/auth/register/
    Body: { name, phone, password, password_confirm, role, location }
    Response: { success, data: { token, user } }
    Auth: None required

POST   /api/auth/login/
    Body: { phone, password }
    Response: { success, data: { token, user } }
    Auth: None required

POST   /api/auth/logout/
    Response: { success, message }
    Auth: Required

GET    /api/auth/me/
    Response: { success, data: { id, name, phone, role, location, ... } }
    Auth: Required

PATCH  /api/auth/me/
    Body: { name, location }   (only these two can be changed)
    Response: { success, data: { updated user } }
    Auth: Required

------------------------------------------------------------------
PRODUCT ENDPOINTS
------------------------------------------------------------------

GET    /api/products/
    Query params: ?search=tomato&category=vegetables&page=1
    Response: { success, data: { results: [...], total, page, has_next } }
    Auth: None required (public)

POST   /api/products/create/
    Body: multipart/form-data (because of image upload)
    Fields: name, price, quantity, unit, location, description,
            category_id, image (file), harvest_date
    Response: { success, data: { product } }
    Auth: Required — Farmer only

GET    /api/products/<uuid>/
    Response: { success, data: { full product + farmer info } }
    Auth: None required (public)

PATCH  /api/products/<uuid>/edit/
    Body: any product fields to update
    Response: { success, data: { updated product } }
    Auth: Required — owner farmer only

DELETE /api/products/<uuid>/edit/
    Response: { success, message }
    Auth: Required — owner farmer only

GET    /api/products/mine/
    Response: { success, data: [ farmer's products ] }
    Auth: Required — Farmer only

GET    /api/products/categories/
    Response: { success, data: [ { id, name, slug } ] }
    Auth: None required (public)

------------------------------------------------------------------
ORDER ENDPOINTS
------------------------------------------------------------------

POST   /api/products/orders/
    Body: { product: "<uuid>", quantity: 2, note: "..." }
    Response: { success, data: { order } }
    Auth: Required — Buyer only

GET    /api/products/orders/mine/
    - Farmers see orders for their products
    - Buyers see orders they placed
    Response: { success, data: [ orders ] }
    Auth: Required

PATCH  /api/products/orders/<uuid>/status/
    Body: { status: "confirmed" }  or "completed" or "cancelled"
    Response: { success, data: { updated order } }
    Auth: Required — Farmer who owns the product only


==============================================================
## SECURITY FEATURES IMPLEMENTED
==============================================================

1. PASSWORDS
   - Never stored as plain text
   - Hashed using PBKDF2 + SHA256 (Django default)
   - Minimum 8 characters enforced
   - Cannot be a common password (e.g. "password123")

2. AUTHENTICATION
   - Token-based authentication (Authorization: Token ...)
   - Tokens are invalidated on logout (deleted from DB)
   - UUID primary keys prevent ID enumeration attacks

3. BRUTE FORCE PROTECTION (django-axes)
   - Locks out after 5 failed login attempts
   - Lockout lasts 1 hour
   - Records all failed attempts with IP address
   - Resets on successful login

4. RATE LIMITING
   - Anonymous users: max 50 requests/hour
   - Authenticated users: max 500 requests/hour
   - Login endpoint: max 10 attempts/hour

5. INPUT SANITIZATION
   - All text inputs pass through bleach.clean()
   - Strips all HTML and JavaScript from user input
   - Prevents stored XSS (Cross-Site Scripting) attacks

6. FILE UPLOAD SECURITY
   - Only JPEG, PNG, WEBP images allowed
   - Maximum file size: 5 MB
   - Files renamed with UUID before saving
   - Stored outside the web root

7. CORS (Cross-Origin Resource Sharing)
   - Only your frontend URL is whitelisted
   - Prevents other websites from calling your API

8. ENVIRONMENT VARIABLES
   - SECRET_KEY, DEBUG, database credentials in .env
   - .env is in .gitignore — never committed to Git

9. SQL INJECTION PREVENTION
   - Django ORM parameterises all queries automatically
   - Never use raw SQL with user input

10. HTTPS IN PRODUCTION
    - HSTS headers force HTTPS connections
    - Cookies marked Secure and HttpOnly
    - SSL redirect enabled

11. CLICKJACKING PREVENTION
    - X-Frame-Options: DENY header set
    - Prevents your site being loaded in iframes

12. OBJECT-LEVEL PERMISSIONS
    - Farmers can only edit/delete their own products
    - Buyers can only view their own orders
    - IsOwnerOrAdmin permission class enforced on all writes


==============================================================
## COMMON ERRORS AND FIXES
==============================================================

Error: "No module named 'apps.users'"
Fix:   Make sure apps/__init__.py exists (even if empty).
       Make sure INSTALLED_APPS uses 'apps.users' not 'users'.

Error: "AUTH_USER_MODEL refers to model 'users.CustomUser' that
        has not been installed"
Fix:   In settings/base.py, confirm INSTALLED_APPS includes
       'apps.users', then run migrations again.

Error: "Table 'db.users_customuser' doesn't exist"
Fix:   python manage.py makemigrations users
       python manage.py migrate

Error: CORS error in browser console
Fix:   In .env, set CORS_ALLOWED_ORIGINS to include the
       exact URL of your frontend, e.g.:
       http://127.0.0.1:5500

Error: "Authentication credentials were not provided"
Fix:   The endpoint requires a token. Make sure your
       frontend sends: Authorization: Token <token>

Error: Image not showing after upload
Fix:   Make sure DEBUG=True in development.
       Check that MEDIA_URL and MEDIA_ROOT are set in settings.
       The config/urls.py must include the static() line.
