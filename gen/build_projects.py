#!/usr/bin/env python3
"""Build real project content for the Projects page + case-study galleries.

Source of truth: the owner-supplied descriptions in
    "site images/<project>/*.md"
(the raw markdown carries emoji, "@" typos, and salesy metaphors; this script
carries the same facts, cleaned for the notebook-document voice).

Output:  content/projects.json  (consumed by gen/build_content.py)

Every fact below is taken from the owner's own project descriptions —
capabilities, tech stack, and the few concrete numbers (818 ingredients,
10/10 tests, 30–60 min, etc.). No figures are invented.

Run:  python3 gen/build_projects.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content")


PROJECTS = [
    {
        "slug": "mealprep",
        "title": "MealPrep.exe",
        "kind": "Local-first meal-prep ERP",
        "description": "A local-first web app that replaces spreadsheets, WhatsApp, and notebooks for small-batch meal-prep businesses: menu planning, online ordering, batch counts, shopping lists, and delivery routes in one place.",
        "body": (
            "<p>MealPrep.exe is a local-first meal-prep ERP for small-batch, home-based meal-prep businesses. It replaces the spreadsheets, WhatsApp groups, and notebooks that most chefs juggle with one purpose-built web app.</p>"
            "<p>The problem it solves: a chef has to plan menus each week, let clients order online, track who ordered what, calculate exact batch counts, generate shopping lists, optimise delivery routes, and keep on top of allergen safety. Most chefs run three or more tools to do it. MealPrep.exe replaces all of them.</p>"
            "<h2>For the chef</h2>"
            "<ul>"
            "<li><strong>Recipe builder:</strong> build meals from 818 real USDA ingredients with live cost and margin as you add them, plus auto-inherited allergens.</li>"
            "<li><strong>Weekly menu planner:</strong> pick meals and publish when ready; unpublished meals stay hidden from clients.</li>"
            "<li><strong>Order management:</strong> cards on a status workflow (pending → confirmed → prep → delivered), filterable by status.</li>"
            "<li><strong>Batch counts:</strong> total portions per meal across all confirmed orders for the week.</li>"
            "<li><strong>Shopping list:</strong> aggregated ingredients grouped by category, tickable while shopping, printable.</li>"
            "<li><strong>Delivery route:</strong> an OR-Tools TSP solver turns client addresses into the optimal stop order with total miles and Google Maps links.</li>"
            "<li><strong>Ingredient archive:</strong> 818 real USDA ingredients with full nutrition, plus custom ingredients and USDA lookup.</li>"
            "</ul>"
            "<h2>For the client</h2>"
            "<ul>"
            "<li><strong>Public menu:</strong> browse published meals with prices, calories, and macros. No login needed.</li>"
            "<li><strong>PIN login:</strong> a simple four-digit PIN per client; no passwords or email verification.</li>"
            "<li><strong>Allergen warnings:</strong> a red border and warning icon on any meal containing a client's allergens.</li>"
            "<li><strong>Order placement:</strong> select portions, submit; the order starts as pending until the chef confirms.</li>"
            "<li><strong>Order history:</strong> track past orders with colour-coded status badges.</li>"
            "</ul>"
            "<h2>How an order moves</h2>"
            "<ol>"
            "<li>The chef creates meals, plans the week, and clicks publish.</li>"
            "<li>A client browses the menu, logs in with their PIN, and submits an order.</li>"
            "<li>The chef sees the order as pending and confirms it.</li>"
            "<li>The batch and shopping pages plan production.</li>"
            "<li>The chef cooks, then marks the order delivered.</li>"
            "<li>The client checks their history for live status updates.</li>"
            "</ol>"
            "<h2>Under the hood</h2>"
            "<p>FastAPI and SQLite on the backend, a dependency-free vanilla JS frontend, a mobile-first dark theme built for the kitchen, and OR-Tools routing for deliveries. No cloud required: it runs on a laptop in the kitchen at localhost:8000, and the whole database is a single portable file.</p>"
        ),
        "stats": [
            {"value": "818", "label": "USDA ingredients imported"},
            {"value": "9", "label": "SPA views"},
            {"value": "10/10", "label": "backend tests passing"},
            {"value": "1", "label": "app replaces 3+ tools"},
        ],
    },
    {
        "slug": "ledger-lens",
        "title": "LedgerLens",
        "kind": "AI accounting gateway",
        "description": "An intelligent automation system that turns the chaos of incoming invoices and receipts into structured, audit-ready ledger data — no manual entry required.",
        "body": (
            "<p>LedgerLens is an intelligent automation system that turns the steady chaos of financial documents into structured, audit-ready data. Using large language models and computer-vision logic, it watches your accounts in real time and captures every expense the moment it happens — no manual entry.</p>"
            "<h2>Key capabilities</h2>"
            "<ul>"
            "<li><strong>Zero-touch expense capture</strong> — a 24/7 digital clerk for your invoice and receipt inbox. It detects new emails, works out whether the data is in the body or an attachment, and starts processing immediately.</li>"
            "<li><strong>Multi-channel AI extraction</strong> — whether an invoice arrives as a professional PDF, a photo of a thermal receipt, or text in an email body, it reads the document and extracts date, vendor, amount, currency, and expense category with precision.</li>"
            "<li><strong>Automatic document digitalisation</strong> — formatted emails (like an Uber or Amazon receipt) are converted into clean PDFs, so every transaction is archived as a standardised document.</li>"
            "<li><strong>Intelligent naming and filing</strong> — every document is renamed kebab-case (for example, 2024-05-12-adobe-subscription-14-99.pdf) and uploaded to a secure Google Drive folder for instant searchability.</li>"
            "<li><strong>Live ledger sync</strong> — each extracted row is appended to a Google Sheets master ledger with a direct link to the archived file, giving you a linked paper trail.</li>"
            "</ul>"
        ),
        "stats": [
            {"value": "24/7", "label": "zero-touch capture"},
            {"value": "5", "label": "fields extracted per document"},
            {"value": "0", "label": "manual data entry"},
        ],
    },
    {
        "slug": "connex-one-data-bridge",
        "title": "Connex-One Data Bridge",
        "kind": "Contact-centre reporting automation",
        "description": "A silent automation engine linking Connex-One to Google Sheets so campaign and agent performance is captured, cleaned, and visualised without any manual work.",
        "body": (
            "<p>The Connex-One Data Bridge is a quiet, high-efficiency automation engine that removes the morning reporting grind. It links the Connex-One communications platform to Google Sheets, capturing, cleaning, and visualising performance data without human intervention.</p>"
            "<h2>What it does</h2>"
            "<ul>"
            "<li><strong>Reclaims your morning</strong> — supervisors in most contact centres spend the first 30–60 minutes of the shift downloading attachments and keying in data. The bridge does it in seconds, so decisions start at 9:01, not 10:30.</li>"
            "<li><strong>Absolute data integrity</strong> — rigid mapping logic moves Connex-One reports straight into your dashboards, so every abandon-rate and talk-time figure is consistent every time.</li>"
            "<li><strong>Live missed-opportunity tracking</strong> — the inbound abandoned-calls report is prioritised and updated instantly, turning lost calls into an outbound follow-up list.</li>"
            "<li><strong>Unified operations dashboard</strong> — campaign summaries, phone-number stats, and agent metrics land in one central Google Sheet.</li>"
            "<li><strong>Set-and-forget reliability</strong> — it watches the inbox 24/7, marks reports as read once processed, and scales from 100 to 10,000 calls without more staff.</li>"
            "</ul>"
        ),
        "stats": [
            {"value": "24/7", "label": "inbox monitoring"},
            {"value": "30–60 min", "label": "reclaimed each morning"},
            {"value": "0", "label": "manual keying"},
        ],
    },
    {
        "slug": "docket-leads-ai",
        "title": "DocketLeads AI",
        "kind": "Intelligent document processing",
        "description": "Intelligent document processing that extracts high-value personal-injury leads from handwritten towing dockets — vision plus OCR, WhatsApp intake, straight into the CRM.",
        "body": (
            "<p>DocketLeads AI is an intelligent document-processing system that extracts high-value personal-injury leads from handwritten towing dockets. By combining the visual intelligence of GPT-4o with high-precision OCR, it removes manual data entry and makes sure no case slips through the cracks.</p>"
            "<h2>Key features</h2>"
            "<ul>"
            "<li><strong>Multi-engine OCR verification</strong> — a double-check process runs each image through OpenAI Vision for context and OCR.space for raw-text accuracy, resolving messy handwriting.</li>"
            "<li><strong>WhatsApp-native intake</strong> — built for the field: a tow-truck driver or investigator snaps a photo and sends it via WhatsApp, and the system handles the rest.</li>"
            "<li><strong>Intelligent field mapping</strong> — it structures victim info (owner name, phone, suburb), incident data (vehicle make/model, plate number, location), and precise date and time from each docket.</li>"
            "<li><strong>Automated lead logging</strong> — cleaned, validated data is pushed straight into Google Sheets or the CRM, ready for the intake team to follow up.</li>"
            "</ul>"
            "<h2>Why speed matters here</h2>"
            "<p>In personal-injury work, speed to lead is everything. Handwritten dockets often sit in gloveboxes for days. DocketLeads AI digitises them in seconds, so firms can reach accident victims while the incident is still fresh — and convert more of them.</p>"
        ),
        "stats": [
            {"value": "2", "label": "OCR engines (vision + OCR.space)"},
            {"value": "seconds", "label": "to digitise a docket"},
            {"value": "0", "label": "manual data entry"},
        ],
    },
    {
        "slug": "accident-claims-intelligent-automator",
        "title": "Accident Claims Intelligent Automator",
        "kind": "Claims triage and growth automation",
        "description": "A 24/7 digital triage and growth engine for insurance brokers and claims firms — liability analysis, a tailored first response, and zero-touch CRM sync.",
        "body": (
            "<p>The Accident Claims Intelligent Automator is a 24/7 digital triage and growth engine for insurance brokers and claims-management firms. It turns raw accident data into actionable revenue opportunities by combining liability analysis with immediate, empathetic communication.</p>"
            "<h2>What it does</h2>"
            "<ul>"
            "<li><strong>Wins the race to the claimant</strong> — in claims, the golden hour is the window before a claimant speaks to a competing insurer. The system processes reports in seconds, not hours, securing the first notice of loss.</li>"
            "<li><strong>Expert liability triage</strong> — acting as a virtual claims adjuster, it reads complex accident descriptions and flags who is truly at fault against your legal criteria, filtering out no-win cases so the team only works the profitable files.</li>"
            "<li><strong>Tailored-response logic</strong> — custom emails are written to the situation: reassuring non-fault clients about their no-claims discount and a replacement car, offering empathy to third parties, and reminding at-fault clients of their choice-of-repairer rights.</li>"
            "<li><strong>Zero-touch data management</strong> — every detail, from registration numbers to accident notes, syncs straight into Zoho CRM with no typing or missed fields.</li>"
            "<li><strong>Protects repair volume</strong> — it identifies clients who hold choice-of-repairer in their policy and proactively educates them on their rights, keeping vehicles in your network.</li>"
            "</ul>"
        ),
        "stats": [
            {"value": "24/7", "label": "digital triage"},
            {"value": "3", "label": "tailored response variants"},
            {"value": "0", "label": "manual typing"},
        ],
    },
]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "projects.json"), "w", encoding="utf-8") as fh:
        json.dump(PROJECTS, fh, indent=2, ensure_ascii=False)
    print(f"wrote {len(PROJECTS)} projects to content/projects.json")
    for p in PROJECTS:
        print(f"  {p['slug']:40} stats={len(p['stats'])} title={p['title']}")