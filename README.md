# Portal Starter — Seventh Sense AI

A ready-to-go starter template for building product portals with Seventh Sense branding. Clone it, customize the product-specific pages, and ship — the boilerplate is already done.

## Why This Exists

Every new Seventh Sense product portal needs the same foundation: user signup, login, email verification, forgot/reset password, a branded landing page, and a dashboard shell. Building these from scratch each time is repetitive and error-prone.

This starter provides all of that out of the box so teams can skip straight to building the product-specific features.

## What's Included

- **Branded landing page** with hero, features grid, how-it-works section, and footer — all using Seventh Sense brand colors, fonts, and assets
- **Full auth flows** — registration, login, email verification, forgot password, and password reset with token-based links
- **Dashboard shell** — top nav, left nav, overview page, and profile page with a protected route guard
- **Dark/light theme** toggle with consistent styling across both modes
- **Curtain loading animation** matching the seventhsense.ai website
- **Production build pipeline** — single script to build the frontend and serve it from the backend

## Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Frontend | Angular 21, Tailwind CSS 4, TypeScript           |
| Backend  | FastAPI, SQLAlchemy (async), Pydantic            |
| Database | PostgreSQL (via asyncpg)                         |
| Auth     | JWT (PyJWT), bcrypt password hashing             |
| Email    | SendGrid (verification & password reset emails)  |
| Server   | Uvicorn (serves both API and SPA static files)   |

## Project Structure

```
portal-starter/
├── frontend/               # Angular 21 SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── pages/    # Landing, Dashboard, Verify Email
│   │   │   │   └── common/   # TopNav, LeftNav shared components
│   │   │   └── services/     # Auth, Theme services
│   │   ├── styles.css      # Tailwind config & global styles
│   │   └── index.html
│   └── public/images/      # Logos, icons, hero graphics
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── api/            # REST API routes
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic
│   │   └── middleware/     # Custom middleware
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── .env                # Environment variables (not committed)
├── build.sh                # Build frontend only
├── build-and-run.sh        # Build frontend + start backend
└── reset-db.sh             # Drop & recreate database
```

## Getting Started

### Prerequisites

- **Node.js** (v20+) and npm
- **Python** 3.11+
- **PostgreSQL** running locally
- **SendGrid** API key (for email features)

### Database Setup

```sql
CREATE USER portaluser WITH PASSWORD '!@$portaluserPassword123';
CREATE DATABASE portaluserdb OWNER portaluser;
```

### Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://portaluser:!@$portaluserPassword123@localhost/portaluserdb
SECRET_KEY=your-secret-key-here
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Quick Start

```bash
./build-and-run.sh
```

This installs dependencies, builds the frontend, copies it to the backend, runs migrations, and starts the server at `http://localhost:8000`.

### Manual Setup

```bash
# Frontend
cd frontend && npm install && npx ng build

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp -r ../frontend/dist/frontend/browser/* static/
PYTHONPATH=. alembic upgrade head
uvicorn app.main:app --reload
```

### Development (frontend only)

```bash
cd frontend && npm start
```

Runs at `http://localhost:4200` with hot reload.

## Customizing for a New Product

1. **Update landing page content** — edit `frontend/src/app/components/pages/landing/landing.ts` to change the hero headline, feature cards, and how-it-works steps
2. **Add product pages** — create new components under `frontend/src/app/components/pages/dashboard/` and add routes in `app.routes.ts`
3. **Extend the left nav** — add links in `frontend/src/app/components/common/left-nav/left-nav.html`
4. **Add API endpoints** — create new route files under `backend/app/api/`
5. **Brand tweaks** — colors and fonts are defined as CSS variables in `frontend/src/styles.css` under the `@theme` block

## Helper Scripts

| Script             | Description                                        |
| ------------------ | -------------------------------------------------- |
| `build.sh`         | Build frontend and copy to `backend/static/`       |
| `build-and-run.sh` | Build, install deps, migrate, and start the server |
| `reset-db.sh`      | Drop and recreate the database, re-run migrations  |
