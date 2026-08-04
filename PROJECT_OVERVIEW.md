# StartupSphere

**One Connected Ecosystem for Ideas, Founders, Funding & Talent.**

---

## 📖 Project Overview
StartupSphere is a comprehensive SaaS platform built to support student entrepreneurs. The platform connects the entire startup lifecycle—from idea inception and mentorship to incubation, funding, hiring, and scaling—into one unified ecosystem.

Instead of navigating between disparate tools, founders, mentors, investors, and job seekers can seamlessly interact on a single, modern platform.

---

## 🛠 Technology Stack

### Backend
- **Language:** Python 3.x
- **Framework:** Django 5.x
- **Database:** SQLite (Development) / PostgreSQL (Production)

### Frontend
- **Structure & Logic:** HTML5, Vanilla JavaScript, AJAX
- **Styling:** Vanilla CSS, Bootstrap 5 (with a custom, modern SaaS aesthetic)
- **Typography:** Poppins (Google Fonts)

---

## 👥 User Roles & Access
The platform features role-based access control, ensuring that each stakeholder gets a tailored dashboard, navigation sidebar, and distinct permissions.

1. **Founder**: Can submit ideas, track milestones, pitch to investors, and post jobs.
2. **Mentor**: Can review startup ideas, provide feedback, and guide founders.
3. **Investor**: Can view pitch decks, track funding rounds, and communicate with founders.
4. **Applicant**: Can upload resumes, apply for jobs, and track interview status.
5. **Admin**: Platform oversight and moderation.

---

## 🧩 Project Modules

### 1. Incubator Module (Core Engine)
- **Startup Registration:** Create and manage startup profiles.
- **Idea Submission:** Detail problem statements and proposed solutions.
- **Mentorship:** Assign mentors to startups for guidance and feedback.
- **Milestone Tracking:** Track progress timelines and startup stages.
- **Documents & Events:** Upload essential startup documents and participate in ecosystem events.

### 2. CRM Module (Investor Relations)
- **Investor Profiles:** Manage investor preferences and portfolios.
- **Funding Rounds:** Track pre-seed, seed, and growth funding.
- **Pitch Decks:** Secure upload and review of pitch decks.
- **Analytics:** Data-driven insights on startup performance for investors.

### 3. Hiring Module (Talent Acquisition)
- **Job Postings:** Founders can list open positions by category.
- **Candidate Pipeline:** Applicants can upload resumes and apply for roles.
- **Hiring Dashboard:** Tools for shortlisting and interview scheduling.

---

## 🔄 Expected User Flow

1. **Onboarding:** Register → Login → Select Role (e.g., Founder)
2. **Incubation:** Create Startup → Submit Idea → Mentor Review → Idea Approved
3. **Execution:** Hit Milestones → Participate in Events → Upload Pitch Deck
4. **Funding:** Investor Review → Funding Secured
5. **Scaling:** Post Jobs → Receive Applications → Shortlist → Interview → Hire
6. **Growth:** Continuous Startup Growth

---

## 🏗 System Architecture (Django Apps)
The backend is structured into highly cohesive, loosely coupled Django apps:
- `core/`: Custom User Model and generic platform logic.
- `accounts/`: Authentication and role assignment.
- `dashboard/`: Dedicated user dashboards for different roles.
- `incubator/`: Startup lifecycle management.
- `crm/`: Investor and funding management (Upcoming).
- `hiring/`: Jobs and application tracking (Upcoming).
- `events/`, `notifications/`, `reports/`, `analytics/`: Shared ecosystem utilities.

---

## 🎨 UI/UX Philosophy
The design language is heavily inspired by modern SaaS platforms (like Vercel, Stripe, or Linear):
- **Aesthetic:** Light theme focused on clean layouts, rounded cards (12px border radius), and soft drop shadows.
- **Colors:** Vibrant gradients and accents drawn directly from the official StartupSphere branding.
- **Usability:** Responsive, intuitive navigation, and micro-interactions for a premium feel.

---

## 📅 Development Roadmap & Checkpoints

- **Checkpoint 1 (Day 1-10):** Professional foundation. Project setup, Custom User Model, Authentication, Landing Page, Dashboard skeletons, and initial Startup registration. *(Completed - v0.1)*
- **Checkpoint 2 (Mid Aug - Late Sep):** Core business logic. Incubator deep-dive, CRM module, milestones, and funding mechanics. *(Upcoming - v0.5)*
- **Checkpoint 3 (Late Sep - Early Oct):** Platform completion. Hiring module, final UI polish, performance optimization, and testing. *(Upcoming - v1.0)*
