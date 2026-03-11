# Forking Portal Starter for a New Product

This guide walks you through creating a new product portal from the portal-starter base.

## 1. Create Your Fork

```bash
# Fork on GitHub, then clone
git clone git@github.com:your-org/your-product-portal.git
cd your-product-portal

# Track the base repo for future updates
git remote add upstream git@github.com:SeventhSenseAI/portal-starter.git
```

## 2. Rebrand

### Colors & Fonts

Edit **one file** — `frontend/src/styles/theme.css`:

```css
@theme {
  --color-brand: #YOUR_BRAND;
  --color-brand-dark: #YOUR_BRAND_DARK;
  --color-brand-light: #YOUR_BRAND_LIGHT;
  --color-gold: #YOUR_ACCENT;
  --color-nav: #YOUR_NAV_BG;
  --color-nav-border: #YOUR_NAV_BORDER;
  --font-heading: "Your Heading Font", system-ui, sans-serif;
  --font-body: "Your Body Font", system-ui, sans-serif;
}
```

### Logo & Images

Replace files in `frontend/public/images/`:

| File | Purpose |
|------|---------|
| `logos-white.svg` | Navbar logo (white, for dark nav background) |
| `emblem-gradient.svg` | Footer emblem |
| `masked-woman.png` | Hero graphic |
| `network-pattern.svg` | Background pattern (hero, dashboard) |
| `network-pattern-white.svg` | Background pattern (CTA banner) |
| `certi-1.png`, `cert2.png`, `certi-3.png` | Trust badges |
| `footerbg.jpg` | Footer background texture |

### Landing Page Content

Edit `frontend/src/app/components/pages/landing/landing.ts` to update:
- `features` array — card icons, titles, descriptions
- `steps` array — how-it-works content

Edit `frontend/src/app/components/pages/landing/landing.html` to update:
- Hero headline, subtitle, and CTA text
- CTA banner text
- Footer copy

## 3. Add Product Features

### Frontend Pages

Create components under `frontend/src/app/product/pages/`:

```
app/product/
├── product.routes.ts
└── pages/
    └── analytics/
        ├── analytics.ts
        └── analytics.html
```

Register them in `frontend/src/app/product/product.routes.ts`:

```typescript
import { Routes } from '@angular/router';

export const productRoutes: Routes = [
  {
    path: 'analytics',
    loadComponent: () => import('./pages/analytics/analytics').then(m => m.Analytics),
  },
];
```

These routes are automatically loaded as children of `/dashboard`.

### Left Nav Links

Add navigation links in `frontend/src/app/components/common/left-nav/left-nav.html`.

### Backend API Routes

Create route modules under `backend/app/api/product/`:

```python
# backend/app/api/product/analytics.py
from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
async def get_summary(current_user=Depends(get_current_user)):
    return {"data": "..."}
```

Register them in `backend/app/api/product/router.py`:

```python
from fastapi import APIRouter
from app.api.product.analytics import router as analytics_router

router = APIRouter(prefix="/product", tags=["product"])
router.include_router(analytics_router)
```

All product routes are served under `/api/product/`.

### Backend Models

Add SQLAlchemy models under `backend/app/models/product/`:

```python
# backend/app/models/product/widget.py
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Widget(Base):
    __tablename__ = "widgets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
```

Import them in `backend/app/models/product/__init__.py`:

```python
from app.models.product.widget import Widget  # noqa: F401
```

Alembic picks these up automatically. Generate a migration:

```bash
cd backend
PYTHONPATH=. alembic revision --autogenerate -m "add widgets table"
PYTHONPATH=. alembic upgrade head
```

### Backend Schemas & Services

Add Pydantic schemas in `backend/app/schemas/product/` and business logic in `backend/app/services/product/`.

## 4. Pull Base Updates

When the base repo has improvements (auth fixes, UI polish, new shared features):

```bash
git fetch upstream
git merge upstream/main
```

Conflicts are unlikely if you kept product code in `product/` directories. If they occur, they'll typically be in:
- `app.routes.ts` — re-add the `...productRoutes` spread
- `styles/theme.css` — keep your brand values
- `left-nav.html` — keep your nav links

## 5. What the Base Owns (avoid editing)

| Layer | Files |
|-------|-------|
| Auth | `services/auth.ts`, `services/api.ts`, `guards/`, `interceptors/` |
| Auth UI | Landing page modals (login, register, forgot, reset, email-sent) |
| Auth API | `backend/app/api/auth.py`, `backend/app/api/users.py` |
| User model | `backend/app/models/user.py`, `backend/app/schemas/user.py` |
| Layout | `top-nav/`, `left-nav/` (structure), `dashboard.ts` (shell) |
| Infra | `database.py`, `config.py`, `middleware/`, `alembic/env.py` |
| Styles | `styles.css` (component styles — not `theme.css`) |

## 6. Environment Setup

Copy and configure `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/yourdb
SECRET_KEY=your-secret-key
SENDGRID_API_KEY=your-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
BASE_URL=http://localhost:8000
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Then:

```bash
./build-and-run.sh
```
