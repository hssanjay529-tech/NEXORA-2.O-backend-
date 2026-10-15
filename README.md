# NEXORA — Multi-Tenant College Operations Portal

> **Production-Grade Architecture**: FastAPI + PostgreSQL 16 + SQLAlchemy + Docker + React 18 + Vite + TypeScript + Tailwind CSS.

---

## 🚀 Unified Production Authentication

NEXORA enforces **strict database-backed authentication** across all workflows. There are no client-side role toggle buttons, preset simulation pills, or unauthenticated role switching. 

When a user logs in via the unified login interface:
1. **Target Institution**: Loaded dynamically via `GET /api/v1/tenants/public` (auto-detects the institution domain from the email input, e.g., `@apex.edu` or `@metro-uni.edu`).
2. **Database Verification**: The backend verifies email, password hash (bcrypt), tenant membership, and account status in PostgreSQL.
3. **Role Determination**: The role (`STUDENT`, `FACULTY`, `DEAN`, `ADMIN`) is extracted directly from the verified database record and encoded into the signed JWT access token and rotated refresh token cookie.
4. **Dynamic Lanyard ID Card**: The ReactBits 3D lanyard ID card displays a placeholder (`PENDING AUTH` / `AWAITING SIGN-IN`) before authentication, and animates on `200 OK` to display the verified member's real name, role badge, student/employee identifier, department, and `VERIFIED` status prior to redirecting.
5. **Role-Based Workspace**: The application automatically routes the user to their authorized portal workspace.

---

## 🔑 Authorized Test Credentials

All credentials below are active and verified in the database:

| Role | Name | Institutional Email | Password | Identifier | Default Workspace |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **STUDENT** | Sanjay H S | `sanjudeepu.153@gmail.com` | `sanju$123` | `2024CSE001` | Student Portal (Overview, Courses, Attendance, Invoices, Exams) |
| **FACULTY** | Dr. Priya Nair | `prof.priya@apex.edu` | `Password123!` | `FAC-CSE-002` | Faculty Portal (Attendance Matrix, Course Vault, Gradebook) |
| **DEAN** | Dr. Arvind Swaminathan | `dean.engineering@apex.edu` | `Password123!` | `DEAN-ENG-001` | Dean Executive Suite (School Metrics, Curriculum Approvals, KPIs) |
| **ADMIN** | Dr. Rajesh Sharma | `admin@apex.edu` | `Password123!` | `ADM-001` | Governance & Control (Directory, Schedule Matrix, Invoicing, Audits) |

---

## 🔒 Security & RBAC Specifications

- **Token Rotation**: Single-use refresh tokens stored hashed in `user_tokens`; rotated automatically on `POST /api/v1/auth/refresh`.
- **HttpOnly Cookies**: Refresh tokens are returned with `httponly=True`, `samesite="lax"`, and `path="/api/v1/auth"`.
- **Brute-Force Defense**: Repeated failed logins (5 attempts) lock the account for 15 minutes (`HTTP 423 Locked`).
- **Generic Errors**: Failed credentials return generic messages (`Invalid email or password`) to mitigate user enumeration.
- **Session Revocation**: Password reset via `/api/v1/auth/reset-password` immediately revokes all prior refresh tokens and active sessions.
- **Audit Logging**: Every authentication event (`USER_LOGIN`, `USER_LOGOUT`, `PASSWORD_RESET_REQUESTED`, `PASSWORD_RESET_COMPLETED`) is written to `audit_logs`.
- **RBAC Enforcement**: Endpoints strictly enforce permissions (e.g., Dean attempting to manage admin users receives `HTTP 403 Forbidden`).

---

## 🛠️ API Routes

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/login` — Authenticate and issue JWT pair + user preview
- `POST /api/v1/auth/refresh` — Refresh token rotation
- `POST /api/v1/auth/logout` — Revoke active token & clear cookie
- `GET /api/v1/auth/me` — Deep user profile resolution
- `POST /api/v1/auth/forgot-password` — Single-use password reset token dispatch
- `POST /api/v1/auth/reset-password` — Password reset completion
- `POST /api/v1/auth/change-password` — Authenticated password change

### Public Discovery & Portals
- `GET /api/v1/tenants/public` — List active institutions and domains
- `GET /api/v1/dean/dashboard` — Dean executive metrics and pending curriculum proposals
- `GET /api/v1/admin/dashboard` — Institutional KPI summaries
- `GET /api/v1/faculty/dashboard` — Faculty timetable and lectures
- `GET /api/v1/student/dashboard` — Student attendance, courses, and fee invoices

---

## 📦 Running NEXORA Locally

```bash
# 1. Start all container services (PostgreSQL, FastAPI Backend)
docker compose up -d

# 2. Re-seed database (if necessary)
docker exec nexora_backend python seed_db.py

# 3. Access Services
# FastAPI Swagger Docs: http://localhost:8000/docs
# Backend Health Check: http://localhost:8000/health
```

---

## ☁️ Cloud Deployment & Repositories

### Repositories
- **Backend (FastAPI)**: [NEXORA-2.O-backend-](https://github.com/hssanjay529-tech/NEXORA-2.O-backend-)
- **Frontend (React / Vite)**: [NEXORA-2.O-forntend-](https://github.com/hssanjay529-tech/NEXORA-2.O-forntend-)

### 1. Database (Supabase)
1. Sign up at [supabase.com](https://supabase.com) and create a new project.
2. Under **Project Settings -> Database**, find your connection string (`URI`).
3. Set `DATABASE_URL` in your backend environment variables using the connection pooler or direct URI:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
   ```

### 2. Backend Hosting (Render / Railway)
- **Render**:
  1. Create a **New Web Service** connected to `https://github.com/hssanjay529-tech/NEXORA-2.O-backend-.git`.
  2. Build Command: `pip install -r requirements.txt`
  3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
  4. Environment Variables: Add `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT=production`, etc.
- **Railway**:
  1. Create a **New Project** -> **Deploy from GitHub repo** -> select `NEXORA-2.O-backend-`.
  2. Set environment variables.
