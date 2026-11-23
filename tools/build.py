"""Build the white-paper pages and charts from whitepaper/en.md and whitepaper/ja.md.

python tools/build.py   (needs pandoc)
Writes: whitepaper/chart_en.svg, whitepaper/chart_ja.svg, index.html (English), ja/index.html (Japanese).
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# share of 300 jobs completed, mean of 3 runs (warehouse simulation, November 2026)
DATA = {
    "10": {"yorosix": 0.349, "auction": 0.292, "nearest": 0.311, "random": 0.304, "broadcast": 0.167},
    "30": {"yorosix": 0.504, "auction": 0.437, "nearest": 0.410, "random": 0.402, "broadcast": 0.181},
    "100": {"yorosix": 0.548, "auction": 0.480, "nearest": 0.407, "random": 0.410, "broadcast": 0.168},
}
METHODS = ["yorosix", "auction", "nearest", "random", "broadcast"]
LABELS = {
    "en": {"yorosix": "YOROSIX AI", "auction": "Auction", "nearest": "Nearest robot", "random": "Random",
           "broadcast": "Ask everyone", "title": "YOROSIX AI completes the most jobs at every fleet size",
           "sub": "Share of 300 jobs completed, mean of 3 runs, simulated warehouse", "fleet": "{} robots"},
    "ja": {"yorosix": "YOROSIX AI", "auction": "オークション", "nearest": "一番近いロボット", "random": "ランダム",
           "broadcast": "全員に聞く", "title": "YOROSIX AI はどの台数でも最も多くの仕事を完了した",
           "sub": "300件の仕事の完了率（3回の平均、倉庫シミュレーション）", "fleet": "ロボット{}台"},
}


def chart(lang):
    L = LABELS[lang]
    base, scale, gw, bw, gap = 300, 200 / 0.6, 680 / 3, 30, 6
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 340" role="img" aria-label="{L["title"]}" '
           'font-family="-apple-system, Segoe UI, Hiragino Sans, Noto Sans JP, sans-serif" font-size="11.5">',
           '<rect width="760" height="340" fill="#ffffff"/>',
           f'<text x="40" y="28" font-size="15" font-weight="600" fill="#1d1d1b">{L["title"]}</text>',
           f'<text x="40" y="48" fill="#6b6a65">{L["sub"]}</text>']
    shade = {m: (1 if m == "yorosix" else 0.85 - i * 0.15) for i, m in enumerate(METHODS)}
    fill = lambda m: "#2a7ab8" if m == "yorosix" else "#9b9a93"
    for i, m in enumerate(METHODS):
        out.append(f'<rect x="{40 + i * 136}" y="64" width="12" height="12" rx="2" fill="{fill(m)}" fill-opacity="{shade[m]:.2f}"/>')
        out.append(f'<text x="{58 + i * 136}" y="75" fill="#1d1d1b"{" font-weight=\"600\"" if m == "yorosix" else ""}>{L[m]}</text>')
    out.append(f'<line x1="40" x2="720" y1="{base}" y2="{base}" stroke="#b9b7b0"/>')
    for g, (fleet, vals) in enumerate(DATA.items()):
        gx = 40 + g * gw + (gw - len(METHODS) * (bw + gap)) / 2
        for i, m in enumerate(METHODS):
            v = vals[m]; x = gx + i * (bw + gap); h = v * scale
            out.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="2" fill="{fill(m)}" fill-opacity="{shade[m]:.2f}"/>')
            out.append(f'<text x="{x + bw / 2:.1f}" y="{base - h - 6:.1f}" text-anchor="middle" font-size="10.5" '
                       f'fill="{"#1d1d1b" if m == "yorosix" else "#6b6a65"}"{" font-weight=\"600\"" if m == "yorosix" else ""}>{round(v * 100)}%</text>')
        out.append(f'<text x="{gx + (len(METHODS) * (bw + gap) - gap) / 2:.1f}" y="{base + 22}" text-anchor="middle" font-size="13" fill="#1d1d1b">{L["fleet"].format(fleet)}</text>')
    out.append("</svg>")
    (ROOT / "whitepaper" / f"chart_{lang}.svg").write_text("\n".join(out), encoding="utf-8")


PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<style>
  :root {{ --bg:#fbfaf7; --fg:#1d1d1b; --muted:#6b6a65; --line:#dcdad3; --accent:#2a7ab8; --card:#ffffff; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg:#1b1b1a; --fg:#ecebe6; --muted:#a3a29c; --line:#3a3936; --accent:#5fa8e0; --card:#232321; }} }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font:17px/1.75 -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif; }}
  main {{ max-width:760px; margin:0 auto; padding:28px 16px 64px; }}
  nav {{ display:flex; justify-content:space-between; font-size:14px; margin-bottom:28px; }}
  nav a {{ color:var(--muted); text-decoration:none; margin-left:12px; }} nav a.cur {{ color:var(--fg); font-weight:600; }}
  h1 {{ font-size:32px; line-height:1.25; margin:0 0 8px; }}
  h2 {{ font-size:22px; margin:44px 0 10px; padding-top:12px; border-top:1px solid var(--line); }}
  a {{ color:var(--accent); }}
  table {{ border-collapse:collapse; width:100%; font-size:15px; margin:16px 0; }}
  th, td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
  th {{ color:var(--muted); font-weight:600; }}
  img {{ max-width:100%; height:auto; border-radius:8px; border:1px solid var(--line); background:#fff; }}
  .demo {{ display:block; text-align:center; padding:14px; border:1px solid var(--accent); border-radius:10px; font-weight:600; text-decoration:none; margin:16px 0; background:var(--card); }}
  em {{ color:var(--muted); font-style:normal; }}
  .wrap {{ overflow-x:auto; }}
</style>
</head>
<body>
<main>
<nav><span>YOROSIX</span><span><a href="{en_href}" class="{en_cur}">English</a><a href="{ja_href}" class="{ja_cur}">日本語</a></span></nav>
{body}
</main>
</body>
</html>
"""


def page(lang):
    md = (ROOT / "whitepaper" / f"{lang}.md").read_text(encoding="utf-8")
    prefix = "whitepaper/" if lang == "en" else "../whitepaper/"
    md = md.replace("](chart_", f"]({prefix}chart_")
    if lang == "en":
        md = md.replace("](../demo/)", "](demo/?lang=en)")
    body = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5"], input=md, capture_output=True, text=True, check=True).stdout
    body = body.replace("<table>", '<div class="wrap"><table>').replace("</table>", "</table></div>")
    for label in ("Open the demo →", "デモを開く →"):
        body = body.replace(f"<strong>{label}</strong></a>", f"{label}</a>")
    body = body.replace('<p><a href="demo/?lang=en">', '<p><a class="demo" href="demo/?lang=en">')
    body = body.replace('<p><a href="../demo/?lang=ja">', '<p><a class="demo" href="../demo/?lang=ja">')
    title = md.splitlines()[0].lstrip("# ").strip()
    desc = {"en": "One machine is small. Machines that rely on each other, and on people, can do together what none can do alone.",
            "ja": "1台の機械の力は小さい。互いに、そして人に頼り合える機械なら、1台ではできないことを一緒に成し遂げられる。"}[lang]
    html = PAGE.format(lang=lang, title=title, desc=desc, body=body,
                       en_href="./" if lang == "en" else "../", ja_href="ja/" if lang == "en" else "./",
                       en_cur="cur" if lang == "en" else "", ja_cur="cur" if lang == "ja" else "")
    target = ROOT / ("index.html" if lang == "en" else "ja/index.html")
    target.parent.mkdir(exist_ok=True)
    target.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    for lang in ("en", "ja"):
        chart(lang)
        page(lang)
    print("built")
