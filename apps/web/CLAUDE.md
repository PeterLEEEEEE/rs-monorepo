# CLAUDE.md

This file provides guidance to Claude Code when working with the web app.

## Project Overview

React frontend for the Real Estate Agent chatbot. Built with Vite for fast development and optimized builds.

**Stack**: React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router

## Common Commands

```bash
# Development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Directory Structure

```
apps/web/
├── src/
│   ├── main.tsx           # App entry point (providers setup)
│   ├── App.tsx            # Routes definition
│   ├── index.css          # Tailwind imports, global styles
│   ├── components/        # Reusable UI components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── api/               # API client functions
│   └── types/             # TypeScript type definitions
├── public/                # Static assets
├── vite.config.ts         # Vite configuration
└── package.json
```

## Key Patterns

### API Calls with TanStack Query
```tsx
import { useQuery, useMutation } from '@tanstack/react-query'

// Fetch data
const { data, isLoading } = useQuery({
  queryKey: ['chatRooms'],
  queryFn: () => fetch('/api/chat/room').then(res => res.json())
})

// Mutate data
const mutation = useMutation({
  mutationFn: (message: string) =>
    fetch('/api/chat/room/123/message', {
      method: 'POST',
      body: JSON.stringify({ message })
    })
})
```

### Styling with Tailwind
- Use utility classes directly in JSX
- Dark mode: prefix with `dark:` (e.g., `dark:bg-gray-800`)
- Responsive: prefix with `sm:`, `md:`, `lg:`, `xl:`

## API Proxy

Development server proxies `/api/*` to `http://localhost:8000` (FastAPI backend).

```ts
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## Environment Variables

Create `.env.local` for local overrides:
```
VITE_API_URL=http://localhost:8000
```

Access in code: `import.meta.env.VITE_API_URL`
