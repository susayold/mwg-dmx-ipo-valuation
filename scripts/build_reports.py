from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
FACTS_PATH = ROOT / "data" / "processed" / "dmx_q1_2026_financial_facts.csv"
SOURCES_PATH = ROOT / "data" / "source_registry.csv"
DOWNLOADS = ROOT / "public" / "downloads"
REPORTS = ROOT / "reports"

INK = colors.HexColor("#101B17")
LIME = colors.HexColor("#D7FF5F")
CORAL = colors.HexColor("#FF7358")
PAPER = colors.HexColor("#F4F0E7")
MUTED = colors.HexColor("#67736C")


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    observed: str
    tolerance: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fact_value(
    rows: list[dict[str, str]], statement: str, line_item: str, period: str
) -> int:
    matches = [
        int(row["value_vnd"])
        for row in rows
        if row["statement"] == statement
        and row["line_item"] == line_item
        and row["period"] == period
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one fact for {statement}/{line_item}/{period}; got {len(matches)}"
        )
    return matches[0]


def build_checks(rows: list[dict[str, str]], sources: list[dict[str, str]]) -> list[Check]:
    keys = [
        (row["statement"], row["line_item"], row["period"]) for row in rows
    ]
    duplicates = len(keys) - len(set(keys))

    assets = fact_value(rows, "balance_sheet", "total_assets", "2026-03-31")
    liabilities = fact_value(rows, "balance_sheet", "total_liabilities", "2026-03-31")
    equity = fact_value(rows, "balance_sheet", "total_equity", "2026-03-31")
    bs_difference = assets - liabilities - equity

    revenue = fact_value(rows, "income_statement", "revenue", "2026-03-31")
    cogs = fact_value(rows, "income_statement", "cogs", "2026-03-31")
    gross_profit = fact_value(rows, "income_statement", "gross_profit", "2026-03-31")
    gp_difference = revenue + cogs - gross_profit

    opening_cash = fact_value(rows, "cash_flow_statement", "opening_cash", "2026-03-31")
    cash_change = fact_value(
        rows, "cash_flow_statement", "net_change_in_cash", "2026-03-31"
    )
    fx_effect = fact_value(rows, "cash_flow_statement", "fx_cash_effect", "2026-03-31")
    ending_cash = fact_value(rows, "cash_flow_statement", "ending_cash", "2026-03-31")
    cash_difference = opening_cash + cash_change + fx_effect - ending_cash

    source_ids = {row["source_id"] for row in rows}
    source_complete = len(source_ids) == 1 and all(
        source_id.startswith("DMX_Q1_2026_DATA_PACK_XLSX_")
        for source_id in source_ids
    )
    registry_hashes = [
        row["sha256"] for row in sources if row.get("status") == "downloaded_verified"
    ]

    return [
        Check("Curated fact rows", len(rows) == 210, str(len(rows)), "210"),
        Check("Duplicate natural keys", duplicates == 0, str(duplicates), "0"),
        Check("Balance-sheet equation", bs_difference == 0, f"{bs_difference:,} VND", "0 VND"),
        Check("Gross-profit equation", gp_difference == 0, f"{gp_difference:,} VND", "0 VND"),
        Check("Cash-flow bridge", cash_difference == 0, f"{cash_difference:,} VND", "0 VND"),
        Check("Full source hash on each fact", source_complete, str(len(source_ids)), "1 source"),
        Check(
            "Verified source registry",
            len(registry_hashes) >= 20 and all(len(value) == 64 for value in registry_hashes),
            f"{len(registry_hashes)} files",
            "at least 20",
        ),
    ]


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(18 * mm, 12 * mm, "MWG AFTER THE DMX IPO · INDEPENDENT WORK SAMPLE")
    canvas.drawRightString(192 * mm, 12 * mm, f"{doc.page}")
    canvas.restoreState()


def build_pdf(output_path: Path):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="MemoTitle",
            parent=styles["Title"],
            fontName="Times-Roman",
            fontSize=30,
            leading=31,
            textColor=INK,
            spaceAfter=12,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MemoH1",
            parent=styles["Heading1"],
            fontName="Times-Roman",
            fontSize=20,
            leading=22,
            textColor=INK,
            spaceBefore=12,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MemoH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=INK,
            spaceBefore=10,
            spaceAfter=6,
            uppercase=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MemoBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=13,
            textColor=INK,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MemoSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7,
            leading=10,
            textColor=MUTED,
        )
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title="MWG After the DMX IPO",
        author="Independent portfolio project",
    )
    story = []

    story.append(Paragraph("EVENT-DRIVEN VALUATION CASE · 13 JULY 2026", styles["MemoSmall"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("MWG After the<br/>DMX IPO", styles["MemoTitle"]))
    story.append(
        Paragraph(
            "IPO bridge, sum-of-the-parts valuation and the value of the non-DMX stub.",
            styles["MemoBody"],
        )
    )
    hero = Table(
        [
            ["VND 13.3tn", "166.4m", "1,267.7m", "~86%"],
            ["gross proceeds", "shares issued", "post-offer shares", "MWG ownership"],
        ],
        colWidths=[41 * mm] * 4,
        rowHeights=[18 * mm, 9 * mm],
    )
    hero.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIME),
                ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                ("FONT", (0, 0), (-1, 0), "Times-Roman", 20),
                ("FONT", (0, 1), (-1, 1), "Helvetica-Bold", 6.5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, INK),
            ]
        )
    )
    story.append(Spacer(1, 6 * mm))
    story.append(hero)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Decision question", styles["MemoH2"]))
    story.append(
        Paragraph(
            "After valuing MWG's post-IPO stake in DMX, what value belongs to Bach Hoa Xanh, "
            "An Khang, AvaKids and parent-level adjustments?",
            styles["MemoH1"],
        )
    )
    story.append(
        Paragraph(
            "<b>Publication gate:</b> this work sample does not publish an investment rating, "
            "target price or observed stub value without a verified share price, price date and "
            "diluted MWG share count.",
            styles["MemoBody"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("1 · Transaction mechanics", styles["MemoH1"]))
    story.append(
        Paragraph(
            "DMX successfully issued 166,438,500 primary shares at VND 80,000. The unallocated "
            "shares were cancelled, so the actual post-offer share count is 1,267,722,000—not "
            "the larger planned count.",
            styles["MemoBody"],
        )
    )
    transaction = [
        ["VND bn except shares", "Planned", "Actual close"],
        ["Shares issued, mn", "179.5004", "166.4385"],
        ["Post-offer shares, mn", "1,280.7839", "1,267.7220"],
        ["Gross proceeds", "14,360.032", "13,315.080"],
        ["Post-money at VND80k", "102,462.712", "101,417.760"],
    ]
    tx_table = Table(transaction, colWidths=[75 * mm, 43 * mm, 43 * mm])
    tx_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7),
                ("FONT", (0, 1), (-1, -1), "Helvetica", 7.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B9B4AA")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(tx_table)
    story.append(Spacer(1, 7 * mm))

    story.append(Paragraph("2 · Perimeter control", styles["MemoH1"]))
    perimeter = [
        ["Inside DMX", "Outside DMX / MWG stub"],
        [
            "TGDD, DMX, TopZone, DMX Technician, Super App, EraBlue 45% JV",
            "Bach Hoa Xanh, An Khang, AvaKids, parent and other assets",
        ],
    ]
    perimeter_table = Table(perimeter, colWidths=[80.5 * mm, 80.5 * mm])
    perimeter_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIME),
                ("BACKGROUND", (1, 0), (1, -1), PAPER),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
                ("FONT", (0, 1), (-1, 1), "Helvetica", 8),
                ("GRID", (0, 0), (-1, -1), 0.5, INK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(perimeter_table)
    story.append(
        Paragraph(
            "EraBlue is equity accounted. A P/E based on NPAT already includes DMX's share of "
            "JV profit and must not add EraBlue again. An FCFF DCF may require a separate JV "
            "value at the equity bridge.",
            styles["MemoBody"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("3 · Latest evidence", styles["MemoH1"]))
    q1_table_data = [
        ["VND bn", "1Q25", "1Q26", "YoY / change"],
        ["Revenue", "25,154", "32,542", "+29.4%"],
        ["Gross profit", "4,526", "6,241", "+37.9%"],
        ["Gross margin", "17.99%", "19.18%", "+119 bps"],
        ["PBT", "1,857", "2,775", "+49.5%"],
        ["NPAT", "1,478", "2,219", "+50.1%"],
        ["CFO", "2,477", "864", "39% of NPAT"],
    ]
    q1_table = Table(q1_table_data, colWidths=[55 * mm, 34 * mm, 34 * mm, 38 * mm])
    q1_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7),
                ("FONT", (0, 1), (-1, -1), "Helvetica", 7.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B9B4AA")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(q1_table)
    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            "<b>Positive signal:</b> revenue growth and margin expansion produced faster NPAT growth.",
            styles["MemoBody"],
        )
    )
    story.append(
        Paragraph(
            "<b>Watchpoint:</b> Q1 operating cash flow was only 39% of NPAT because inventory "
            "increased and payables declined. The model therefore stresses inventory days and "
            "supplier funding instead of forecasting cash as a fixed percentage of earnings.",
            styles["MemoBody"],
        )
    )
    story.append(Paragraph("Six-month operating pulse", styles["MemoH2"]))
    story.append(
        Paragraph(
            "Unaudited 6M26 revenue reached VND 65,279bn, up 31% on the company's stated LFL "
            "basis and equal to 53% of annual guidance. SSSG was 32%; EraBlue reached 261 stores "
            "and reported 92% revenue growth. Q2/H1 financial statements were not available at "
            "the 13 July cut-off.",
            styles["MemoBody"],
        )
    )

    story.append(Paragraph("4 · Management reference case", styles["MemoH1"]))
    forecast = [
        ["VND bn", "2025A LFL", "2026F", "2027F", "2028F", "2029F", "2030F"],
        ["Revenue", "107,000", "122,500", "135,000", "149,000", "164,000", "182,000"],
        ["NPAT", "6,075", "7,350", "8,500", "9,800", "11,300", "13,000"],
        ["Gross margin", "17.1%", "17.5%", "17.8%", "18.0%", "18.3%", "18.4%"],
    ]
    forecast_table = Table(forecast, colWidths=[34 * mm] + [21 * mm] * 6)
    forecast_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 6.2),
                ("FONT", (0, 1), (-1, -1), "Helvetica", 6.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B9B4AA")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(forecast_table)
    story.append(
        Paragraph(
            "These values are management projections, stored separately from independent Bear, "
            "Base and Bull scenarios.",
            styles["MemoSmall"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("5 · Valuation architecture", styles["MemoH1"]))
    story.append(Paragraph("DMX", styles["MemoH2"]))
    story.append(
        Paragraph(
            "The workbook supports FCFF DCF and normalised earnings multiples. The transparent "
            "website lab uses forecast NPAT multiplied by a selected P/E, then applies MWG's "
            "post-IPO ownership.",
            styles["MemoBody"],
        )
    )
    story.append(Paragraph("MWG sum of the parts", styles["MemoH2"]))
    formula = Table(
        [
            ["MWG equity value"],
            ["MWG share of DMX"],
            ["+ non-DMX stub"],
            ["± parent net cash, debt and corporate adjustments"],
        ],
        colWidths=[161 * mm],
    )
    formula.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), LIME),
                ("BACKGROUND", (0, 1), (0, -1), PAPER),
                ("FONT", (0, 0), (0, 0), "Times-Roman", 17),
                ("FONT", (0, 1), (0, -1), "Helvetica-Bold", 9),
                ("BOX", (0, 0), (-1, -1), 0.7, INK),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, INK),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(formula)
    story.append(Spacer(1, 7 * mm))

    story.append(Paragraph("6 · Scenario logic", styles["MemoH1"]))
    scenarios = [
        ["Bear", "Base", "Bull"],
        [
            "Lower SSSG and margin; inventory absorbs cash; lower multiple; larger parent deduction.",
            "Guidance broadly achieved; gradual margin expansion; working capital normalises.",
            "Services and EraBlue outperform; margin expands; cash conversion remains controlled.",
        ],
    ]
    scenario_table = Table(scenarios, colWidths=[53.7 * mm] * 3)
    scenario_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FFD8D0")),
                ("BACKGROUND", (1, 0), (1, -1), LIME),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#DDE4FF")),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
                ("FONT", (0, 1), (-1, 1), "Helvetica", 7.2),
                ("GRID", (0, 0), (-1, -1), 0.5, INK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(scenario_table)
    story.append(Spacer(1, 7 * mm))

    story.append(Paragraph("7 · Catalysts and risks", styles["MemoH1"]))
    catalyst_risk = [
        ["Potential catalysts", "Key risks"],
        [
            "DMX price discovery; H1 statements; debt reduction and interest savings from IPO proceeds; EraBlue unit economics; BHX cash generation.",
            "Demand normalisation; margin reversal; working-capital absorption; expansion before unit economics; persistent holdco discount.",
        ],
    ]
    cr_table = Table(catalyst_risk, colWidths=[80.5 * mm, 80.5 * mm])
    cr_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIME),
                ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#FFD8D0")),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
                ("FONT", (0, 1), (-1, 1), "Helvetica", 7.5),
                ("GRID", (0, 0), (-1, -1), 0.5, INK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(cr_table)
    story.append(PageBreak())

    story.append(Paragraph("8 · Analyst conclusion", styles["MemoH1"]))
    story.append(
        Paragraph(
            "The IPO makes MWG more analyzable, not automatically more valuable. Current evidence "
            "supports continued modelling: revenue growth and margin expansion are strong, while "
            "cash conversion remains the main financial watchpoint.",
            styles["MemoBody"],
        )
    )
    conclusion = Table(
        [
            [
                "VALUE DMX ONCE",
                "KEEP ERABLUE INSIDE DMX",
                "VALUE THE STUB SEPARATELY",
                "PUBLISH ONLY AFTER PRICE-DATE CONTROLS",
            ]
        ],
        colWidths=[40.25 * mm] * 4,
        rowHeights=[24 * mm],
    )
    conclusion.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), INK),
                ("TEXTCOLOR", (0, 0), (-1, -1), LIME),
                ("FONT", (0, 0), (-1, -1), "Helvetica-Bold", 7),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, LIME),
            ]
        )
    )
    story.append(conclusion)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Primary-source discipline", styles["MemoH2"]))
    story.append(
        Paragraph(
            "The repository contains a 29-document source register. Raw issuer files are excluded "
            "from Git because redistribution terms are not explicit; URLs, hashes, periods and "
            "document roles remain committed. The curated Q1 data contains 210 source-tagged facts.",
            styles["MemoBody"],
        )
    )
    story.append(
        Paragraph(
            "Independent educational portfolio project. Public information only. Not investment advice.",
            styles["MemoSmall"],
        )
    )

    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)


def build_validation_html(
    output_path: Path, checks: list[Check], rows: list[dict[str, str]], sources: list[dict[str, str]]
):
    checks_html = "".join(
        "<tr><td>{}</td><td><span class='{}'>{}</span></td><td>{}</td><td>{}</td></tr>".format(
            html.escape(check.name),
            "pass" if check.passed else "fail",
            "PASS" if check.passed else "FAIL",
            html.escape(check.observed),
            html.escape(check.tolerance),
        )
        for check in checks
    )
    overall = all(check.passed for check in checks)
    unique_periods = len({row["period"] for row in rows})
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>MWG-DMX validation report</title>
  <style>
    :root{{--ink:#101b17;--lime:#d7ff5f;--paper:#f4f0e7;--coral:#ff7358}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:14px Arial,sans-serif}}
    main{{max-width:1100px;margin:auto;padding:64px 24px}} h1{{font:52px Georgia,serif;letter-spacing:-.04em;margin:.2em 0}}
    .top{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;border-bottom:2px solid var(--ink);padding-bottom:28px}}
    .badge{{padding:12px 16px;background:{'var(--lime)' if overall else 'var(--coral)'};font-weight:800}}
    .metrics{{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--ink);margin:32px 0}}
    .metrics div{{padding:24px;border-right:1px solid var(--ink)}} .metrics div:last-child{{border:0}}
    .metrics strong{{display:block;font:36px Georgia,serif}} .metrics span{{font-size:10px;text-transform:uppercase}}
    table{{width:100%;border-collapse:collapse;background:#fff}} th,td{{padding:14px;border:1px solid #b7b0a4;text-align:left}}
    th{{background:var(--ink);color:#fff}} .pass{{color:#4f7000;font-weight:800}} .fail{{color:#b42f18;font-weight:800}}
    .note{{margin-top:28px;color:#67736c;line-height:1.6}} code{{background:#e6e0d4;padding:2px 5px}}
    @media(max-width:700px){{.top,.metrics{{grid-template-columns:1fr}}.metrics div{{border-right:0;border-bottom:1px solid var(--ink)}}}}
  </style>
</head>
<body><main>
  <div class="top"><div><small>GENERATED · {date.today().isoformat()}</small><h1>Validation report</h1>
  <p>DMX official Q1 2026 data pack → curated financial facts.</p></div>
  <div class="badge">{'ALL CHECKS PASS' if overall else 'REVIEW REQUIRED'}</div></div>
  <section class="metrics">
    <div><strong>{len(rows)}</strong><span>curated facts</span></div>
    <div><strong>{unique_periods}</strong><span>reporting dates</span></div>
    <div><strong>{len(sources)}</strong><span>registered sources</span></div>
  </section>
  <table><thead><tr><th>Control</th><th>Status</th><th>Observed</th><th>Tolerance</th></tr></thead>
  <tbody>{checks_html}</tbody></table>
  <p class="note">The extractor allowlists only <code>Balance Sheet</code>, <code>Income Statement</code>
  and <code>Cash Flow Statement</code>. Config and notes sheets are not ingested. Raw issuer files remain
  outside Git; the source register retains URL, retrieval timestamp, file size and SHA-256.</p>
</main></body></html>"""
    output_path.write_text(content, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    facts = read_csv(FACTS_PATH)
    sources = read_csv(SOURCES_PATH)
    checks = build_checks(facts, sources)

    pdf_path = DOWNLOADS / "Investment_Memo_EN.pdf"
    validation_path = DOWNLOADS / "validation_report.html"
    build_pdf(pdf_path)
    build_validation_html(validation_path, checks, facts, sources)

    curated_copy = DOWNLOADS / FACTS_PATH.name
    shutil.copy2(FACTS_PATH, curated_copy)

    model_path = ROOT / "model" / "MWG_DMX_IPO_SOTP_Model.xlsx"
    public_model = DOWNLOADS / "MWG_DMX_IPO_SOTP_Model.xlsx"
    if model_path.exists():
        shutil.copy2(model_path, public_model)

    artifacts = [pdf_path, validation_path, curated_copy]
    if public_model.exists():
        artifacts.append(public_model)
    manifest = {
        "generated_on": date.today().isoformat(),
        "data_cutoff": "2026-07-13",
        "checks_passed": all(check.passed for check in checks),
        "artifacts": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in artifacts
        ],
    }
    (DOWNLOADS / "artifacts_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"Built {len(artifacts)} artifacts; checks_passed={manifest['checks_passed']}")


if __name__ == "__main__":
    main()
