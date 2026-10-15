# NEXORA Database Initialization & Seed Data

This directory contains the database schema initialization and realistic dummy seed scripts conforming to the **57-table multi-tenant architecture** defined in `database_architecture.md`.

---

## 📁 Database Files & Dumps

1. **[`01_table_creation.sql`](file:///c:/Users/DELL/OneDrive/Desktop/NEXORA/db/01_table_creation.sql)** (Schema DDL)
   - Contains table creation commands (`CREATE TABLE IF NOT EXISTS`), extensions (`uuid-ossp`, `pgcrypto`, `citext`), primary/foreign key constraints, unique constraints, check constraints, and performance indexes across all 57 tables.

2. **[`02_data_insertion.sql`](file:///c:/Users/DELL/OneDrive/Desktop/NEXORA/db/02_data_insertion.sql)** (Data Records)
   - Contains pure data insertion commands (`INSERT INTO ... VALUES (...) ON CONFLICT DO NOTHING`) for all 27 populated tables (over 760+ records).
   - Features primary student **Sanjay H S** (`sanjudeepu.153@gmail.com`), the active 21-student roster without Nikhitha, faculty, admins, attendance, grades, finance, exams, and courses.

3. **[`03_nexora_complete_dump.sql`](file:///c:/Users/DELL/OneDrive/Desktop/NEXORA/db/03_nexora_complete_dump.sql)** (Full Dump: Schema + Data)
   - Complete single-file SQL dump combining both Part 1 (Table Creation) and Part 2 (Data Insertion).
   - Can be imported directly into any fresh or existing PostgreSQL 14+ database in a single command.

---

## 🚀 How to Import / Restore

```powershell
# Restore Complete Dump (Schema + Data together):
Get-Content db/03_nexora_complete_dump.sql -Raw | docker exec -i nexora_db psql -U nexora_admin -d nexora

# Or restore individually:
Get-Content db/01_table_creation.sql -Raw | docker exec -i nexora_db psql -U nexora_admin -d nexora
Get-Content db/02_data_insertion.sql -Raw | docker exec -i nexora_db psql -U nexora_admin -d nexora
```

---

## 👥 Seeded Test Credentials

All accounts are pre-configured with the default password: **`Password123!`**

### 1. Platform Operator
| Role | Email | Password |
| :--- | :--- | :--- |
| **Superadmin** | `superadmin@nexoracloud.com` | `Password123!` |

### 2. Tenant: Apex Institute of Technology & Management (`apex-institute`)
| Role | Name | Email | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | Dr. Rajesh Sharma | `admin@apex.edu` | System Administrator |
| **Faculty (HOD)** | Dr. Aris Thorne | `hod.cse@apex.edu` | HOD & Professor, CSE (`FAC-CSE-001`) |
| **Faculty** | Dr. Priya Nair | `prof.priya@apex.edu` | Associate Professor, CSE (`FAC-CSE-002`) |
| **Faculty** | Prof. Vikram Malhotra | `prof.vikram@apex.edu` | Assistant Professor, ECE (`FAC-ECE-001`) |
| **Student** | Sanjay H S | `sanjudeepu.153@gmail.com` | B.Tech CSE, Term 5 (`2024CSE001`, Password: `sanju$123`) |
| **Student** | Nirmala G | `student.nirmala.g@apex.edu` | B.Tech CSE, Term 5 (`2024CSE003`) |
| **Student** | Nisarga B G | `student.nisarga.bg@apex.edu` | B.Tech ECE, Term 5 (`2024ECE001`) |
| **Student** | Nishanth C K | `student.nishanth.ck@apex.edu` | B.Tech CSE, Term 5 (`2024CSE004`) |
