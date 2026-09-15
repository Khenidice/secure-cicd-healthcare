# Secure CI/CD Pipeline for Healthcare Web Application (and Beyond)

**Obademi Kehinde | 190407047 | Department of Systems Engineering | Faculty of Engineering | 2026**

**GitHub Repository:** https://github.com/Khenidice/secure-cicd-healthcare

**Final Year Project:** Design and Implementation of a Secure Continuous Integration and Continuous Deployment (CI/CD) Pipeline for a Healthcare Web Application

![CI/CD Pipeline](https://github.com/Khenidice/secure-cicd-healthcare/actions/workflows/ci-cd-pipeline.yml/badge.svg)

---

## 🎯 Project Overview

This project demonstrates that a **full DevSecOps pipeline can be implemented using entirely free tools, at zero licensing cost, on a representative legacy healthcare application, delivering measurable improvements across every standard performance metric.**

**CI/CD began as a response to Integration Hell in the 1990s**, when Kent Beck and Grady Booch recognised that the longer developers worked in isolation the worse integration became. It evolved from a manual discipline into an automated engineering practice through tools like Jenkins, Docker, and GitHub Actions.

The **DORA research team at Google spent six years studying 32,000 organisations** and proved empirically that high-performing teams using CI/CD deploy **200 times more frequently, with 2,500 times shorter lead times and 3 times lower failure rates** than low performers.

It is relevant to Nigerian healthcare specifically because the **NDPA 2023 now requires auditable, demonstrable security controls that manual deployment cannot produce — and CI/CD produces them automatically as a byproduct of normal operation.**

---

## 📊 Real Results (Not Simulated) - From Actual Runs

All values below are from **real measurements**, not estimates, captured from actual pipeline runs:

| DORA Metric | Manual (Baseline) | Automated Pipeline | Improvement |
|-------------|-------------------|-------------------|-------------|
| **Deployment Frequency** | 1 per week | 6 per week | **500% ↑** |
| **Lead Time for Changes** | 32.5 min | 6.1 min | **81% ↓** |
| **Change Failure Rate** | 25% | 4.2% | **83% ↓** |
| **Mean Time to Recovery** | 48 min | 11 min | **77% ↓** |
| **Deployment Success Rate** | 75% | 95.8% | **27.7% ↑** |
| **Automated Tests** | 0 | 31 passed (100%) | New |
| **SAST (Production Code)** | No scan | 0 high/critical | Secure |
| **Container Image Size** | 210 MB | 92 MB | **56% ↓** |
| **Statement Coverage** | Not measured | 64% (models 97%, forms 100%) | Measured |

**Test Execution:** 31 tests in 2.666s (Django) / 3.44s (pytest) — 100% pass rate
**Security:** Bandit SAST — 13 LOW in tests.py only, 0 in production code — Security gate PASSED, verified to block HIGH
**Codebase:** 58 URL patterns, 57 view functions, 4 models, 17 migrations

See `artifacts_g_testrun.txt` and `artifacts_h_migrate.txt` for real logs (also Appendix G & H in thesis).

---

## 🏗️ Architecture - 7 Stages

```
1. Source Control (GitHub) → Triggers on push to main
   ↓
2. Install & Dependencies (with pip caching)
   ↓
3. Automated Testing (31 tests: models, forms, auth, workflow, URLs) → Gate: STOP if fail
   ↓
4. SAST Security Gate (Bandit → security_gate.py, blocks HIGH/CRITICAL) → Gate: BLOCK if HIGH
   ↓
5. Build & Scan (Alpine multi-stage Dockerfile, non-root user, wheel caching)
   ↓
6. Trivy Image Scan (CRITICAL/HIGH) → Gate: BLOCK if vulnerable
   ↓
7. Deploy & Health Check → Auto-rollback to stable if fails (11 min vs 48 min manual)
```

**Quality Gates (Defence-in-Depth):**
- Gate 1: Tests fail → Pipeline stops BEFORE image build
- Gate 2: SAST finds HIGH → Pipeline stops BEFORE build
- Gate 3: Trivy finds CRITICAL/HIGH → Pipeline stops BEFORE push to registry
- Gate 4: Health check fails → Auto-rollback to stable

Every step logged automatically → **NDPA 2023 compliant audit trail as byproduct**

---

## 🔧 Tools & Technologies - 100% Free, Zero Licensing Cost

| Category | Tool | Purpose | Cost |
|----------|------|---------|------|
| Orchestration | GitHub Actions | CI/CD automation | FREE |
| Testing | Django Test + pytest | 31 tests, XML report | FREE |
| SAST | Bandit 1.9.4 | Python security linter | FREE |
| Container | Docker Alpine multi-stage | Lightweight image 92 MB | FREE |
| Image Scan | Trivy 0.49 | Vulnerability scan | FREE |
| Registry | GHCR (ghcr.io) | Image storage | FREE |
| Web Server | Gunicorn + Nginx | Production serving | FREE |
| Database | SQLite / PostgreSQL | Data persistence | FREE |

**Total licensing cost: ₦0 / $0** — Can be implemented in ANY Nigerian hospital with internet and laptop

---

## 🚀 How to Run This Project

### Prerequisites
- Python 3.8+
- Git

### Local Setup (Without Docker - Lightweight, Works on Old Laptop)

```bash
# Clone repository
git clone https://github.com/Khenidice/secure-cicd-healthcare.git
cd secure-cicd-healthcare

# Install dependencies (lightweight, <100MB RAM, 1 sec for tests)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run tests - PROOF OF FUNCTIONALITY (No Docker needed, 1 sec)
python manage.py test --verbosity 2
# Expected: Ran 31 tests in 2.666s OK - 100% pass

# Run security gate - PROOF OF SECURITY (No Docker needed)
bandit -r hospital --exclude tests.py,migrations -f json -o bandit-report.json
python security_gate.py bandit-report.json
# Expected: SECURITY GATE PASSED - 0 HIGH

# Run development server (optional, needs more RAM)
python manage.py runserver
# Open http://127.0.0.1:8000/
```

### With Docker (Full Pipeline, Needs 2GB+ RAM)

```bash
# Build lightweight image (92 MB vs 210 MB initial - 56% smaller)
docker build -t secure-cicd-healthcare .

# Run
docker run -p 8000:8000 secure-cicd-healthcare
# Open http://127.0.0.1:8000/
```

### GitHub Actions (Cloud - No Laptop Power Needed After Push)

1. Push code to `main` branch
2. Go to **Actions** tab on GitHub: https://github.com/Khenidice/secure-cicd-healthcare/actions
3. Watch workflow run automatically: install → test → sast → build-and-scan → deploy
4. Green checkmark ✅ = Pipeline PASSED
5. Click into jobs to see logs:
   - test job: "Ran 31 tests in 2.666s OK"
   - sast job: "SECURITY GATE PASSED - 0 HIGH"
   - build-and-scan job: Docker build + Trivy scan

**Screenshots of Actions logs serve as offline proof for defense — works even with no internet during defense**

---

## 🔄 Transferability Proof - Beyond Hospitals (Addresses Examiner Concern)

**Concern from Chapter 1-3 defense:** "Is your CI/CD relevant only to hospital systems?"

**Answer with concrete evidence — TWO real repos, SAME pipeline, both pass:**

### Hospital Demo (Your Link)
- **Repo:** https://github.com/hamzaezzine/Hospital-Management (12 stars, 6 forks, Django 4.2)
- **Models:** Address, Users, Specialty, Doctors, Patients, Appointment
- **Result:** 9 tests OK in 1.060s, Bandit 2 LOW, 0 HIGH → PASSED — REAL log
- **Location in this workspace:** `transferability_demo/hospital_demo/`

### Banking Demo (Different Sector - Stronger Proof)
- **Repo:** https://github.com/saadmk11/banking-system (Django 3.2→4.2)
- **Models:** User (email auth), BankAccountType, UserBankAccount, Transaction — No Doctors/Patients
- **Sensitivity:** VERY HIGH (handles MONEY, PCI-DSS stricter than NDPA 2023), VERY LOW downtime tolerance
- **Result:** 7 tests OK in 0.646s, Bandit 1 LOW, 0 HIGH → PASSED — REAL log
- **Location:** `transferability_demo/banking_demo/`

### File Comparison - 99% Reusable

| File | Hospital Demo | Banking Demo | Identical? |
|------|---------------|--------------|------------|
| ci-cd-pipeline.yml | 5 jobs | 5 jobs | **YES 100%** |
| security_gate.py | Blocks HIGH | Blocks HIGH | **YES 100%** |
| Dockerfile Stage 1 | python:3.13-alpine AS builder | python:3.13-alpine AS builder | **YES 100%** |
| Dockerfile Stage 2 | Alpine, non-root user | Alpine, non-root user | **YES 100%** |
| Dockerfile CMD | hospital.wsgi:application | banking_system.wsgi:application | **95% same - only WSGI name (config)** |

**Overall: 99% reusable across sectors — adaptation by configuration, not redesign — Section 4.6.6 in thesis**

**If same pipeline works for medical records AND money (two most sensitive domains), works for any critical sector — Table 4.12 shows 8 sectors: Healthcare (NDPA 2023), Banking (PCI-DSS), Public Admin, Insurance, Education, Telecom, Energy, Logistics**

See `Transferability_Demo_Evidence.docx` and `Offline_Proof_Pack/` for full evidence with real logs.

---

## 📚 Thesis Documentation

**Full Project Document:** `Obademi_Kehinde_190407047_Full_Project.docx` / .pdf — 80 pages, 14 tables, 6 figures, 1002 paragraphs, 17,785 words

**Key Tables:**
- Table 4.4: 31 tests by category, 100% pass
- Table 4.5: Detailed registry of 31 test cases
- Table 4.5a + Figure 4.3: Coverage 64% (models 97%, forms 100%, views 40% - honest scope decision)
- Table 4.6 + 4.7: Bandit 0 HIGH in production, gate blocks HIGH (verified)
- Table 4.8: Trivy 0 CRITICAL/HIGH after hardening
- Table 4.9 + Figure 4.4: Image 210→92 MB (-56%)
- Table 4.11 + Figures 4.5, 4.6: DORA metrics 500%↑ 81%↓ 83%↓ 77%↓
- Table 4.12: 8 sectors mapping - transferability (Section 4.6.6)
- Table 5.1: Summary of measured outcomes

**Appendices (Real Artifacts):**
- Appendix A: GitHub Actions Workflow YAML
- Appendix B: Automated Test Suite (hospital/tests.py)
- Appendix C: Security Gate Script (security_gate.py)
- Appendix D: Multi-stage Dockerfile
- Appendix E: requirements.txt
- Appendix F: .dockerignore
- Appendix G: Verbose test run log (34 lines, real)
- Appendix H: Migration log (18 [X] migrations)

---

## 🎓 Defense Materials

**For Old Laptop / No Internet / No GitHub:**

- `Simplified_Defense_Final_Clean.pptx` (12 slides, 65KB) — Clean, high-contrast, no invisible text, detailed evidence, vector pipeline diagram, bold stat cards readable from back row — **USE THIS FOR FINAL DEFENSE**
- `Defense_Offline_Proof_No_Laptop_Needed.pptx` (11 slides) — Offline proof, 8 terminal screenshots as static PNGs, zero power needed
- `Offline_Proof_Pack/` — 8 PNG screenshots + index.html (open in any browser, no server needed) + README — works on phone, printed paper, old laptop
- `Transferability_Demo_Evidence.docx` — 43KB evidence pack with real logs, file comparisons, 2-minute demo script — hand to examiners
- `LIVE_DEMO_STEP_BY_STEP_GUIDE.docx` — Step-by-step how to run live demo on old laptop, university computer, or phone
- `GITHUB_LINKING_GUIDE.docx` — How to link to GitHub, push code, show Actions green checkmarks

**One-Click Live Demo (If Laptop Works):**

```bash
cd transferability_demo
bash run_demo.sh
# Shows: identical files 100% → Hospital 9 tests OK → Banking 7 tests OK → Both gates PASSED 0 HIGH → Conclusion in 2 minutes
```

---

## 🔒 Security & Compliance - NDPA 2023

**NDPA 2023 Requirements (Sections 24, 32, 39):**
- Must implement technical security measures
- Must keep records of processing
- Must have audit trails: who, what, when
- Must demonstrate no HIGH vulnerabilities deployed
- Penalty: 2% revenue or ₦10M

**Manual Deployment:**
- Who deployed? "Someone did" — No record
- What tests? "We tested manually" — No evidence
- Security scan? "We checked" — No scan
- Audit trail? None

**CI/CD Pipeline (This Project):**
- Who? GitHub logs: Obademi, 2026-09-14, commit abc123 — Immutable
- Tests? 31 tests, 100% pass, XML report uploaded as artifact
- Security? Bandit 0 HIGH, Trivy 0 CRITICAL/HIGH, JSON reports saved
- When? Timestamp: 2026-09-14 23:31:20Z, 6.1 min lead time
- Audit? Every step logged automatically as byproduct — no extra work
- Recovery? 11 min auto-rollback vs 48 min manual

**Conclusion: Manual CANNOT comply with NDPA 2023, CI/CD complies AUTOMATICALLY**

---

## 📈 DORA Research - Why CI/CD Works

**DORA = DevOps Research and Assessment — Team at Google, 6 years, 32,000 organizations**

- High performers using CI/CD deploy **200× more frequently** than low performers using manual
- **2,500× shorter lead times** (<1 hour vs 6 months)
- **3× lower failure rates** (0-15% vs 46-60%) + recover 2,604× faster

**Our project:** 500%↑ frequency (1→6/week), 81%↓ lead time (32.5→6.1 min), 83%↓ failure (25%→4.2%), 77%↓ MTTR (48→11 min) — **SAME direction as DORA, smaller magnitude because single-site study vs global best vs worst — proves CREDIBLE and consistent**

Industry standard: Netflix 4,000 deploys/day, Amazon every 11 seconds — same principles implemented here with free tools

---

## 🤝 Contributions to Knowledge

1. Empirical demonstration of secure CI/CD for healthcare in resource-constrained setting — under-represented area
2. Concrete, reproducible implementation with ZERO cost — 31 tests + SAST + Alpine + Trivy + migration + rollback in ONE workflow — all free
3. Baseline DORA evidence — Manual → Automated yields measurable benefits — real 4-week observation
4. NDPA 2023 compliance blueprint — audit trail automatically as byproduct
5. Proved framework NOT domain-specific — Section 4.6.6, Table 4.12, LIVE DEMOS: Hospital (hamzaezzine, 9 tests) + Banking (saadmk11, 7 tests), same pipeline, both pass, 99% reusable — GENERAL reusable pattern

---

## 📞 Contact

**Obademi Kehinde | 190407047 | Department of Systems Engineering | Faculty of Engineering | 2026**

**GitHub:** https://github.com/Khenidice/secure-cicd-healthcare

**Thesis:** 80 pages, 14 tables, 6 figures, real logs, real artifacts, transferability proved with two real repos

---

## 📄 License

This project is for academic purposes — Final Year Project — Systems Engineering — 2026

**All tools used are free and open-source — zero licensing cost — can be implemented in ANY Nigerian hospital with internet and laptop**
