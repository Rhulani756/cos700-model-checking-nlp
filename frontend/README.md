<<<<<<< HEAD
# Frontend 

Student-facing web interface for submitting C++ programs and viewing pedagogical feedback. Built with Next.js (App Router), TypeScript, and Tailwind CSS.

---

## Stack

| Tool | Purpose |
|---|---|
| Next.js 14 (App Router) | Framework |
| TypeScript | Language |
| Tailwind CSS | Styling |

---

## Structure

```
frontend/
├── public/                  # Static assets
├── src/
│   └── app/
│       ├── layout.tsx       # Root layout
│       ├── page.tsx         # Landing page / submission form
│       ├── results/
│       │   └── page.tsx     # Feedback display page
│       └── globals.css
├── .env.local               # Environment variables (not committed)
├── next.config.js
├── tsconfig.json
└── package.json
```

---

## Pages

| Route | Description |
|---|---|
| `/` | Student submission form — accepts a C++ file, tool selection, and feedback preferences |
| `/results` | Displays generated pedagogical feedback returned from the backend |

---

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend running on `http://localhost:8000`

### Install Dependencies

```bash
npm install
```

### Environment Variables

Create a `.env.local` file in this directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Development Server

```bash
npm run dev
```

The app runs on [http://localhost:3000](http://localhost:3000).

---

## Connecting to the Backend

All API calls go through the FastAPI backend. The base URL is set via `NEXT_PUBLIC_API_URL` in `.env.local`. Example:

```typescript
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/feedback`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});
```

To verify the backend is reachable before making requests:

```typescript
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
const data = await res.json(); // { status: "ok" }
```

---

## Notes

- `.env.local` is excluded from version control, do not commit it.
- `node_modules/` and `.next/` are excluded via `.gitignore`.
- The frontend does not interact with the pipeline or model checkers directly, all processing goes through the backend.

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
=======
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
>>>>>>> origin/feature/ui+pipeline
