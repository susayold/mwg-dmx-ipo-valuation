# Web application

This folder contains the typed React/Vinext version of the research presentation.

- `page.tsx` assembles the research narrative.
- `components/ValuationLab.tsx` implements the interactive Bear/Base/Bull SOTP.
- `components/ThreeStatementAnalysis.tsx` renders comparative statements,
  reconciliation bridges, working-capital schedules and earnings-quality
  analysis.
- `data/case-data.ts` keeps public facts, status labels, dates and source IDs together.
- `data/three-statement-analysis.json` is the generated, versioned analysis
  payload shared with the workbook and downloadable artifacts.
- `layout.tsx` defines metadata and social-card behavior.
- `globals.css` contains the presentation design system.

The recruiter-facing GitHub Pages site uses the root `index.html`; this application is retained to demonstrate component architecture, type-safe case data and server rendering.
