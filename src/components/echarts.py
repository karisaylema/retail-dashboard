"""ECharts animated stacked-area — embedded via st.components.v1.html."""
import json
import streamlit as st
import pandas as pd

from src.config import PAGE_BG, COLOR_MAP


def render_echarts_area(df: pd.DataFrame) -> None:
    """Render a monthly stacked-area chart using Apache ECharts (non-native Streamlit)."""
    monthly = (
        df.groupby(["month_dt", "category"])["sales"]
        .sum().reset_index().sort_values("month_dt")
    )
    months = sorted(monthly["month_dt"].dt.strftime("%b %Y").unique().tolist())
    cats   = sorted(monthly["category"].unique().tolist())

    series_data: dict = {}
    for cat in cats:
        sub    = monthly[monthly["category"] == cat].copy()
        sub["label"] = sub["month_dt"].dt.strftime("%b %Y")
        lookup = dict(zip(sub["label"], sub["sales"]))
        series_data[cat] = [round(lookup.get(m, 0), 2) for m in months]

    series = []
    for cat in cats:
        clr = COLOR_MAP.get(cat, "#ffffff")
        series.append({
            "name": cat, "type": "line", "stack": "total",
            "smooth": True, "symbol": "circle", "symbolSize": 5,
            "areaStyle": {
                "opacity": 0.72,
                "color": {
                    "type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": clr},
                        {"offset": 1, "color": clr + "18"},
                    ],
                },
            },
            "lineStyle": {"color": clr, "width": 2.5},
            "itemStyle": {"color": clr, "borderColor": "#fff", "borderWidth": 1.5},
            "emphasis": {"focus": "series"},
            "data": series_data[cat],
        })

    option = {
        "backgroundColor": PAGE_BG,
        "animation": True,
        "animationDuration": 1600,
        "animationEasing": "cubicOut",
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "cross",
                "label": {"backgroundColor": "#1e2030", "color": "#e2e8f0"},
                "crossStyle": {"color": "#94a3b8"},
            },
            "backgroundColor": "#1e2030",
            "borderColor": "#374151",
            "borderWidth": 1,
            "textStyle": {"color": "#e2e8f0", "fontSize": 12},
        },
        "legend": {
            "data": cats, "top": 8,
            "textStyle": {"color": "#94a3b8", "fontSize": 12},
            "inactiveColor": "#374151", "icon": "circle",
        },
        "grid": {"left": "3%", "right": "3%", "bottom": "12%", "top": "12%", "containLabel": True},
        "xAxis": {
            "type": "category", "boundaryGap": False, "data": months,
            "axisLine":  {"lineStyle": {"color": "#374151"}},
            "axisLabel": {"color": "#64748b", "rotate": 35, "fontSize": 10},
            "splitLine": {"show": False},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": "#64748b", "fontSize": 10},
            "splitLine": {"lineStyle": {"color": "#1e2535", "type": "dashed"}},
            "axisLine": {"show": False},
        },
        "dataZoom": [
            {"type": "inside", "start": 0, "end": 100},
            {
                "type": "slider", "start": 0, "end": 100,
                "height": 20, "bottom": 4,
                "borderColor": "#374151", "fillerColor": "rgba(99,102,241,0.15)",
                "handleStyle": {"color": "#6366f1"},
                "textStyle": {"color": "#64748b"},
            },
        ],
        "series": series,
    }

    tooltip_fn = """function(params){
        var total=params.reduce(function(s,p){return s+p.value;},0);
        var rows=params.map(function(p){
            return '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:'
                +p.color+';margin-right:6px;"></span>'
                +'<b>'+p.seriesName+'</b>: $'
                +p.value.toLocaleString('en-US',{maximumFractionDigits:0});
        }).join('<br/>');
        return '<div style="padding:4px 2px"><b style="color:#e2e8f0">'+params[0].axisValueLabel+'</b><br/>'
            +rows
            +'<hr style="border-color:#374151;margin:6px 0"/>'
            +'<b style="color:#fbbf24">Total: $'
            +total.toLocaleString('en-US',{maximumFractionDigits:0})+'</b></div>';
    }"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>body{{margin:0;padding:0;background:{PAGE_BG};}} #c{{width:100%;height:430px;}}</style>
</head>
<body>
  <div id="c"></div>
  <script>
    var chart = echarts.init(document.getElementById('c'),'dark');
    var opt   = {json.dumps(option)};
    opt.tooltip.formatter        = {tooltip_fn};
    opt.yAxis.axisLabel.formatter = function(v){{return '$'+v.toLocaleString();}};
    chart.setOption(opt);
    window.addEventListener('resize',function(){{chart.resize();}});
  </script>
</body>
</html>"""

    st.components.v1.html(html, height=450)
