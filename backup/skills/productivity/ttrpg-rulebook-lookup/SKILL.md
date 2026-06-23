---
name: ttrpg-rulebook-lookup
title: TTRPG Rulebook Lookup
description: Query tabletop RPG rules from local PDF rulebooks. Use when the user asks for a rule, combat mechanic, skill, item rule, or setting detail from a stored PDF.
---

# TTRPG Rulebook Lookup

Use this skill when the user asks for rules, mechanics, combat steps, skills, items, or setting details from their local TTRPG rulebook PDFs.

## Primary workflow

1. Confirm rulebook folder. Default: `~/rules-pdfs/`
2. If not yet extracted, convert PDFs to text once:
   - `pdftotext "<path>" /tmp/<slug>.txt`
3. Search the extracted text with keyword queries.
4. Read the surrounding lines for context.
5. Answer using the actual rule text. Quote the rule citation or page context when it helps.

## Answer style

- Prefer concise, direct answers.
- State the rule, then give a short example if it clarifies.
- Avoid narration, meta commentary, or filler.
- If the rule is ambiguous, note the ambiguity and the GM call.

## Reference files

- `references/forbidden-lands-attack-rules.md` — distilled attack/combat lookup notes for Forbidden Lands Player's Handbook.
