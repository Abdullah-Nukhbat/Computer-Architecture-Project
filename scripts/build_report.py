"""Build the project report PDF from the part logs in docs/.

Each graph heading in the logs ends with "(data/<file>.png)"; the graph is
placed right under that heading. Member names come from report/members.txt.

Needs LibreOffice for the HTML -> PDF step:
    python3 scripts/build_report.py
Output: report/Project_Report_G8.pdf (and report/report.html)
"""
import base64
import datetime
import html
import os
import re
import shutil
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "report")
LOGS = ["02_part1_log.md", "03_part2_log.md", "04_part3_log.md",
        "05_part4_log.md", "06_part5_log.md", "07_part6_log.md"]
GROUP = 8
BENCHMARKS = "compress95 and cc1"


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def image(path):
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return ""
    # embedded as data: LibreOffice does not load linked images when converting
    data = base64.b64encode(open(full, "rb").read()).decode()
    return (f'<p class="fig" align="center"><img src="data:image/png;base64,{data}" width="620"></p>')


def convert(md, first_page_break):
    out, para, table, code, items = [], [], [], [], []

    def flush():
        nonlocal para, table, code, items
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
        if code:
            out.append("<pre>" + html.escape("\n".join(code)) + "</pre>")
        if table:
            rows = [r for r in table if not re.match(r"^\|[-| ]+\|$", r)]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            h = "".join(f"<th>{inline(c)}</th>" for c in cells[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                           for r in cells[1:])
            out.append(f'<table border="1" cellspacing="0" cellpadding="3"><tr>{h}</tr>{body}</table>')
        para, table, code, items = [], [], [], []

    for line in md.split("\n"):
        if line.startswith("    ") and not para and not items:
            code.append(line[4:])
            continue
        if code and not line.startswith("    "):
            flush()
        if line.startswith("|"):
            if para or items:
                flush()
            table.append(line.strip())
            continue
        if table:
            flush()
        m = re.match(r"^(#{1,3}) (.*)$", line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2)
            fig = re.search(r"\((data/[^)]+\.png)\)\s*$", title)
            title = re.sub(r"\s*\(data/[^)]+\.png\)\s*$", "", title)
            title = re.sub(r"^Part (\d) log: ", r"Part \1: ", title)
            breaks = (level == 1 and first_page_break) or title.startswith("(b) The path")
            style = ' style="page-break-before: always"' if breaks else ""
            out.append(f"<h{level}{style}>{inline(title)}</h{level}>")
            if fig:
                out.append(image(fig.group(1)))
            continue
        if line.startswith("- "):
            if para:
                flush()
            items.append(line[2:].strip())
            continue
        if line.startswith("  ") and items:
            items[-1] += " " + line.strip()
            continue
        if not line.strip():
            flush()
            continue
        para.append(line.strip())
    flush()
    return "\n".join(out)


def part1_extras(md):
    """Part 1's chart list is replaced by the charts themselves."""
    md = re.sub(r"## 1\(c\) Charts\n\n(- data/[^\n]+\n)+", "## 1(c) Charts\n", md)
    return md


def members():
    rows = []
    for line in open(os.path.join(OUT, "members.txt")):
        line = line.strip()
        if line and not line.startswith("#"):
            name, _, roll = line.partition(",")
            rows.append((name.strip(), roll.strip()))
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    mem = "".join(f"<tr><td>{html.escape(n)}</td><td>{html.escape(r)}</td></tr>"
                  for n, r in members())
    cover = f"""
<p class="title" align="center">Design-Space Exploration of an<br>Out-of-Order Superscalar Processor</p>
<p align="center" class="sub">Computer Architecture (BCS-5F), Fall 2026<br>
FAST National University of Computer and Emerging Sciences, Lahore</p>
<p align="center" class="sub"><b>Group {GROUP}</b> &nbsp;|&nbsp; Benchmarks: <b>{BENCHMARKS}</b></p>
<table border="1" cellspacing="0" cellpadding="5" align="center">
<tr><th>Member</th><th>Roll number</th></tr>{mem}</table>
<p align="center" class="sub">Simulator: SimpleScalar 3.0 sim-outorder (PISA), SPEC95 binaries<br>
{datetime.date.today():%d %B %Y}</p>
"""
    body = []
    for i, name in enumerate(LOGS):
        md = open(os.path.join(REPO, "docs", name)).read()
        if name.startswith("02_"):
            md = part1_extras(md)
            # the Part 1 charts have their own headings; attach the images
            for title, png in [("### Instruction mix", "data/part1_instruction_mix.png"),
                               ("### IPC", "data/part1_ipc.png"),
                               ("### Miss rates", "data/part1_miss_rates.png"),
                               ("### Branch mispredictions", "data/part1_mpki.png")]:
                md = re.sub(rf"^{re.escape(title)}( \(data/[^)]+\))?$", f"{title} ({png})",
                            md, flags=re.M)
        body.append(convert(md, first_page_break=True))

    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Project Report G{GROUP}</title>
<style>
body {{ font-family: 'Liberation Serif', 'Times New Roman', serif; font-size: 11pt; }}
h1 {{ font-size: 18pt; }} h2 {{ font-size: 13pt; margin-top: 14pt; }} h3 {{ font-size: 12pt; }}
p {{ text-align: justify; }}
.title {{ font-size: 22pt; font-weight: bold; margin-top: 120pt; }}
.sub {{ font-size: 12pt; }}
table {{ border-collapse: collapse; font-size: 9pt; }}
th {{ background: #e8e8e8; }}
pre, code {{ font-family: 'Liberation Mono', monospace; font-size: 8.5pt; }}
</style></head><body>
{cover}
{''.join(body)}
</body></html>"""
    path = os.path.join(OUT, "report.html")
    open(path, "w").write(doc)

    office = shutil.which("libreoffice") or shutil.which("soffice")
    if not office:
        raise SystemExit("LibreOffice not found; open report/report.html and print it to PDF")
    subprocess.run([office, "--headless", "--infilter=HTML (StarWriter)",
                    "--convert-to", "pdf:writer_pdf_Export", "--outdir", OUT, path],
                   check=True, stdout=subprocess.DEVNULL)
    final = os.path.join(OUT, f"Project_Report_G{GROUP}.pdf")
    os.replace(os.path.join(OUT, "report.pdf"), final)
    print(f"Wrote {os.path.relpath(final, REPO)}")


if __name__ == "__main__":
    main()
