"""Central configuration — colors, AWS settings, theme constants."""
import os

# ── AWS ───────────────────────────────────────────────────────────────────────
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET  = os.getenv("S3_BUCKET",  "retail-dashboard-285051607109")
S3_KEY     = os.getenv("S3_KEY",     "data/retail_data.csv")
LOCAL_PATH = os.getenv("LOCAL_PATH", "data/retail_data.csv")

# ── Theme ─────────────────────────────────────────────────────────────────────
PAGE_BG    = "#0f1117"
SIDEBAR_BG = "#1a1d27"
PLOT_BG    = "#16192a"
PAPER_BG   = "#0f1117"
GRID_CLR   = "#1e2535"
TEXT_CLR   = "#94a3b8"

TOOLTIP = dict(
    bgcolor="#1e2030",
    bordercolor="#374151",
    font=dict(color="#e2e8f0", size=12),
)

# ── Category palette ──────────────────────────────────────────────────────────
COLOR_MAP = {
    "Furniture":       "#818cf8",
    "Technology":      "#34d399",
    "Office Supplies": "#fbbf24",
}

# ── KPI card gradients ────────────────────────────────────────────────────────
KPI_GRADIENTS = {
    "sales":   "linear-gradient(135deg,#667eea,#764ba2)",
    "profit":  "linear-gradient(135deg,#11998e,#38ef7d)",
    "orders":  "linear-gradient(135deg,#f7971e,#ffd200)",
    "aov":     "linear-gradient(135deg,#ee0979,#ff6a00)",
    "margin_pos": "linear-gradient(135deg,#4776e6,#8e54e9)",
    "margin_neg": "linear-gradient(135deg,#c0392b,#e74c3c)",
}
