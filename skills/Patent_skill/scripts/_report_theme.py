"""Shared design tokens for every generated report surface.

All hex values below are copied verbatim from the `dataviz` skill's validated
reference palette (references/palette.md) - categorical slot order, sequential
blue ramp and status palette are NOT re-derived here, so no new colors need
re-validation. If the palette ever changes, edit only this file; every
report/landscape builder script imports it instead of hand-rolling its own
<style> colors.
"""

# Categorical slots 1-8, fixed order (never cycle past 8; fold extras into "Other").
CATEGORICAL = [
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]

# Sequential blue ramp, light -> dark, for magnitude encodings (bar length, map fill).
SEQUENTIAL = {
    100: "#cde2fb", 150: "#b7d3f6", 200: "#9ec5f4", 250: "#86b6ef",
    300: "#6da7ec", 350: "#5598e7", 400: "#3987e5", 450: "#2a78d6",
    500: "#256abf", 550: "#1c5cab", 600: "#184f95", 650: "#104281", 700: "#0d366b",
}

# Status palette - fixed, never themed, never reused for a plain categorical series.
STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

# Chart chrome / ink (light mode only - dark mode intentionally out of scope this round).
INK = {
    "surface": "#fcfcfb",
    "page": "#f9f9f7",
    "primary": "#0b0b0b",
    "secondary": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "border": "rgba(11,11,11,0.10)",
}

# Product accent (slot 1 blue) reused for hero gradients / links / nav across all pages.
ACCENT = CATEGORICAL[0]
ACCENT_SOFT = SEQUENTIAL[100]


def status_for(text):
    """Classify a free-text status/priority signal into good/warning/serious/critical."""
    value = str(text or "").lower()
    if any(t in value for t in ("active", "有效", "granted", "授权", "good", "high")):
        return "good"
    if any(t in value for t in ("pending", "申请", "公开", "审查", "medium")):
        return "warning"
    if any(t in value for t in ("expired", "失效", "abandoned", "放弃", "watch", "low")):
        return "serious"
    if any(t in value for t in ("unknown", "需", "require", "未", "核验", "待")):
        return "warning"
    return "warning"


def css_tokens():
    """A :root{--...} block every page includes once, near the top of <style>."""
    seq = "".join(f"--seq-{k}:{v};" for k, v in SEQUENTIAL.items())
    cat = "".join(f"--cat-{i + 1}:{c};" for i, c in enumerate(CATEGORICAL))
    return (
        ":root{"
        f"--ink:{INK['primary']};--muted:{INK['secondary']};--faint:{INK['muted']};"
        f"--line:{INK['grid']};--axis:{INK['axis']};--bg:{INK['page']};--surface:{INK['surface']};"
        f"--accent:{ACCENT};--accent-soft:{ACCENT_SOFT};--border:{INK['border']};"
        f"--good:{STATUS['good']};--warning:{STATUS['warning']};--serious:{STATUS['serious']};--critical:{STATUS['critical']};"
        f"{seq}{cat}"
        "}"
    )


def shared_component_css():
    """Hero header, metric cards, nav, tooltip and table-view CSS shared by all pages."""
    return """
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.hero{background:linear-gradient(135deg,var(--surface),var(--accent-soft));border:1px solid var(--line);border-radius:20px;padding:26px 30px;box-shadow:0 8px 24px rgba(11,11,11,.05)}
.eyebrow{color:var(--accent);font-size:12px;font-weight:800;letter-spacing:.08em}
.hero h1{margin:9px 0 7px;font-size:29px}
.hero p{margin:0;color:var(--muted);line-height:1.7}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.metric{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px}
.metric b,.metric-value{display:block;color:var(--accent);font-size:23px}
.metric span,.metric-label{display:block;margin-top:5px;font-size:13px;font-weight:700}
.metric small,.metric-hint{display:block;color:var(--muted);margin-top:5px;font-size:11px}
.notice{background:color-mix(in srgb,var(--warning) 12%,var(--surface));border:1px solid color-mix(in srgb,var(--warning) 45%,var(--surface));border-radius:12px;padding:13px 16px;color:#71531b;font-size:12px;line-height:1.7;margin:18px 0}
a{color:var(--accent)}
.status-pill{display:inline-flex;align-items:center;gap:5px;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:700}
.status-pill.good{background:color-mix(in srgb,var(--good) 14%,var(--surface));color:#0a6b0a}
.status-pill.warning{background:color-mix(in srgb,var(--warning) 20%,var(--surface));color:#7a5600}
.status-pill.serious{background:color-mix(in srgb,var(--serious) 18%,var(--surface));color:#8a3b1f}
.status-pill.critical{background:color-mix(in srgb,var(--critical) 14%,var(--surface));color:#8a1f1f}
.status-pill i{width:7px;height:7px;border-radius:50%;background:currentColor}
.chart-card{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:14px;box-shadow:0 4px 14px rgba(11,11,11,.04)}
.chart-card svg{display:block;width:100%;height:auto}
.chart-note{border-top:1px solid var(--line);padding:10px 12px 3px;color:var(--muted);font-size:12px;line-height:1.6}
.chart-table{margin-top:8px}
.chart-table summary{cursor:pointer;color:var(--muted);font-size:12px;padding:4px 2px}
.chart-table table{width:100%;border-collapse:collapse;font-size:12px;margin-top:6px}
.chart-table th,.chart-table td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
.svg-bar-row:hover .svg-bar-fill,.svg-bar-row:hover rect.svg-bar-fill{filter:brightness(1.08)}
.svg-tt{pointer-events:none}
.mermaid{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;overflow:auto}
.mermaid-fallback{margin-top:8px;font-size:12px;color:var(--muted)}
.mermaid-fallback pre{white-space:pre-wrap;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px}
.scope-chips{display:flex;flex-wrap:wrap;gap:6px 0;margin:10px 0}
.chip{display:inline-flex;align-items:center;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:12px;color:var(--ink);margin:0 6px 0 0}
.chip strong{color:var(--accent);font-weight:700;margin-right:4px}
.chip.small{padding:2px 9px;font-size:11px;background:var(--accent-soft);border-color:transparent;margin:0 4px 4px 0}
.mx-dot{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:6px;font-size:12px;font-weight:700}
.mx-dot.yes{background:var(--good);color:#fff}
.mx-dot.no{background:var(--line);color:var(--muted)}
"""


MERMAID_BOOTSTRAP = """<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/+esm";
mermaid.initialize({
  startOnLoad: true,
  theme: "base",
  themeVariables: {
    primaryColor: "%(accent_soft)s",
    primaryTextColor: "%(ink)s",
    primaryBorderColor: "%(accent)s",
    lineColor: "%(axis)s",
    fontFamily: "-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif"
  }
});
</script>""" % {"accent_soft": ACCENT_SOFT, "ink": INK["primary"], "accent": ACCENT, "axis": INK["axis"]}
