# CLAUDE.md

React frontend for the Real Estate Agent chatbot.

**Stack**: React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router

## Commands

```bash
npm run dev      # Dev server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview build
npm run lint     # ESLint
```

## Structure

```
src/
├── main.tsx      # Entry point, providers
├── App.tsx       # Routes
├── index.css     # Tailwind
├── components/   # UI components
├── pages/        # Page components
├── hooks/        # Custom hooks
└── api/          # API client
```

## API Proxy

Dev server proxies `/api/*` to `http://localhost:8000` (FastAPI).
