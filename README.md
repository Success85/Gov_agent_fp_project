# GovAgent — A Multilingual AI Assistant for Irembo Government Services

**Breaking language and literacy barriers to public-service access in Rwanda.**

GovAgent is a conversational AI assistant that guides Rwandan citizens through government service applications on Irembo — in Kinyarwanda, English, or French — without needing a paid agent or high digital literacy. It simulates the full Irembo application journey: describing a service, collecting requirements, uploading documents, processing payment, and issuing a real approval document by email.

Built by **Group 3**, BSc (Hons) Software Engineering, African Leadership University.

---

## Table of Contents

- [The Problem](#the-problem)
- [What GovAgent Does](#what-govagent-does)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Services Covered](#services-covered)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Seeding the Database](#seeding-the-database)
- [Testing the API](#testing-the-api)
- [Payment Testing (Flutterwave Sandbox)](#payment-testing-flutterwave-sandbox)
- [Known Limitations](#known-limitations)
- [Next Steps](#next-steps)
- [Team](#team)
- [Acknowledgements](#acknowledgements)

---

## The Problem

Rwanda has digitized its government services through Irembo — but most citizens still can't use them directly.

| Statistic | Source |
|---|---|
| 59% of users still rely on a paid agent to use Irembo | Cenfri, 2024 |
| 12.8% national computer literacy (6.6% in rural areas) | NISR, 2024 |
| Rwf 500–2,000 paid per transaction, on top of official fees | — |

The barrier isn't availability — it's literacy and language. GovAgent addresses this directly by letting citizens interact in their own language, in plain conversation, with no agent fee.

---

## What GovAgent Does

1. **Ask** — a citizen describes what they need, in Kinyarwanda, English, or French
2. **Guide** — GovAgent identifies the right service and walks them through every requirement, one question at a time
3. **Collect** — text answers and document uploads, including optional vs. mandatory fields
4. **Pay** — real Flutterwave checkout (sandbox/test mode), with server-side payment verification
5. **Deliver** — a generated PDF approval document, emailed directly to the citizen, with collection instructions

Every response is **grounded** in verified service data stored in the database — the AI answers only from real, structured records, and cannot invent requirements, fees, or steps.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  LAYER 1 · Citizen Interface (Web)           │
│  Chat · Apply · Upload · Pay · Result        │
│  Kinyarwanda / English / French, text/voice  │
└───────────────────┬───────────────────────────┘
                     │ HTTP
┌───────────────────▼───────────────────────────┐
│  LAYER 2 · Backend (FastAPI)                 │
│  ─ API Gateway                               │
│  ─ Grounding + AI Prompt (answers ONLY       │
│    from verified data)                       │
│  ─ Application Flow Manager (conversation    │
│    state machine, tracks progress)           │
│  ─ Payment + Document Generation             │
└───────────────────┬───────────────────────────┘
                     │
┌───────────────────▼───────────────────────────┐
│  LAYER 3 · Storage (PostgreSQL)              │
│  11 tables, seeded with verified Irembo data │
└───────────────────────────────────────────────┘

  LAYER 4 · External services (used, not trained)
  Gemini (grounded LLM) · Flutterwave (payment) · Gmail SMTP (email)
```

The frontend is served directly by the FastAPI backend as static files (same origin — no CORS complexity), so the entire app runs from a single Docker Compose stack.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11), SQLAlchemy, Pydantic |
| Database | PostgreSQL 16 |
| AI | Google Gemini (`gemini-2.5-flash`), grounded prompting — no model training |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Payment | Flutterwave (Inline Checkout v3, sandbox/test mode) |
| Documents | `fpdf2` (PDF generation) |
| Email | Gmail SMTP |
| Containerization | Docker & Docker Compose |
| Version control | Git — branch-per-lane, merged via `integration` branch |

---

## Services Covered

GovAgent currently supports 6 real government services, with requirements and steps sourced from official Irembo process documentation:

1. **Application for National ID** — NIDA, Rwf 500
2. **Birth Record** — registering a new birth, Rwf 1,500
3. **Birth Certificate** — for an existing birth record, Rwf 500
4. **Marriage Declaration** — declaring an upcoming civil marriage, Rwf 500–50,000 (free on Thursdays)
5. **Mutuelle (Community-Based Health Insurance) Renewal** — RSSB, income-tiered fee
6. **Driving License Application** — RNP, Rwf 50,000 (final stage of a multi-step process)

---

## Database Schema

11 tables:

| Table | Purpose |
|---|---|
| `users` | Citizens using the assistant (identified by phone number) |
| `services` | The 6 government services, with fee and processing time |
| `requirements` | Per-service required fields, including upload flags |
| `steps` | Per-service step-by-step instructions |
| `conversations` | Chat sessions, including conversational state (pending confirmations, awaited fields) |
| `messages` | Full chat history per conversation |
| `applications` | A citizen's in-progress or completed application |
| `application_data` | Collected answers per requirement |
| `uploaded_documents` | Citizen-submitted files |
| `payment_transactions` | Payment records (simulated and real Flutterwave) |
| `generated_documents` | Generated PDF approval documents |

---

## Project Structure

```
Gov_agent_fp_project/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── core/           # Settings/config
│   │   ├── db/             # Database session, seed script
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic: flow manager, grounding,
│   │   │                     intent detection, LLM client, payment,
│   │   │                     Flutterwave verification, email service
│   │   └── schemas.py      # Pydantic request/response models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend_folder/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── templates/          # Downloadable forms (e.g. Mutuelle household template)
├── storage/                # Uploaded documents & generated PDFs (gitignored)
├── docker-compose.yml
└── .env                    # Local secrets (gitignored — see below)
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- A [Gemini API key](https://aistudio.google.com/apikey) (free tier available)
- A [Flutterwave](https://dashboard.flutterwave.com) test account (Public + Secret keys)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification)

### Clone and configure

```bash
git clone https://github.com/Success85/Gov_agent_fp_project.git
cd Gov_agent_fp_project
```

Create a `.env` file in the project root (see [Environment Variables](#environment-variables) below).

---

## Environment Variables

Create `.env` in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-xxxxxxxx-X
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-xxxxxxxx-X
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your16charapppassword
```

> **Never commit `.env`.** It's already listed in `.gitignore`. Gemini's daily free-tier quota is tied to the *Google Cloud project*, not just the key — if you hit a `429` quota error, create a new API key under a **new project** in AI Studio rather than reusing the same one.

---

## Running the App

```bash
docker compose up --build -d
```

This starts:
- `gov_agent_db` — PostgreSQL (port `5433` on host)
- `gov_agent_backend` — FastAPI + static frontend (port `8000` on host)

Once running, open:

```
http://localhost:8000/
```

The Swagger API docs are available at `http://localhost:8000/docs`.

---

## Seeding the Database

The database starts empty. Seed it with the 6 services, requirements, steps, and sample users:

```bash
docker compose exec backend python -m app.db.seed
```

Re-run this any time you want to reset to a clean state (it clears and re-seeds all tables).

> **Note:** since this project doesn't yet use Alembic migrations, any model/schema change requires a full reset: `docker compose down -v && docker compose up --build -d && docker compose exec backend python -m app.db.seed`.

---

## Testing the API

Quick health check:

```bash
curl http://localhost:8000/health
```

Start a conversation:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "0788123456", "message": "Nshaka gusaba indangamuntu", "preferred_language": "rw"}'
```

Full endpoint list is available and testable interactively at `/docs`.

---

## Payment Testing (Flutterwave Sandbox)

When the "Pay Now" button appears in the chat, it opens a **real Flutterwave Inline Checkout modal**. Use Flutterwave's official test card:

| Field | Value |
|---|---|
| Card number | `4242 4242 4242 4242` |
| Expiry | `01/31` |
| CVV | `812` |
| PIN | `3310` |
| OTP | `12345` (card) or `123456` (mobile money) |

Payments are verified **server-side** against Flutterwave's Verify Transaction API before being marked successful — the client-side checkout callback alone is never trusted.

On successful payment, GovAgent:
1. Generates a PDF approval document (via `fpdf2`)
2. Sends a custom confirmation email (via Gmail SMTP) with the PDF attached
3. Displays a warm, AI-generated closing message with real reference numbers and collection instructions

---

## Known Limitations

This is a proof-of-concept, built to demonstrate feasibility — not a production system. Honest current gaps:

- **No live Irembo integration.** Irembo has no public API; this project simulates the full flow using verified but independently-sourced data.
- **No user authentication.** Citizens are identified by phone number only — no login/signup or session security.
- **Limited input validation.** Fields like National ID numbers and district/sector names are currently accepted as free text; format and real-world validation (e.g. against actual Rwandan administrative divisions) is not yet enforced.
- **Language consistency.** Kinyarwanda and English content is grounded in parallel translated data; French responses currently rely on live AI translation rather than pre-verified parallel content, which can introduce minor inconsistencies.
- **No database migrations.** Schema changes currently require a full reset rather than an incremental migration.

---

## Next Steps

- Expand verified data coverage to additional Irembo services
- Add real Kinyarwanda voice input/output (speech-to-text, text-to-speech)
- Add format validation for National IDs and real administrative-division name matching
- User testing with real citizens
- Pursue an official Irembo/government data partnership

---

## Team

**Group 3** — BSc (Hons) Software Engineering, African Leadership University

- Success Ituma
- Henriette Iraguha
- Moreen Muthoni
- Alvin Njoroge
- Davy Dushimiyimana

---

## Acknowledgements

Thanks to our facilitator for guidance throughout this project, and to African Leadership University.

**References:**
- Cenfri (2024). *Digital access to services in Rwanda.*
- NISR (2024). *ICT & literacy statistics.*
- Irembo Ltd.; NIDA; MINALOC — for public process documentation referenced during data collection.