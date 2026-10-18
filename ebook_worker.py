#!/usr/bin/env python3
"""Read-only manuscript QA/build worker. Never prints manuscript excerpts or edits source files."""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

EXPECTED_SECTIONS = 35
SOURCE_DIR = Path(os.environ.get("EBOOK_SOURCE_DIR", ".")).resolve()
OUTPUT_DIR = Path(os.environ.get("EBOOK_OUTPUT_DIR", "worker-output")).resolve()
BUILD_PATH = Path("/home/claude/manuscript/The Rook and the Wolf.docx")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)


def summarize_scan(output):
    counts = {}
    for label, count in re.findall(r"^=== (.*?): (\d+) hits ===$", output, re.M):
        counts[label] = int(count)
    match = re.search(r"Total paragraphs scanned: (\d+)", output)
    if not match:
        raise RuntimeError("Scanner output did not include its paragraph total.")
    return {"paragraphs_scanned": int(match.group(1)), "heuristic_counts": counts}


def inspect_source(source):
    js = r'''
const chapters = require("./chapters.js");
if (!Array.isArray(chapters)) throw new Error("chapters.js must export an array");
const labels = chapters.map(c => c.label);
const paragraphs = chapters.reduce((n, c) => n + (Array.isArray(c.paragraphs) ? c.paragraphs.length : 0), 0);
const words = chapters.reduce((n, c) => n + (Array.isArray(c.paragraphs) ? c.paragraphs.join(" ").trim().split(/\s+/).filter(Boolean).length : 0), 0);
console.log(JSON.stringify({section_count: chapters.length, labels, paragraph_count: paragraphs, word_count: words}));
'''
    result = run(["node", "-e", js], cwd=source)
    if result.returncode != 0:
        raise RuntimeError("Could not load chapters.js. Details withheld to avoid exposing manuscript text.")
    try:
        data = json.loads(result.stdout.strip().splitlines()[-1])
    except Exception as exc:
        raise RuntimeError("Could not parse manuscript metadata.") from exc
    if data.get("section_count") != EXPECTED_SECTIONS:
        raise RuntimeError(f"Expected {EXPECTED_SECTIONS} sections; found {data.get('section_count')}. Build stopped.")
    if data.get("paragraph_count", 0) <= 0 or data.get("word_count", 0) <= 0:
        raise RuntimeError("Manuscript appears empty. Build stopped.")
    return data


def main():
    source = SOURCE_DIR
    if not (source / "chapters.js").is_file():
        raise SystemExit("Missing chapters.js in the private source repository. No changes made.")
    if not (source / "scan_slop.js").is_file() or not (source / "build.js").is_file():
        raise SystemExit("Expected scan_slop.js and build.js beside chapters.js. No changes made.")

    metadata = inspect_source(source)
    scan = run(["node", "scan_slop.js"], cwd=source)
    if scan.returncode != 0:
        raise SystemExit("Slop scanner failed. Build stopped; no source files changed.")
    scan_summary = summarize_scan(scan.stdout)

    # build.js writes to this fixed path; this is a temporary runner path, not the master.
    BUILD_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUILD_PATH.unlink(missing_ok=True)
    build = run(["node", "build.js"], cwd=source)
    if build.returncode != 0 or not BUILD_PATH.is_file():
        raise SystemExit("DOCX build failed. Master source was not changed; no artifact published.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_docx = OUTPUT_DIR / "The Rook and the Wolf - QA draft.docx"
    shutil.copy2(BUILD_PATH, output_docx)

    report = {
        "result": "built_needs_human_quality_review",
        "source_files_modified": False,
        "master_replaced": False,
        "drive_upload_attempted": False,
        "section_count": metadata["section_count"],
        "paragraph_count": metadata["paragraph_count"],
        "word_count": metadata["word_count"],
        "scan": scan_summary,
        "docx_bytes": output_docx.stat().st_size,
        "notes": [
            "Scanner counts are heuristic flags, not proof of AI writing or quality.",
            "This run does not perform a literary review, historical fact-check, or visual DOCX inspection.",
            "The output is a draft artifact only; approval is required before replacing a master or uploading to Drive."
        ]
    }
    (OUTPUT_DIR / "qa-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("eBook worker completed.")
    print(f"Sections: {metadata['section_count']}; paragraphs: {metadata['paragraph_count']}; words: {metadata['word_count']}.")
    print(f"Scanner checked {scan_summary['paragraphs_scanned']} paragraphs and reported {len(scan_summary['heuristic_counts'])} heuristic categories.")
    print(f"DOCX draft bytes: {report['docx_bytes']}.")
    print("Result: draft built; human quality review still required. No source/master/Drive changes made.")


if __name__ == "__main__":
    main()
