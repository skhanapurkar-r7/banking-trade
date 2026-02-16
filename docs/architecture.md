# Trade Store Architecture

## Overview

Trade Store is a full-stack application built with a clear separation between frontend and backend, following modern best practices and architectural patterns.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Pages      │  │  Components  │  │   Services   │  │
│  │              │  │              │  │              │  │
│  │ - TradesPage │  │ - DataGrid   │  │ - API Client │  │
│  │ - AboutPage  │  │ - FormDialog │  │ - Validation │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   API Layer  │  │   Services   │  │ Repositories │  │
│  │              │  │              │  │              │  │
│  │ - Routes     │  │ - Business   │  │ - Data       │  │
│  │ - Validation │  │   Logic      │  │   Access     │  │
│  │ - Error      │  │ - Rules      │  │ - SQLAlchemy │  │
│  │   Handling   │  │   Validation │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   SQLite DB  │
                    └──────────────┘
```

## Backend Architecture (3-Tier)

### 1. API Layer (`app/api/`)
- **Responsibility**: HTTP request/response handling
- **Components**:
  - Route definitions
  - Request validation
  - Response formatting
  - Error handling
  - API versioning (`/api/v1/`)

### 2. Service Layer (`app/services/`)
- **Responsibility**: Business logic and rules
- **Components**:
  - Trade validation
  - Version conflict detection
  - Maturity date validation
  - Business rule enforcement

### 3. Repository Layer (`app/repositories/`)
- **Responsibility**: Data access and persistence
- **Components**:
  - Database operations (CRUD)
  - Query building
  - SQLAlchemy ORM interactions
  - Data filtering and sorting

### Core Modules (`app/core/`)
- Configuration management
- Logging setup
- Custom exceptions
- Shared utilities

## Frontend Architecture

### Component Structure
```
src/
├── components/       # Reusable UI components
│   ├── Layout.tsx
│   ├── TradeDataGrid.tsx
│   └── TradeFormDialog.tsx
├── pages/           # Page-level components
│   ├── TradesPage.tsx
│   └── AboutPage.tsx
├── services/        # API and external services
│   └── api.ts
├── types/           # TypeScript type definitions
│   └── trade.ts
├── utils/           # Utility functions
│   ├── validation.ts
│   └── dateUtils.ts
└── theme/           # MUI theme configuration
    └── theme.ts
```

### State Management
- **Server State**: TanStack Query (React Query)
  - Caching
  - Automatic refetching
  - Optimistic updates
- **UI State**: React local state
  - Form state (React Hook Form)
  - Dialog visibility
  - Theme preference

## Data Flow

### Create Trade Flow
```
1. User fills form → TradeFormDialog
2. Form validation → Zod schema
3. Submit → API call (tradeApi.createTrade)
4. Backend validation → TradeService
5. Version check → TradeRepository
6. Save to DB → SQLAlchemy
7. Response → Update React Query cache
8. UI update → DataGrid refresh
```

### Version Conflict Handling
```
1. User submits trade with version X
2. Service checks existing versions
3. If version < latest: Reject with 409
4. If version = latest: Show replace dialog
5. If version > latest: Accept and create
```

## Security Considerations

### Backend
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Error message sanitization

### Frontend
- XSS prevention (React auto-escaping)
- Input validation (Zod)
- Type safety (TypeScript)
- Dependency vulnerability scanning

## Testing Strategy

### Backend Tests
- **Unit Tests**: Service and repository logic
- **Integration Tests**: API endpoints
- **Coverage Target**: >70%

### Frontend Tests
- **Unit Tests**: Components and utilities
- **Integration Tests**: User flows
- **E2E Tests**: Critical paths with Playwright
- **Coverage Target**: >80%

## Deployment Architecture

```
GitHub Repository
      │
      ├─→ GitHub Actions (CI)
      │   ├─→ Backend Pipeline
      │   │   ├─→ Lint (Black, isort, Flake8)
      │   │   ├─→ Test (Pytest)
      │   │   └─→ Security Scan
      │   │
      │   └─→ Frontend Pipeline
      │       ├─→ Lint (ESLint, Prettier)
      │       ├─→ Type Check (TypeScript)
      │       ├─→ Test (Vitest, Playwright)
      │       ├─→ Build
      │       └─→ Vulnerability Scan (npm audit)
      │
      └─→ Deployment (Manual/CD)
          ├─→ Backend: Docker/Cloud
          └─→ Frontend: Static hosting
```

## Performance Optimizations

### Backend
- Database indexing on frequently queried fields
- Pagination for large datasets
- Connection pooling

### Frontend
- Code splitting (React.lazy)
- Memoization (useMemo, useCallback)
- Virtual scrolling in DataGrid
- Debounced search
- React Query caching

## Scalability Considerations

### Current Implementation
- SQLite for development/demo
- Single server deployment

### Production Recommendations
- PostgreSQL/MySQL for production
- Redis for caching
- Load balancer for multiple instances
- CDN for frontend assets
- Separate API and database servers

## Monitoring and Logging

### Backend
- Structured logging with Python logging module
- Request/response logging
- Error tracking
- Performance metrics

### Frontend
- Console logging (development)
- Error boundaries
- Sentry integration ready
- Web Vitals tracking ready
