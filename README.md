# StartupSphere

**One Connected Ecosystem for Ideas, Founders, Funding & Talent.**

StartupSphere is a complete startup ecosystem platform designed to support student entrepreneurs from idea creation to building their team and scaling.

## Current Checkpoint Release: v0.1 (Checkpoint 1)
This release focuses on the core foundation of the platform:
- Custom User model and Role-Based Authentication
- Landing Page with modern SaaS UI principles
- Founder Dashboard Skeleton
- Startup Registration functionality

## Installation Guide

Follow these instructions to set up the project locally.

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vineet375/Startup_Sphere.git
   cd Startup_Sphere/startup_sphere
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   *(Since this is a fresh Django project, you currently only need Django)*
   ```bash
   pip install django
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/`.

## Architecture & Structure
The project uses a modular Django architecture with custom vanilla CSS layered on Bootstrap 5 for modern styling.
- `core/`: Custom User Model & generic views (landing page)
- `accounts/`: Authentication logic (login, register, logout)
- `dashboard/`: Role-specific routing and dashboard skeleton
- `incubator/`: Startup registration, profiles, milestones

## Documentation
- Database Schema and ER Diagram: `docs/database_schema.md`
