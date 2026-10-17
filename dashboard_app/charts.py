"""
charts.py — Line Chart with Gradient Fill + Donut Chart
========================================================
"""

import math
import tkinter as tk
import theme as T
from neumorphic import neumorphic_card, rounded_rect


def draw_line_chart(canvas, x, y, w=520, h=320):
    """Smooth line chart with purple gradient fill below the curve."""
    neumorphic_card(canvas, x, y, w, h)

    pad_l, pad_r, pad_t, pad_b = 55, 25, 55, 45
    chart_x = x + pad_l
    chart_y = y + pad_t
    chart_w = w - pad_l - pad_r
    chart_h = h - pad_t - pad_b

    # Title
    canvas.create_text(x + 30, y + 22, text="Revenue Overview",
                       font=T.FONT_SUBHEADING, fill=T.TEXT_PRIMARY, anchor=tk.W)
    canvas.create_text(x + 30, y + 42, text="Last 12 months",
                       font=T.FONT_TINY, fill=T.TEXT_SECONDARY, anchor=tk.W)

    # Legend dots
    canvas.create_oval(x + w - 120, y + 20, x + w - 112, y + 28,
                       fill=T.PURPLE, outline="")
    canvas.create_text(x + w - 108, y + 24, text="Revenue", font=T.FONT_TINY,
                       fill=T.TEXT_SECONDARY, anchor=tk.W)
    canvas.create_oval(x + w - 55, y + 20, x + w - 47, y + 28,
                       fill=T.ORANGE, outline="")
    canvas.create_text(x + w - 43, y + 24, text="Cost", font=T.FONT_TINY,
                       fill=T.TEXT_SECONDARY, anchor=tk.W)

    # Grid lines + Y-axis labels
    for i in range(5):
        gy = chart_y + chart_h - i * (chart_h / 4)
        canvas.create_line(chart_x, gy, chart_x + chart_w, gy,
                           fill=T.TEXT_MUTED, width=1, dash=(3, 6))
        val = f"${i * 25}k"
        canvas.create_text(chart_x - 10, gy, text=val, font=T.FONT_TINY,
                           fill=T.TEXT_MUTED, anchor=tk.E)

    # X-axis labels
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, m in enumerate(months):
        mx = chart_x + i * (chart_w / 11)
        canvas.create_text(mx, chart_y + chart_h + 16, text=m,
                           font=T.FONT_TINY, fill=T.TEXT_MUTED)

    # Revenue data (purple line)
    rev_data = [30, 45, 38, 55, 48, 62, 70, 65, 75, 82, 78, 92]
    max_val = 100
    rev_points = []
    for i, v in enumerate(rev_data):
        px = chart_x + i * (chart_w / 11)
        py = chart_y + chart_h - (v / max_val) * chart_h
        rev_points.append((px, py))

    # Gradient fill under purple curve
    fill_points = list(rev_points)
    fill_points.append((rev_points[-1][0], chart_y + chart_h))
    fill_points.insert(0, (rev_points[0][0], chart_y + chart_h))
    # Draw gradient stripes
    for row in range(int(chart_h)):
        ry = chart_y + row
        t = row / chart_h
        # Interpolate purple→transparent
        r = int(138 * (1 - t * 0.85))
        g = int(43 * (1 - t * 0.85))
        b = int(226 * (1 - t * 0.85))
        # Only color pixels inside the polygon
        # We'll approximate with decreasing alpha via color shift toward BG
        bg_r, bg_g, bg_b = 0x1e, 0x1f, 0x2b
        blend = t * 0.9
        fr = int(r * (1 - blend) + bg_r * blend)
        fg = int(g * (1 - blend) + bg_g * blend)
        fb = int(b * (1 - blend) + bg_b * blend)
        col = f"#{fr:02x}{fg:02x}{fb:02x}"

        # Find left/right intersection at this y
        intersections = _line_intersections(rev_points, ry)
        if len(intersections) >= 2:
            canvas.create_line(intersections[0], ry, intersections[-1], ry,
                               fill=col, width=1)
        elif len(intersections) == 1:
            canvas.create_line(intersections[0], ry, intersections[0] + 1, ry,
                               fill=col, width=1)

    # Purple line on top
    for i in range(len(rev_points) - 1):
        canvas.create_line(rev_points[i][0], rev_points[i][1],
                           rev_points[i + 1][0], rev_points[i + 1][1],
                           fill=T.PURPLE, width=3, smooth=True)

    # Dots on purple line
    for px, py in rev_points:
        canvas.create_oval(px - 4, py - 4, px + 4, py + 4,
                           fill=T.PURPLE, outline=T.BG, width=2)

    # Orange cost line (simpler, thinner)
    cost_data = [20, 22, 25, 28, 30, 32, 35, 34, 38, 40, 42, 45]
    cost_pts = []
    for i, v in enumerate(cost_data):
        px = chart_x + i * (chart_w / 11)
        py = chart_y + chart_h - (v / max_val) * chart_h
        cost_pts.append((px, py))
    for i in range(len(cost_pts) - 1):
        canvas.create_line(cost_pts[i][0], cost_pts[i][1],
                           cost_pts[i + 1][0], cost_pts[i + 1][1],
                           fill=T.ORANGE, width=2, smooth=True)
    for px, py in cost_pts:
        canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                           fill=T.ORANGE, outline=T.BG, width=2)


def _line_intersections(points, y):
    """Find x-values where the polyline crosses a given y."""
    hits = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if (y1 <= y <= y2) or (y2 <= y <= y1):
            if y2 - y1 == 0:
                hits.append(x1)
            else:
                t = (y - y1) / (y2 - y1)
                hits.append(x1 + t * (x2 - x1))
    return sorted(hits)


def draw_donut_chart(canvas, x, y, w=280, h=300):
    """Donut chart (circular progress) inside a neumorphic card."""
    neumorphic_card(canvas, x, y, w, h)

    # Title
    canvas.create_text(x + 20, y + 22, text="Performance",
                       font=T.FONT_SUBHEADING, fill=T.TEXT_PRIMARY, anchor=tk.W)
    canvas.create_text(x + 20, y + 42, text="Overall score",
                       font=T.FONT_TINY, fill=T.TEXT_SECONDARY, anchor=tk.W)

    # Donut dimensions
    cx, cy = x + w // 2, y + h // 2 + 15
    outer_r = 80
    inner_r = 55

    # Background ring (dark neumorphic)
    canvas.create_oval(cx - outer_r - 4, cy - outer_r - 4,
                       cx + outer_r + 4, cy + outer_r + 4,
                       fill=T.BG_DARK, outline="")
    canvas.create_oval(cx - outer_r, cy - outer_r,
                       cx + outer_r, cy + outer_r,
                       fill=T.BG_LIGHT, outline="")

    # Segments: purple=72%, orange=15%, green=13%
    segments = [
        (72, T.PURPLE),
        (15, T.ORANGE),
        (13, T.GREEN),
    ]
    start = 90
    for pct, col in segments:
        extent = 360 * pct / 100
        canvas.create_arc(
            cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r,
            start=start, extent=extent, fill=col, outline=T.BG, width=2,
            style=tk.PIESLICE
        )
        start += extent

    # Inner circle (cut out the donut hole)
    canvas.create_oval(cx - inner_r - 3, cy - inner_r - 3,
                       cx + inner_r + 3, cy + inner_r + 3,
                       fill=T.BG_DARK, outline="")
    canvas.create_oval(cx - inner_r, cy - inner_r,
                       cx + inner_r, cy + inner_r,
                       fill=T.BG, outline="")

    # Center number
    canvas.create_text(cx, cy - 8, text="72%", font=T.FONT_BIG_NUM,
                       fill=T.TEXT_PRIMARY)
    canvas.create_text(cx, cy + 22, text="Completed", font=T.FONT_TINY,
                       fill=T.TEXT_SECONDARY)

    # Legend at bottom
    leg_y = y + h - 30
    items = [("Revenue", T.PURPLE), ("Cost", T.ORANGE), ("Profit", T.GREEN)]
    leg_x = x + 25
    for label, col in items:
        canvas.create_oval(leg_x, leg_y, leg_x + 8, leg_y + 8,
                           fill=col, outline="")
        canvas.create_text(leg_x + 14, leg_y + 4, text=label,
                           font=T.FONT_TINY, fill=T.TEXT_SECONDARY, anchor=tk.W)
        leg_x += 80
