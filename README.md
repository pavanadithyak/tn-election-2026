# Tamil Nadu 2026 Election Forecast

A data-driven, static HTML forecast site for the 2026 Tamil Nadu Legislative Assembly election. Built with pure HTML, CSS, and vanilla JavaScript — zero build step, ready for GitHub Pages.

## Features

- **Hero Section** — 100vh landing with animated entry and parallax watermark
- **Summary Stats** — Key metrics (6.3Cr+ voters, 22% youth, 42 swing seats)
- **Sankey Visualization** — Seat flip flows between parties (143 total flips)
- **Regional Dashboard** — Interactive region selector with demographic/economic views
- **Vote Share Analysis** — 2021 vs 2026 comparison bars across all major parties
- **Priority Issues** — Issue grid (Jobs, Infrastructure, Education, Welfare)
- **Editorial Insights** — Three editorial cards with hover effects
- **Responsive** — Mobile-first with Tailwind-standard breakpoints

## Data Sources

- 2021 Tamil Nadu election results (ECI)
- 2026 exit polls and projections
- Regional demographic and economic indices

## Tech Stack

- HTML5 + CSS3 (all styling inline)
- Vanilla JS (IntersectionObserver for scroll-reveal, data injection via fetch)
- Google Fonts (Playfair Display, Hanken Grotesk)
- Material Symbols Outlined
- GitHub Pages (no build step)

## File Structure

```
/
├── index.html           # Main page — all sections merged
├── js/
│   ├── data.js          # Fetches JSON, injects into DOM
│   └── interactions.js  # Scroll reveal, toggles, parallax, hover effects
├── data/
│   ├── metadata.json
│   ├── flip_flows.json
│   ├── seats_by_region.json
│   └── vote_share_comparison.json
└── README.md
```

## Live Site

[https://pavanadithyak.github.io/tn-election-2026/](https://pavanadithyak.github.io/tn-election-2026/)

## License

MIT
