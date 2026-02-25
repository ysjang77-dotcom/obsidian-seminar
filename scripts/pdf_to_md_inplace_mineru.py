#!/usr/bin/env python3
"""Batch convert PDFs to Markdown in-place.

- Input: a directory containing one or more .pdf files
- Output: writes <same-name>.md next to each PDF
- Assets: writes extracted images under ./images/<pdf-stem>/

This script is intentionally small and task-focused.

Behavior:
- Tries MinerU first (best structure/OCR, but may require heavy deps like torch).
- If MinerU isn't available or fails, falls back to a lightweight PyMuPDF
    text extraction so you still get <same-name>.md outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _mineru_error_hints_torch_missing(stderr: str) -> bool:
    s = (stderr or "").lower()
    needles = [
        "no module named 'torch'",
        "no module named \"torch\"",
        "modulenotfounderror",
        "import torch",
    ]
    return any(n in s for n in needles)


def _normalize_ws(text: str) -> str:
    return " ".join((text or "").replace("\u00a0", " ").split())


_DISCLAIMER_PATTERNS: list[re.Pattern[str]] = [
    # Some PDFs contain a large background watermark that gets extracted as a
    # standalone "ASTM" line. We only de-duplicate exact-line occurrences.
    re.compile(r"^astm$", re.IGNORECASE),
    # Per-page header lines like "B213 −20" (unicode minus) or "B213-20".
    # Keep the first occurrence only.
    re.compile(r"^b213\s*[-\u2212\u2013\u2014]\s*20$", re.IGNORECASE),
    re.compile(r"\bpursuant to license agreement\b", re.IGNORECASE),
    re.compile(r"\bno further reproductions? authorized\b", re.IGNORECASE),
    re.compile(r"\bdownloaded/printed by\b", re.IGNORECASE),
    re.compile(r"\bcopyright by\s+astm\b", re.IGNORECASE),
    re.compile(r"\ball rights reserved\b", re.IGNORECASE),
    re.compile(r"\bkorea institute of materials science\b", re.IGNORECASE),
    re.compile(r"\(kims\)", re.IGNORECASE),
]


def _is_disclaimer_line(line: str) -> bool:
    s = _normalize_ws(line)
    if not s:
        return False
    return any(p.search(s) for p in _DISCLAIMER_PATTERNS)


def _dedupe_repeated_disclaimers(md_text: str) -> str:
    """Remove repeated disclaimer/watermark lines, keep first occurrence.

    Many ASTM PDFs include per-page footers such as KIMS/license/copyright lines.
    This keeps the first seen unique line and removes repeats.
    """

    lines = (md_text or "").splitlines()
    seen: set[str] = set()
    out: list[str] = []

    for line in lines:
        if _is_disclaimer_line(line):
            key = _normalize_ws(line).lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(_normalize_ws(line))
        else:
            out.append(line)

    # Remove standalone per-page numbers (e.g., "1", "2", "3") that appear
    # near page boundaries.
    page_header_re = re.compile(r"^##\s+Page\s+\d+\s*$", re.IGNORECASE)
    page_num_re = re.compile(r"^\s*\d{1,4}\s*$")
    page_idxs = [i for i, l in enumerate(out) if page_header_re.match(_normalize_ws(l))]
    if page_idxs:
        remove_idx: set[int] = set()

        # Also clean the preamble section before the first explicit page header.
        first_page = page_idxs[0]
        pre_nonempty = [j for j in range(0, first_page) if _normalize_ws(out[j]) != ""]
        for j in pre_nonempty[-3:]:
            if page_num_re.match(out[j]) and "|" not in out[j]:
                remove_idx.add(j)

        for pi, start in enumerate(page_idxs):
            end = page_idxs[pi + 1] if pi + 1 < len(page_idxs) else len(out)
            # Non-empty line indices within this page section (excluding header).
            nonempty = [j for j in range(start + 1, end) if _normalize_ws(out[j]) != ""]
            if not nonempty:
                continue
            boundary = set(nonempty[:2] + nonempty[-2:])
            for j in boundary:
                if page_num_re.match(out[j]) and "|" not in out[j]:
                    remove_idx.add(j)
        if remove_idx:
            out = [l for i, l in enumerate(out) if i not in remove_idx]

    # Clean up excessive blank lines introduced by removals
    cleaned: list[str] = []
    blank_run = 0
    for line in out:
        if _normalize_ws(line) == "":
            blank_run += 1
            if blank_run <= 2:
                cleaned.append("")
        else:
            blank_run = 0
            cleaned.append(line)

    return "\n".join(cleaned).strip() + "\n"


def _bbox_intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    if ax1 <= bx0 or bx1 <= ax0:
        return False
    if ay1 <= by0 or by1 <= ay0:
        return False
    return True


def _md_escape_cell(value: str) -> str:
    v = (value or "").replace("\n", " ").strip()
    v = _normalize_ws(v)
    return v.replace("|", "\\|")


def _table_to_markdown(table_rows: list[list[str | None]]) -> str | None:
    if not table_rows:
        return None
    # Normalize row lengths
    col_count = max((len(r) for r in table_rows if r), default=0)
    if col_count <= 1:
        return None

    normalized: list[list[str]] = []
    for r in table_rows:
        r = list(r or [])
        r = ["" if c is None else str(c) for c in r]
        if len(r) < col_count:
            r = r + [""] * (col_count - len(r))
        elif len(r) > col_count:
            r = r[:col_count]
        normalized.append([_md_escape_cell(c) for c in r])

    # Heuristic: merge multi-row headers into a single header row when the
    # table has 3+ header rows before numeric-heavy body rows.
    numeric_like_re = re.compile(r"^\d+(?:\.\d+)?[A-Za-z]?$", re.IGNORECASE)

    def numeric_like_cells(row: list[str]) -> int:
        return sum(1 for cell in row if numeric_like_re.match(_normalize_ws(cell)))

    body_start = None
    for i, r in enumerate(normalized):
        if numeric_like_cells(r) >= 2:
            body_start = i
            break

    if body_start is not None and body_start >= 3:
        header_rows = normalized[:body_start]
        body = normalized[body_start:]
        header: list[str] = []
        for ci in range(col_count):
            parts: list[str] = []
            seen_parts: set[str] = set()
            for hr in header_rows:
                frag = _normalize_ws(hr[ci])
                if not frag:
                    continue
                key = frag.lower()
                if key in seen_parts:
                    continue
                seen_parts.add(key)
                parts.append(frag)
            header.append(_md_escape_cell(" ".join(parts)))
    else:
        header = normalized[0]
        body = normalized[1:] if len(normalized) > 1 else []
    # Markdown alignment: center every column.
    # (CommonMark/GFM accept :---: in the separator row.)
    sep = [":---:"] * col_count

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for r in body:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def _detect_tables_from_words(
    ppage: Any,
    *,
    y_tolerance: float = 3.0,
    x_bin: float = 12.0,
    min_lines: int = 4,
    min_cols: int = 3,
    max_cols: int = 8,
    min_anchor_presence: float = 0.6,
) -> list[tuple[tuple[float, float, float, float], str]]:
    """Best-effort table detection for whitespace-aligned tables.

    Returns list of (bbox(x0, top, x1, bottom), markdown_table).
    """

    def bin_x(x: float) -> float:
        return round(x / x_bin) * x_bin

    words = ppage.extract_words() or []
    if not words:
        return []

    # Group words into lines by 'top'.
    words_sorted = sorted(words, key=lambda w: (float(w.get("top", 0.0)), float(w.get("x0", 0.0))))
    lines: list[dict[str, Any]] = []
    for w in words_sorted:
        top = float(w.get("top", 0.0))
        if not lines or abs(top - float(lines[-1]["top"])) > y_tolerance:
            lines.append({"top": top, "words": [w]})
        else:
            lines[-1]["words"].append(w)

    # Precompute per-line binned x positions.
    for line in lines:
        bins = {bin_x(float(w.get("x0", 0.0))) for w in line["words"]}
        line["xbins"] = sorted(bins)

    def line_is_candidate(line: dict[str, Any]) -> bool:
        c = len(line.get("xbins") or [])
        return min_cols <= c <= max_cols

    # Find contiguous candidate segments.
    segments: list[tuple[int, int]] = []
    start = None
    for i, line in enumerate(lines):
        if line_is_candidate(line):
            if start is None:
                start = i
        else:
            if start is not None:
                if i - start >= min_lines:
                    segments.append((start, i))
                start = None
    if start is not None and len(lines) - start >= min_lines:
        segments.append((start, len(lines)))

    results: list[tuple[tuple[float, float, float, float], str]] = []
    for s, e in segments:
        seg_lines = lines[s:e]
        # Build anchor histogram.
        counts: dict[float, int] = {}
        for ln in seg_lines:
            for xb in ln["xbins"]:
                counts[xb] = counts.get(xb, 0) + 1
        # Keep anchors that appear in enough lines.
        required = max(1, int(len(seg_lines) * min_anchor_presence))
        anchors = sorted([x for x, c in counts.items() if c >= required])
        if not (min_cols <= len(anchors) <= max_cols):
            continue

        # Convert anchors to column boundaries.
        bounds: list[float] = []
        for i in range(len(anchors) - 1):
            bounds.append((anchors[i] + anchors[i + 1]) / 2)

        def col_index(x0: float) -> int:
            for i, b in enumerate(bounds):
                if x0 < b:
                    return i
            return len(anchors) - 1

        rows: list[list[str]] = []
        used_word_count = 0
        for ln in seg_lines:
            row = [""] * len(anchors)
            for w in sorted(ln["words"], key=lambda ww: float(ww.get("x0", 0.0))):
                x0 = float(w.get("x0", 0.0))
                text = (w.get("text") or "").strip()
                if not text:
                    continue
                used_word_count += 1
                ci = col_index(x0)
                row[ci] = (row[ci] + " " + text).strip() if row[ci] else text
            rows.append(row)

        # Heuristic: if this segment mostly looks like flowing text (few words
        # distributed across multiple columns), skip.
        multi_col_lines = 0
        for r in rows:
            filled = sum(1 for c in r if _normalize_ws(c))
            if filled >= 2:
                multi_col_lines += 1
        if multi_col_lines < max(min_lines, int(len(rows) * 0.5)):
            continue

        # Additional heuristics to avoid turning paragraph-like layout into tables.
        nonempty_lens: list[int] = []
        empty_cells = 0
        total_cells = len(rows) * len(anchors)
        for r in rows:
            for c in r:
                cc = _normalize_ws(c)
                if not cc:
                    empty_cells += 1
                else:
                    nonempty_lens.append(len(cc))

        empty_frac = (empty_cells / total_cells) if total_cells else 0.0
        if len(anchors) == 2 and empty_frac < 0.1:
            # Often indicates 2-column running text / footnotes rather than a table.
            if nonempty_lens:
                nonempty_lens.sort()
                median_len = nonempty_lens[len(nonempty_lens) // 2]
                if median_len >= 40 or len(rows) >= 20:
                    continue

        # Build bbox.
        x0 = min(float(w.get("x0", 0.0)) for ln in seg_lines for w in ln["words"])
        x1 = max(float(w.get("x1", 0.0)) for ln in seg_lines for w in ln["words"])
        top = min(float(w.get("top", 0.0)) for ln in seg_lines for w in ln["words"])
        bottom = max(float(w.get("bottom", 0.0)) for ln in seg_lines for w in ln["words"])

        md = _table_to_markdown(rows)
        if not md:
            continue
        results.append(((x0, top, x1, bottom), md))

    return results


def _group_words_into_lines(words: list[dict[str, Any]], y_tolerance: float) -> list[dict[str, Any]]:
    words_sorted = sorted(words, key=lambda w: (float(w.get("top", 0.0)), float(w.get("x0", 0.0))))
    lines: list[dict[str, Any]] = []
    for w in words_sorted:
        top = float(w.get("top", 0.0))
        if not lines or abs(top - float(lines[-1]["top"])) > y_tolerance:
            lines.append({"top": top, "words": [w]})
        else:
            lines[-1]["words"].append(w)
    return lines


def _table_from_word_region(
    words: list[dict[str, Any]],
    *,
    y_tolerance: float = 3.0,
    x_bin: float = 10.0,
    min_cols: int = 2,
    max_cols: int = 10,
    min_lines: int = 3,
    min_anchor_presence: float = 0.5,
) -> tuple[tuple[float, float, float, float], str] | None:
    if not words:
        return None

    # Many ASTM tables include numeric values with footnote suffixes like
    # 34.2A or 33.8B.
    numeric_like_re = re.compile(r"^\d+(?:\.\d+)?[A-Za-z]?$", re.IGNORECASE)

    def bin_x(x: float) -> float:
        return round(x / x_bin) * x_bin

    def annotate_pure_nums(ls: list[dict[str, Any]]) -> None:
        for ln in ls:
            pure_nums = 0
            for w in ln["words"]:
                t = (w.get("text") or "").strip()
                if numeric_like_re.match(t):
                    pure_nums += 1
            ln["pure_nums"] = pure_nums

    lines = _group_words_into_lines(words, y_tolerance)
    if len(lines) < min_lines:
        return None
    annotate_pure_nums(lines)

    # Attempt to focus on the actual table body area by using numeric-heavy lines.
    # This reduces contamination from adjacent narrative text in multi-column layouts.
    candidate_line_words: list[dict[str, Any]] = []
    for ln in lines:
        if int(ln.get("pure_nums", 0)) >= 2:
            candidate_line_words.extend(ln["words"])

    focused_words = words
    if len(candidate_line_words) >= 10:
        x0_min = min(float(w.get("x0", 0.0)) for w in candidate_line_words)
        x1_max = max(float(w.get("x1", 0.0)) for w in candidate_line_words)
        margin = 40.0
        focused_words = [
            w
            for w in words
            if (float(w.get("x0", 0.0)) >= (x0_min - margin)) and (float(w.get("x1", 0.0)) <= (x1_max + margin))
        ]
        if not focused_words:
            focused_words = words

    # Rebuild lines after focusing.
    lines = _group_words_into_lines(focused_words, y_tolerance)
    if len(lines) < min_lines:
        return None
    annotate_pure_nums(lines)

    # Build column anchors from tabular-looking lines first, fallback to all lines.
    anchor_lines = [ln for ln in lines if int(ln.get("pure_nums", 0)) >= 2]
    if len(anchor_lines) < min_lines:
        anchor_lines = lines

    counts: dict[float, int] = {}
    for ln in anchor_lines:
        xbins = {bin_x(float(w.get("x0", 0.0))) for w in ln["words"]}
        for xb in xbins:
            counts[xb] = counts.get(xb, 0) + 1

    required = max(2, int(len(anchor_lines) * min_anchor_presence))
    anchors = sorted([x for x, c in counts.items() if c >= required])

    # Collapse nearby anchors (often multiple bins per true column).
    if anchors:
        clustered: list[list[float]] = [[anchors[0]]]
        for a in anchors[1:]:
            if abs(a - clustered[-1][-1]) <= (x_bin * 1.6):
                clustered[-1].append(a)
            else:
                clustered.append([a])
        anchors = [sorted(g)[len(g) // 2] for g in clustered]

    # If multiple leftmost anchors are just the continuation of a multi-word
    # first column (e.g., material names), merge them into a single column.
    numeric_words = [w for w in focused_words if numeric_like_re.match((w.get("text") or "").strip())]
    if numeric_words and len(anchors) >= 3:
        min_num_x0 = min(float(w.get("x0", 0.0)) for w in numeric_words)
        threshold = min_num_x0 - (x_bin * 2.0)
        left = [a for a in anchors if a < threshold]
        if len(left) > 1:
            anchors = [min(left)] + [a for a in anchors if a >= threshold]

    if not (min_cols <= len(anchors) <= max_cols):
        return None

    bounds: list[float] = []
    for i in range(len(anchors) - 1):
        bounds.append((anchors[i] + anchors[i + 1]) / 2)

    def col_index(x0: float) -> int:
        for i, b in enumerate(bounds):
            if x0 < b:
                return i
        return len(anchors) - 1

    # Determine the first clearly tabular body line (2+ numeric-like tokens).
    body_top: float | None = None
    for ln in lines:
        if int(ln.get("pure_nums", 0)) >= 2:
            body_top = float(ln.get("top", 0.0))
            break

    rows: list[list[str]] = []
    for ln in lines:
        row = [""] * len(anchors)
        for w in sorted(ln["words"], key=lambda ww: float(ww.get("x0", 0.0))):
            text = (w.get("text") or "").strip()
            if not text:
                continue
            x0 = float(w.get("x0", 0.0))
            ci = col_index(x0)
            row[ci] = (row[ci] + " " + text).strip() if row[ci] else text

        filled = sum(1 for c in row if _normalize_ws(c))

        # Preserve header/unit lines (often fill a single column) only before
        # the numeric-heavy body starts.
        if filled < 2:
            is_header_region = body_top is not None and float(ln.get("top", 0.0)) < body_top
            if not (is_header_region and filled >= 1):
                continue
        rows.append(row)

    # Merge continuation lines: if a row only fills col0, append to previous row col0.
    merged: list[list[str]] = []
    for r in rows:
        filled_cols = [i for i, c in enumerate(r) if _normalize_ws(c)]
        if len(filled_cols) == 1 and filled_cols[0] == 0 and merged:
            merged[-1][0] = (merged[-1][0] + " " + _normalize_ws(r[0])).strip()
            continue
        merged.append(r)
    rows = merged

    md = _table_to_markdown(rows)
    if not md:
        return None

    # ASTM B213-style tables sometimes place the Flow Rate unit on a separate
    # line like "(s/50 g)". If the unit token exists in the table region but
    # does not survive header reconstruction, patch it into the Flow Rate
    # header cell.
    try:
        focused_text = " ".join((w.get("text") or "") for w in focused_words)
        if ("s/50" in focused_text.lower()) and ("s/50" not in md.lower()):
            md_lines = md.splitlines()
            if md_lines and md_lines[0].lstrip().startswith("|"):
                raw = md_lines[0].strip().strip("|")
                cells = [c.strip() for c in raw.split("|")]
                for i, c in enumerate(cells):
                    if "flow rate" in c.lower() and "s/50" not in c.lower():
                        cells[i] = _md_escape_cell(_normalize_ws(c) + " (s/50 g)")
                        md_lines[0] = "| " + " | ".join(cells) + " |"
                        md = "\n".join(md_lines)
                        break
    except Exception:
        pass

    x0 = min(float(w.get("x0", 0.0)) for w in focused_words)
    x1 = max(float(w.get("x1", 0.0)) for w in focused_words)
    top = min(float(w.get("top", 0.0)) for w in focused_words)
    bottom = max(float(w.get("bottom", 0.0)) for w in focused_words)
    return (x0, top, x1, bottom), md


def _fitz_words_to_dicts(words: list[tuple[float, float, float, float, str, int, int, int]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for w in words:
        x0, y0, x1, y1, text = float(w[0]), float(w[1]), float(w[2]), float(w[3]), str(w[4])
        out.append({"x0": x0, "x1": x1, "top": y0, "bottom": y1, "text": text})
    return out


def _detect_tables_near_headings_fitz(page: Any) -> list[tuple[tuple[float, float, float, float], float, str]]:
    """Return [(bbox, insert_y, md_table), ...] using PyMuPDF page coordinates."""

    # PyMuPDF words: x0, y0, x1, y1, word, block_no, line_no, word_no
    words_raw = page.get_text("words") or []
    if not words_raw:
        return []

    # Group into lines by (block_no, line_no)
    by_line: dict[tuple[int, int], list[tuple]] = {}
    for w in words_raw:
        block_no = int(w[5])
        line_no = int(w[6])
        by_line.setdefault((block_no, line_no), []).append(w)

    lines: list[dict[str, Any]] = []
    for (bn, ln), ws in by_line.items():
        ws = sorted(ws, key=lambda t: float(t[0]))
        text = " ".join(_normalize_ws(str(t[4])) for t in ws if str(t[4]).strip())
        if not text:
            continue
        y0 = min(float(t[1]) for t in ws)
        y1 = max(float(t[3]) for t in ws)
        x0 = min(float(t[0]) for t in ws)
        x1 = max(float(t[2]) for t in ws)
        lines.append({"bn": bn, "ln": ln, "y0": y0, "y1": y1, "x0": x0, "x1": x1, "text": text})

    headings = [
        l
        for l in lines
        if re.match(r"^TABLE\s+\d+\b(?!\.)", l["text"], flags=re.IGNORECASE)
        and (l["text"].split()[0] == "TABLE")
    ]
    if not headings:
        return []

    headings = sorted(headings, key=lambda d: d["y0"])
    results: list[tuple[tuple[float, float, float, float], float, str]] = []

    words_dicts = _fitz_words_to_dicts(words_raw)
    page_mid_x = float(page.rect.width) / 2.0
    for i, h in enumerate(headings):
        start_y = float(h["y1"]) + 1.0
        end_y = float(headings[i + 1]["y0"]) - 1.0 if i + 1 < len(headings) else float("inf")
        # In multi-column documents, the content below a heading may continue
        # in the same column while the other column advances with different
        # sections. Restrict to the heading's column first to avoid mixing.
        column_margin = 8.0
        heading_is_right = float(h.get("x0", 0.0)) > page_mid_x
        if heading_is_right:
            region = [
                w
                for w in words_dicts
                if float(w["top"]) >= start_y
                and float(w["top"]) < end_y
                and float(w.get("x0", 0.0)) >= page_mid_x - column_margin
            ]
        else:
            region = [
                w
                for w in words_dicts
                if float(w["top"]) >= start_y
                and float(w["top"]) < end_y
                and float(w.get("x1", 0.0)) <= page_mid_x + column_margin
            ]
        if not region:
            continue

        # Shrink region to the likely end of the table body by using the last
        # pure-number token position. This avoids including normal two-column
        # body text below the table.
        numeric_like_re = re.compile(r"^\d+(?:\.\d+)?[A-Za-z]?$")
        # Limit region to the likely end of the table body by finding the last
        # line that still looks tabular (2+ numeric-like tokens). This avoids
        # pulling in page numbers or footer digits.
        try:
            region_lines = _group_words_into_lines(region, y_tolerance=4.0)
            tabular_lines = []
            min_num_spread = 120.0
            for ln in region_lines:
                nnums = 0
                num_xs: list[float] = []
                for w in ln["words"]:
                    t = (w.get("text") or "").strip()
                    if numeric_like_re.match(t):
                        nnums += 1
                        num_xs.append(float(w.get("x0", 0.0)))
                ln["nnums"] = nnums
                # Table body rows typically have multiple numeric cells spread
                # across the row. This avoids misclassifying phone numbers.
                if nnums >= 3 and num_xs and (max(num_xs) - min(num_xs)) >= min_num_spread:
                    tabular_lines.append(ln)
            if len(tabular_lines) >= 3:
                last = max(tabular_lines, key=lambda d: float(d.get("top", 0.0)))
                last_bottom = max(float(w.get("bottom", w.get("top", 0.0))) for w in last["words"])
                cutoff = last_bottom + 4.0
                region = [w for w in region if float(w["top"]) <= cutoff]
                if not region:
                    continue
        except Exception:
            pass
        tbl = _table_from_word_region(
            region,
            min_cols=2,
            max_cols=10,
            x_bin=8.0,
            y_tolerance=4.0,
            min_anchor_presence=0.2,
        )
        if tbl is None:
            continue
        bbox, md = tbl

        # Attach table footnotes (A/B/...) that appear immediately below the
        # table, and expand the suppressed bbox to avoid duplicated text.
        notes: list[str] = []
        notes_bottom = float(bbox[3])
        try:
            scan_end_y = min(float(end_y), float(bbox[3]) + 220.0)
            foot_candidates: list[dict[str, Any]] = []
            for l in lines:
                y0 = float(l.get("y0", 0.0))
                if y0 < (float(bbox[3]) + 0.5) or y0 >= scan_end_y:
                    continue
                if heading_is_right:
                    if float(l.get("x0", 0.0)) < (page_mid_x - column_margin):
                        continue
                else:
                    if float(l.get("x1", 0.0)) > (page_mid_x + column_margin):
                        continue
                foot_candidates.append(l)
            foot_candidates.sort(key=lambda d: float(d.get("y0", 0.0)))

            note_re = re.compile(r"^[A-Z]\s+", re.IGNORECASE)
            section_re = re.compile(r"^\d+(?:\.\d+)+\b")

            current: str | None = None
            last_y1: float | None = None
            for l in foot_candidates:
                t = _normalize_ws(str(l.get("text") or ""))
                if not t:
                    if current:
                        break
                    continue
                if section_re.match(t):
                    break
                if note_re.match(t) and len(t.split()[0]) == 1:
                    if current:
                        notes.append(current.strip())
                    current = t
                elif current is not None:
                    if last_y1 is not None and (float(l.get("y0", 0.0)) - last_y1) > 12.0:
                        break
                    current = (current + " " + t).strip()
                else:
                    break
                last_y1 = float(l.get("y1", l.get("y0", 0.0)))
                notes_bottom = max(notes_bottom, float(l.get("y1", l.get("y0", 0.0))))
            if current:
                notes.append(current.strip())
        except Exception:
            notes = []

        if notes:
            md = md + "\n\n" + "\n".join(notes)
            x0, top, x1, _bottom = bbox
            bbox = (x0, top, x1, notes_bottom)
        insert_y = start_y + 0.01
        results.append((bbox, insert_y, md))

    return results


def _detect_tables_near_headings(
    ppage: Any,
    *,
    y_tolerance: float = 3.0,
) -> list[tuple[tuple[float, float, float, float], str]]:
    """Detect tables by anchoring on explicit 'TABLE n' headings.

    ASTM docs frequently label tables as 'TABLE 1', 'TABLE 2', etc.
    This approach is more accurate than trying to infer tables page-wide.
    """

    words = ppage.extract_words() or []
    if not words:
        return []

    # Build line groups; find lines that start with 'TABLE' and a number.
    lines = _group_words_into_lines(words, y_tolerance)

    heading_lines: list[dict[str, Any]] = []
    for ln in lines:
        texts = [str(w.get("text") or "") for w in ln["words"]]
        joined = " ".join(_normalize_ws(t) for t in texts if t).strip()
        if not joined:
            continue
        if re.match(r"^TABLE\s+\d+\b(?!\.)", joined, flags=re.IGNORECASE) and joined.split()[0] == "TABLE":
            ln["joined"] = joined
            heading_lines.append(ln)

    if not heading_lines:
        return []

    # For each heading, take words below it until the next heading (or page bottom).
    results: list[tuple[tuple[float, float, float, float], str]] = []
    heading_tops = sorted((float(h["top"]) for h in heading_lines))
    for i, h in enumerate(sorted(heading_lines, key=lambda d: float(d["top"]))):
        h_top = float(h["top"])
        # Define start a bit below heading line.
        h_bottom = max(float(w.get("bottom", h_top)) for w in h["words"]) + 2.0
        next_top = heading_tops[i + 1] if i + 1 < len(heading_tops) else float("inf")

        region_words = [
            w
            for w in words
            if float(w.get("top", 0.0)) >= h_bottom and float(w.get("top", 0.0)) < next_top - 2.0
        ]
        # Heuristic: limit to a reasonable chunk to avoid swallowing the whole page.
        if not region_words:
            continue

        # Try to build a table from this region. Prefer 2+ cols here.
        tbl = _table_from_word_region(region_words, min_cols=2, y_tolerance=y_tolerance)
        if tbl is None:
            continue
        bbox, md = tbl
        results.append((bbox, md))

    return results


def _convert_with_pymupdf_layout(pdf_path: Path, out_md: Path, images_root: Path) -> None:
    try:
        import fitz  # PyMuPDF
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "PyMuPDF is required for fallback conversion. Install with: pip install pymupdf"
        ) from exc

    pdf_stem = pdf_path.stem
    images_dir = images_root / pdf_stem / "extracted"
    if images_dir.exists():
        shutil.rmtree(images_dir)
    images_dir.mkdir(parents=True, exist_ok=True)
    rel_images_prefix = f"images/{pdf_stem}/extracted"

    def save_extracted_image(doc: "fitz.Document", xref: int) -> tuple[str, str]:
        extracted = doc.extract_image(xref)
        ext = (extracted.get("ext") or "png").lower()
        if ext == "jpeg":
            ext = "jpg"
        img_name = f"xref-{xref}.{ext}"
        img_path = images_dir / img_name
        img_bytes = extracted["image"]
        if not img_path.exists():
            img_path.write_bytes(img_bytes)
        digest = hashlib.sha1(img_bytes).hexdigest()
        return f"{rel_images_prefix}/{img_name}", digest

    parts: list[str] = [f"# {pdf_stem}", ""]

    # Filter out per-page header identifiers like "B213 −20" when they match
    # the PDF stem (the stem is already used as the document title).
    stem_id_re: re.Pattern[str] | None = None
    if "-" in pdf_stem:
        left, right = pdf_stem.split("-", 1)
        left = re.escape(left.strip())
        right = re.escape(right.strip())
        dash = r"[-\u2212\u2013\u2014]"
        stem_id_re = re.compile(rf"^{left}\s*{dash}\s*{right}$", re.IGNORECASE)

    # Optional table extraction (best-effort). If pdfplumber isn't installed or
    # fails to detect tables, we still emit text+images.
    try:
        import pdfplumber  # type: ignore
    except Exception:
        pdfplumber = None  # type: ignore

    plumber_pdf = None
    if pdfplumber is not None:
        try:
            plumber_pdf = pdfplumber.open(str(pdf_path))
        except Exception:
            plumber_pdf = None

    with fitz.open(pdf_path) as doc:
        seen_center_watermark_hashes: set[str] = set()
        deferred_watermark_md: str | None = None
        for page_index in range(doc.page_count):
            page_no = page_index + 1
            page = doc.load_page(page_index)

            table_bboxes: list[tuple[float, float, float, float]] = []
            table_elements: list[tuple[float, float, str]] = []

            # Prefer fitz-based TABLE heading detection to keep coordinate systems consistent.
            try:
                detected_fitz = _detect_tables_near_headings_fitz(page)
                for bbox, insert_y, md in detected_fitz:
                    x0, top, x1, bottom = bbox
                    table_bboxes.append((x0, top, x1, bottom))
                    table_elements.append((insert_y, x0, md))
            except Exception:
                detected_fitz = []

            # Fallback to word-based detector (pdfplumber) only if no heading-based tables found.
            if not table_elements and plumber_pdf is not None and page_index < len(plumber_pdf.pages):
                try:
                    ppage = plumber_pdf.pages[page_index]
                    detected = _detect_tables_from_words(ppage)
                    for bbox, md in detected:
                        x0, top, x1, bottom = bbox
                        table_bboxes.append((x0, top, x1, bottom))
                        table_elements.append((top, x0, md))
                except Exception:
                    table_bboxes = []
                    table_elements = []

            # Collect text blocks.
            elements: list[tuple[float, float, str]] = []
            for b in page.get_text("blocks"):
                # (x0, y0, x1, y1, "text", block_no, block_type)
                if len(b) < 7:
                    continue
                x0, y0, _x1, _y1, text, _bn, btype = b
                if int(btype) != 0:
                    continue
                if table_bboxes:
                    block_bbox = (float(x0), float(y0), float(_x1), float(_y1))
                    # Suppress text that lies inside detected table areas.
                    if any(_bbox_intersects(block_bbox, tb) for tb in table_bboxes):
                        continue
                text = (text or "").strip()
                if text:
                    normalized = _normalize_ws(text)
                    if normalized.lower() == "astm":
                        continue
                    if stem_id_re is not None and stem_id_re.match(normalized):
                        continue
                    elements.append((float(y0), float(x0), text))

            # Collect embedded images with their placement rectangles.
            page_w = float(page.rect.width)
            page_h = float(page.rect.height)
            page_area = max(1.0, page_w * page_h)
            page_cx = page_w / 2.0
            page_cy = page_h / 2.0
            for img in page.get_images(full=True):
                xref = img[0]
                try:
                    rects = page.get_image_rects(xref)
                except Exception:
                    rects = []
                if not rects:
                    continue
                try:
                    rel_path, digest = save_extracted_image(doc, xref)
                except Exception:
                    continue
                for r in rects:
                    # Suppress repeated watermark-like images (large + centered)
                    # while keeping the first occurrence.
                    try:
                        rect_area = float(r.width) * float(r.height)
                        area_ratio = rect_area / page_area
                        rcx = (float(r.x0) + float(r.x1)) / 2.0
                        rcy = (float(r.y0) + float(r.y1)) / 2.0
                        centered = (abs(rcx - page_cx) <= (page_w * 0.22)) and (abs(rcy - page_cy) <= (page_h * 0.22))
                        centered_large = centered and (area_ratio >= 0.06)

                        # Also handle repeated header logos: small images near the
                        # top margin that repeat on every page (e.g., ASTM logo).
                        header_small = (
                            float(r.y0) <= (page_h * 0.12)
                            and float(r.height) <= (page_h * 0.20)
                            and float(r.width) <= (page_w * 0.60)
                        )

                        watermark_candidate = centered_large or header_small
                    except Exception:
                        watermark_candidate = False

                    if watermark_candidate:
                        if digest in seen_center_watermark_hashes:
                            continue
                        seen_center_watermark_hashes.add(digest)
                        if deferred_watermark_md is None:
                            deferred_watermark_md = f"![]({rel_path})"
                        continue
                    elements.append((float(r.y0), float(r.x0), f"![]({rel_path})"))

            # Insert tables as elements too.
            if table_elements:
                elements.extend(table_elements)

            elements.sort(key=lambda t: (t[0], t[1]))

            # Keep page boundaries to reduce accidental re-ordering.
            parts.append(f"## Page {page_no}")
            parts.append("")
            for _, __, content in elements:
                parts.append(content)
                parts.append("")

        # Put a single watermark/logo (if any) at the top of the document
        # instead of repeating it on many pages.
        if deferred_watermark_md:
            parts.insert(2, deferred_watermark_md)
            parts.insert(3, "")

    if plumber_pdf is not None:
        try:
            plumber_pdf.close()
        except Exception:
            pass

    md_text = "\n".join(parts).strip() + "\n"
    md_text = _dedupe_repeated_disclaimers(md_text)
    out_md.write_text(md_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert all PDFs in a directory to Markdown (in-place). "
            "Uses MinerU when possible, otherwise falls back to PyMuPDF."
        )
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        type=Path,
        required=True,
        help="Directory containing PDF files",
    )
    parser.add_argument(
        "--backend",
        "-b",
        type=str,
        default="hybrid-auto-engine",
        choices=["pipeline", "vlm", "hybrid-auto-engine"],
        help="MinerU backend (default: hybrid-auto-engine)",
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        default="en",
        help="OCR language (default: en)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .md outputs if they already exist",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        help=(
            "Convert only selected PDFs (match by filename or stem). "
            "Can be provided multiple times, e.g. --only B213-20"
        ),
    )
    return parser.parse_args()


def _find_mineru_cli() -> Path | None:
    """Locate the MinerU CLI executable.

    Prefer the CLI that ships with the current Python environment (venv).
    """
    scripts_dir = Path(sys.executable).parent
    exe_name = "mineru.exe" if os.name == "nt" else "mineru"
    candidate = scripts_dir / exe_name
    if candidate.exists():
        return candidate

    which = shutil.which("mineru")
    if which:
        return Path(which)

    return None


def _rewrite_image_paths(md_text: str, pdf_stem: str) -> str:
    # MinerU outputs MD that references images under a sibling ./images directory.
    # When we move the MD next to the original PDF, we also relocate images to
    # ./images/<pdf_stem>/, so update links accordingly.
    replacements = {
        "(images/": f"(images/{pdf_stem}/",
        "(./images/": f"(images/{pdf_stem}/",
        "src=\"images/": f"src=\"images/{pdf_stem}/",
        "src='images/": f"src='images/{pdf_stem}/",
        "src=\"./images/": f"src=\"images/{pdf_stem}/",
        "src='./images/": f"src='images/{pdf_stem}/",
    }
    out = md_text
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out


def _copy_tree(src_dir: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src_path in src_dir.rglob("*"):
        rel = src_path.relative_to(src_dir)
        dst_path = dst_dir / rel
        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)


def main() -> int:
    args = parse_args()

    if not args.input_dir.exists():
        print(f"Error: input dir not found: {args.input_dir}")
        return 1

    pdf_files = sorted(args.input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Error: no PDFs found in: {args.input_dir}")
        return 1

    if args.only:
        wanted: set[str] = set()
        for item in args.only:
            item = (item or "").strip()
            if not item:
                continue
            p = Path(item)
            if p.suffix.lower() == ".pdf":
                wanted.add(p.name.lower())
                wanted.add(p.stem.lower())
            else:
                wanted.add(item.lower())
        pdf_files = [p for p in pdf_files if p.name.lower() in wanted or p.stem.lower() in wanted]
        if not pdf_files:
            print("Error: no PDFs matched --only filters")
            return 1

    mineru_cli = _find_mineru_cli()
    if not mineru_cli:
        print("Warning: MinerU CLI not found; will use PyMuPDF fallback for all PDFs.")

    images_root = args.input_dir / "images"
    images_root.mkdir(parents=True, exist_ok=True)

    success = 0
    skipped = 0
    failed = 0

    print(f"Found {len(pdf_files)} PDFs")
    print(f"Backend: {args.backend}")
    print(f"Language: {args.language}")
    print(f"Output: in-place next to each PDF")
    if mineru_cli:
        print(f"MinerU CLI: {mineru_cli}")
    else:
        print("MinerU CLI: (not found; using PyMuPDF)")
    print("-" * 60)

    with tempfile.TemporaryDirectory(prefix="mineru_convert_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        for idx, pdf_path in enumerate(pdf_files, 1):
            out_md = pdf_path.with_suffix(".md")
            pdf_stem = pdf_path.stem

            if out_md.exists() and not args.overwrite:
                skipped += 1
                print(f"[{idx}/{len(pdf_files)}] Skip (exists): {out_md.name}")
                continue

            try:
                print(f"[{idx}/{len(pdf_files)}] Converting: {pdf_path.name}")
                converted = False

                if mineru_cli:
                    cmd = [
                        str(mineru_cli),
                        "-p",
                        str(pdf_path),
                        "-o",
                        str(tmp_dir),
                        "-m",
                        "auto",
                        "-b",
                        args.backend,
                        "-l",
                        args.language,
                    ]
                    env = os.environ.copy()
                    # MinerU 2.7.x may crash/bug when torch isn't installed and it tries
                    # to auto-detect GPU. Forcing device mode avoids that code path.
                    env.setdefault("MINERU_DEVICE_MODE", "cpu")
                    env.setdefault("MINERU_VIRTUAL_VRAM_SIZE", "0")

                    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
                    if completed.returncode == 0:
                        md_candidates = list(tmp_dir.glob(f"{pdf_stem}/**/{pdf_stem}.md"))
                        if md_candidates:
                            md_src = md_candidates[0]
                            images_src = md_src.parent / "images"

                            md_text = md_src.read_text(encoding="utf-8", errors="replace")
                            md_text = _rewrite_image_paths(md_text, pdf_stem)
                            md_text = _dedupe_repeated_disclaimers(md_text)
                            out_md.write_text(md_text, encoding="utf-8")

                            if images_src.exists():
                                images_dst = images_root / pdf_stem
                                _copy_tree(images_src, images_dst)

                            converted = True
                        else:
                            print("  ! MinerU ran but output MD not found; falling back to PyMuPDF")
                    else:
                        if completed.stderr and _mineru_error_hints_torch_missing(completed.stderr):
                            print("  ! MinerU failed (torch missing); falling back to PyMuPDF")
                        else:
                            print("  ! MinerU failed; falling back to PyMuPDF")
                            if completed.stderr:
                                print(completed.stderr.strip())

                if not converted:
                    _convert_with_pymupdf_layout(pdf_path, out_md, images_root)
                    converted = True

                success += 1
                print(f"  ✓ Wrote: {out_md.name}")
            except Exception as exc:
                failed += 1
                print(f"  ✗ Failed: {exc}")

    print("-" * 60)
    print(f"Done. success={success}, skipped={skipped}, failed={failed}")

    if failed:
        return 2
    if skipped:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
