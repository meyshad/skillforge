---
name: web-performance
description: Diagnoses and improves web performance and Core Web Vitals (LCP, INP, CLS) by measuring first with Lighthouse and bundle analysis, then applying targeted fixes for images, JavaScript size, rendering, fonts, caching and server response time. Use when the user says a site is slow, asks to improve Lighthouse or PageSpeed scores, Core Web Vitals, bundle size, load time or responsiveness.
---

# Web Performance

**Measure → find the biggest bottleneck → fix → measure again.** Never optimize blind.

## 1. Measure
```bash
npx lighthouse https://localhost:3000 --preset=desktop --view
npx lighthouse https://localhost:3000 --form-factor=mobile --throttling-method=simulate --view
```
- Test a **production build** (`npm run build && npm run start`), never the dev server.
- Real-user data beats lab data: check CrUX/PageSpeed Insights for public sites, or the `web-vitals` library in the app.
- Bundle analysis: `npx vite-bundle-visualizer`, `@next/bundle-analyzer`, `webpack-bundle-analyzer`, or `npx source-map-explorer dist/**/*.js`.

Targets (75th percentile, mobile):

| Metric | Good | What it measures |
|---|---|---|
| **LCP** | ≤ 2.5 s | When the main content appears |
| **INP** | ≤ 200 ms | How fast the page responds to input |
| **CLS** | ≤ 0.1 | How much the layout jumps |
| TTFB | ≤ 0.8 s | Server/CDN response time |

## 2. Fix by metric

### LCP (slow main content)
- Identify the LCP element (Lighthouse names it). Usually a hero image or heading.
- Hero image: modern format (AVIF/WebP), correct dimensions with `srcset`/`sizes`, `fetchpriority="high"`, **not** `loading="lazy"`; `<link rel="preload">` if discovered late (CSS background, JS-rendered).
- Remove render-blocking resources: inline critical CSS, `defer` scripts, load third-party scripts after interaction or with `async`.
- Slow TTFB: cache at the CDN/edge, SSG/ISR for static content, fix slow DB queries, enable compression (Brotli).
- Client-rendered pages: SSR or prerender the above-the-fold content.

### INP (sluggish interactions)
- Find long tasks (> 50 ms) in the Performance panel. Break them up (`await scheduler.yield()` or `setTimeout` chunks), move heavy work to a Web Worker.
- Ship less JS: code-split routes and heavy components (`import()`, `React.lazy`), remove unused dependencies, replace heavy libraries (moment → date-fns/Temporal, lodash → native).
- Avoid unnecessary re-renders (memoization, state colocation, virtualization for long lists).
- Debounce expensive input handlers; give immediate visual feedback before heavy work.

### CLS (layout shift)
- Always set `width`/`height` (or `aspect-ratio`) on images, videos, iframes and ad slots.
- Reserve space for late content (banners, embeds, skeletons with fixed size).
- Fonts: `font-display: swap` (or `optional`) + `size-adjust`/fallback metric overrides; preload the critical font file; self-host and subset.
- Animate `transform`/`opacity`, never `top`/`height`.

## 3. Always-good hygiene
- Long-lived cache headers for hashed assets (`Cache-Control: public, max-age=31536000, immutable`), short for HTML.
- HTTP/2 or HTTP/3, Brotli compression, a CDN.
- `loading="lazy"` for below-the-fold images and iframes; `preconnect` to critical third-party origins.
- Set a **performance budget** in CI (Lighthouse CI or `size-limit`) so regressions fail the build.

## 4. Report
```markdown
| Metric | Before | After | Target |
|---|---|---|---|
| LCP (mobile) | 4.1 s | 2.2 s | ≤ 2.5 s |
| JS shipped | 612 KB | 288 KB | — |

Changes (highest impact first):
1. Hero image → AVIF + fetchpriority (−1.4 s LCP)
2. Lazy-loaded chart library on dashboard route (−260 KB JS)
```
Show measured numbers from real runs only. Lab scores vary between runs; take the median of 3–5.
