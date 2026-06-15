# Buidlpad Design System

Built from the **Invest, Boosted Earn (HODL) v2.0** Figma file and its
companion **V2.0 Shadcn Design System (CORE Library)**.

## What is Buidlpad?

**Buidlpad** is a crypto launch and earn platform that lets long-term
community members take early, transparent positions in pre-token crypto
projects — with valuation and vesting terms historically reserved for VCs.

Two core surfaces:

1. **Invest** — project list, Public Sale pages (upcoming / ongoing /
   ended), KYC, contribution, claim. Partners: Sahara AI, Lombard,
   Solayer, Nomad Capital, Falcon, Momentum.
2. **Boosted Earn (HODL)** — pre-TGE / post-TGE staking where stakers
   unlock boosters by holding tokens through Buidlpad.

A third experimental surface, **Surf.ai**, exists in the Figma but is
not a shipped product.

---

## Basis — shadcn/ui + Tailwind

The Figma source ships as a **shadcn/ui + TailwindCSS** system with a
three-layer token model:

1. **TailwindCSS 2026** — raw palette (Zinc, Neutral, hues)
2. **Theme 2026** — semantic aliases (`primary`, `card`, `muted`,
   `popover`, `border`, `destructive`, `success`…)
3. **Mode 2026** — light / dark mapping, toggled via `data-theme`

App code consumes **mode tokens only** (`var(--primary)`,
`var(--card)` …), never raw palette values. Component class names
track shadcn defaults (`.btn`, `.card`, `.dialog-*`, `.tabs-list`,
`.badge`…) so the sheet ports directly to Tailwind `@apply` rules.

---

## Content fundamentals

**Voice.** Plain-spoken finance with a builder bias — "participate,"
"contribute," "boost," "skin in the game." No crypto-bro cadence, no
emoji, no exclamation points.

**Pronouns.** Second-person imperative. First person is never used.

**Casing.** Sentence case everywhere — buttons, headings, toasts —
except brand/partner names and product names (Boosted Earn). **TGE,
KYC, FDV, TVL** stay upper-case.

**Dates.** `dd/mmm/yy HH:mm:ss UTC` (e.g. `14/Mar/26 12:00:00 UTC`).

**Numerals.** Thousands-comma, `$` prefix, `(1.5%)` in parens. Chivo
Mono with tabular-nums in the `.dl-grid dd` cells.

**Icons.** Lucide CDN, stroke 1.5, 20 px default. No emoji anywhere.

---

## Visual foundations

### Typography
**Inter** for body and UI (400/500/600/700). **Chivo Mono** for all
numerals — amounts, wallet addresses, counters, dates, ticker chips.
Ten-step type scale (`--text-xs` 12 → `--text-6xl` 56). Tight tracking
on display (`--tracking-tight`, `--tracking-tighter`).

### Color
- **Zinc palette** is the neutral spine with three Figma-only
  intermediates: `zinc-250 #d7d7d7`, `zinc-450 #767676`,
  `zinc-850 #1f1f1f`.
- **Semantic tokens** — `--primary`, `--card`, `--background`,
  `--muted`, `--accent`, `--border`, `--input`, `--ring`, `--popover`,
  `--sidebar`, `--destructive`, `--success`, each paired with a
  matching `-foreground`.
- **Light mode** = Invest surface default. **Dark mode** = Boosted
  Earn default. Switch:
  `document.documentElement.setAttribute('data-theme','dark')`.
- Partner accents (Lombard pink, Falcon neon, Momentum blue…) are
  NOT in the core token layer. Apply locally to a project's logo and
  primary CTA only — never override `--primary` globally.

### Radius & shadow
`--radius` is `10 px`. Buttons/inputs `--radius-md` (6 px), cards and
dialogs `--radius-xl` (12 px), pills `--radius-full`. Shadows are
shadcn's `--shadow-sm` (card), `--shadow-md` (hover elevation),
`--shadow-2xl` (dialog).

### Layout
4-px spacing grid, 35 tokens from `--sp-0` through `--sp-96` (0 →
384 px). Content wrap 1200–1280 px centered on 1920 px frames.
Generous side margins — feels like a fintech ops console, not a
consumer app.

### Interaction
150 ms color/opacity transitions only. No springs, no scale-up
pulses. Focus rings use `--ring` (2 px outside, 2 px offset). Dialog
scrim `rgba(0,0,0,0.5)` + `backdrop-filter: blur(--backdrop-blur-sm)`
— the only place blur shows up.

### Anti-patterns
- No gradient-bloat cards
- No colored left-border accent cards
- No emoji as icons
- No overridden global `--primary` per partner

---

## Index

Root:
- `README.md` — this file
- `SKILL.md` — portable skill manifest (Claude Code / Agent Skills)
- `colors_and_type.css` — three token layers + type scale + motion
- `components.css` — minimal shadcn component sheet
- `assets/` — Buidlpad icon + wordmark, light and dark
- `preview/` — small HTML review cards per token group
- `ui_kits/invest/` — Invest surface (light, list + detail + login)
- `ui_kits/earn/` — Boosted Earn surface (dark, pools + stake flow)

Each UI kit ships with `{README.md, index.html, *.jsx}` and runs in
the browser with no build step.

---

## Caveats

- **Fonts.** Self-hosted. `fonts/Inter_18pt-*.ttf` and `fonts/ChivoMono-*.ttf`
  loaded via `@font-face` in `colors_and_type.css`. No Google Fonts CDN required.
- **Partner logos** (Lombard, Sahara, Solayer…) not in the upload set
  — UI kits use placeholders. Swap in real SVGs when available.
- **Partner accent hexes** live in the partner Figma libraries, not
  the core V2.0 token sheet — treated as project-local one-offs.
- **Icons.** Lucide stands in for the Figma's icon set (shadcn
  default). Visually identical in most cases, possibly off by stroke
  detail.
- **Semantic token hex values.** Mode 2026 references in the Figma
  source point to palette entries but don't enumerate every hex; I
  used the shadcn/ui default Zinc mappings where a value wasn't
  explicit. Flag for a Figma variables export if pixel-exact values
  matter.
