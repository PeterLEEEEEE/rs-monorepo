# Web - React Frontend

Real Estate Agent chatbot frontend.

## Stack

- React 19
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- React Router
- Zustand (state management)

## Structure

```
src/
├── main.tsx      # Entry point, providers
├── App.tsx       # Routes
├── index.css     # Tailwind
├── components/   # UI components
├── pages/        # Page components
├── hooks/        # Custom hooks
├── stores/       # Zustand stores
└── api/          # API client
```

## Quick Start

### Using Docker

```bash
# From monorepo root
docker compose up -d web
```

**URL**: http://localhost:80

### Local Development

```bash
cd apps/web

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Dev URL**: http://localhost:5173

## Commands

```bash
npm run dev      # Dev server with HMR
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # ESLint
```

## API Proxy

Development server proxies API requests:

- `/api/*` → `http://localhost:8000` (FastAPI)

Configured in `vite.config.ts`.

## Environment Variables

Create `.env.local` for local overrides:

```bash
VITE_API_URL=http://localhost:8000
```

## Building for Production

```bash
npm run build
```

Output is in `dist/` directory, served by nginx in Docker.
