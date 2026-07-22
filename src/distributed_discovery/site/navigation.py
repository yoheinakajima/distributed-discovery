"""Presentation-only navigation, breadcrumbs, and footer rendering."""

from __future__ import annotations

import html
from pathlib import PurePosixPath

PRIMARY_LINKS = (
    ("Home", "index.html"),
    ("Research", "research.html"),
    ("Results", "results.html"),
    ("Labs", "labs.html"),
    ("Papers", "publications.html"),
)

RESOURCE_GROUPS = (
    (
        "Understand",
        (
            ("Program", "program.html"),
            ("Foundations", "foundations.html"),
            ("Applications", "applications.html"),
        ),
    ),
    ("Verify", (("Claims", "claims.html"), ("Evidence", "evidence.html"))),
    ("Use", (("Benchmark", "benchmark.html"), ("Experiment Kit", "experiment-kit.html"))),
    ("Continue", (("Ideas", "ideas.html"),)),
)


def prefix_for(current: str) -> str:
    return "../" * max(0, len(PurePosixPath(current).parts) - 1)


def primary_route(current: str) -> str:
    if current.startswith("research/"):
        return "research.html"
    if current.startswith("labs/"):
        return "labs.html"
    if current.startswith("publications/"):
        return "publications.html"
    return current


def render_header(current: str) -> str:
    prefix = prefix_for(current)
    active = primary_route(current)
    links = "".join(
        '<a href="{}"{}>{}</a>'.format(
            prefix + route,
            ' aria-current="page"' if active == route else "",
            html.escape(label),
        )
        for label, route in PRIMARY_LINKS
    )
    brand_current = ' aria-current="page"' if current == "index.html" else ""
    return (
        '<header class="site-header"><div class="site-shell">'
        f'<a class="brand" href="{prefix}index.html"{brand_current}>'
        '<span class="brand-mark" aria-hidden="true">DD</span>'
        "<span>Distributed Discovery</span></a>"
        '<nav aria-label="Primary navigation"><details class="nav-menu" open>'
        "<summary>Menu</summary>"
        f'<div class="nav-links">{links}</div>'
        "</details></nav></div></header>"
    )


def render_footer(current: str, repository_url: str) -> str:
    prefix = prefix_for(current)
    groups = "".join(
        "<section><h2>{}</h2><ul>{}</ul></section>".format(
            html.escape(title),
            "".join(
                f'<li><a href="{prefix + route}">{html.escape(label)}</a></li>'
                for label, route in links
            ),
        )
        for title, links in RESOURCE_GROUPS
    )
    return (
        '<footer class="site-footer"><div class="site-shell footer-grid">'
        '<section class="footer-intro"><h2>Distributed Discovery</h2>'
        "<p>How groups turn evidence into portfolios of action.</p>"
        "<p><strong>Share the evidence. Diversify the actions.</strong></p></section>"
        f'{groups}<section><h2>Source</h2><ul><li><a href="{repository_url}">Repository</a></li>'
        "<li>Public MIT-licensed research library</li><li>No analytics or tracking</li>"
        "</ul></section></div></footer>"
    )


def render_breadcrumb(current: str, title: str) -> str:
    if "/" not in current:
        return ""
    prefix = prefix_for(current)
    section = current.split("/", 1)[0]
    parents = {
        "research": ("Research", "research.html"),
        "labs": ("Labs", "labs.html"),
        "publications": ("Papers", "publications.html"),
        "benchmark": ("Benchmark", "benchmark.html"),
        "experiment-kit": ("Experiment Kit", "experiment-kit.html"),
    }
    parent = parents.get(section)
    if parent is None:
        return ""
    return (
        '<nav class="breadcrumb" aria-label="Breadcrumb"><ol>'
        f'<li><a href="{prefix}index.html">Home</a></li>'
        f'<li><a href="{prefix}{parent[1]}">{html.escape(parent[0])}</a></li>'
        f'<li aria-current="page">{html.escape(title)}</li>'
        "</ol></nav>"
    )


def render_section_navigation(current: str) -> str:
    prefix = prefix_for(current)
    links: tuple[tuple[str, str], ...]
    if current == "benchmark.html" or current.startswith("benchmark/"):
        links = (
            ("Overview", "benchmark.html"),
            ("Tasks", "benchmark/tasks.html"),
            ("Strategies", "benchmark/protocols.html"),
            ("Measures", "benchmark/metrics.html"),
            ("Results", "benchmark/results.html"),
            ("Attention", "benchmark/attention.html"),
        )
        label = "Benchmark pages"
    elif current == "experiment-kit.html" or current.startswith("experiment-kit/"):
        links = (
            ("Overview", "experiment-kit.html"),
            ("Questions", "experiment-kit/hypotheses.html"),
            ("Assignment", "experiment-kit/design.html"),
            ("Attention", "experiment-kit/attention.html"),
            ("Threshold + dynamics", "experiment-kit/threshold-dynamic.html"),
            ("Power", "experiment-kit/power.html"),
        )
        label = "Experiment Kit pages"
    else:
        return ""
    active = current
    items = "".join(
        '<a href="{}"{}>{}</a>'.format(
            prefix + route,
            ' aria-current="page"' if active == route else "",
            html.escape(name),
        )
        for name, route in links
    )
    return f'<nav class="section-nav" aria-label="{label}">{items}</nav>'
