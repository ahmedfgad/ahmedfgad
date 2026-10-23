"""Build the animated SVG banners used by the profile README.

Run from the repository root:  python3 tools/build_assets.py
It writes light and dark variants of each banner to assets/. The README picks
one with <picture> so it follows the GitHub theme the visitor has chosen.

Everything is plain SVG + CSS (no scripts, no web fonts) because GitHub renders
README images with <img>, which ignores JavaScript and external resources.
Every animation is switched off under prefers-reduced-motion, and each element
sits at its final position by default, so the still frame is the finished design.
"""

import math
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

THEMES = {
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "faint": "#d8dee4",
        "dot": "#8c959f",
        "blue": "#2563eb",
        "amber": "#d97706",
        "pygad": "#0876d8",
    },
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#9198a1",
        "faint": "#262c36",
        "dot": "#6e7681",
        "blue": "#4c8dff",
        "amber": "#f5b13d",
        "pygad": "#3b9cf0",
    },
}

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def svg_doc(width, height, label, style, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{label}">\n'
        f"<title>{label}</title>\n<style>\n{style}\n{REDUCED_MOTION}\n</style>\n{body}\n</svg>\n"
    )


def panel(width, height, c):
    return (
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" '
        f'fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="1.5"/>'
    )


# ---------------------------------------------------------------- header ---

def header(c):
    """Name and roles on the left, a genetic algorithm population on the right.

    The dots start scattered across a fitness landscape and converge on the
    optimum over a few "generations", then the cycle repeats.
    """
    w, h = 1200, 300
    rng = random.Random(42)
    ox, oy = 958, 146  # the optimum
    cycle = 11

    dots, keyframes = [], []
    for i in range(26):
        # Final position: a tight cluster around the optimum.
        ang = rng.uniform(0, 2 * math.pi)
        r = abs(rng.gauss(0, 13))
        fx, fy = ox + r * math.cos(ang), oy + r * math.sin(ang) * 0.75
        # Start anywhere on the landscape.
        sx, sy = rng.uniform(690, 1170), rng.uniform(28, 272)
        # Two intermediate generations, drifting closer with some noise.
        mid = []
        for frac in (0.45, 0.8):
            mx = sx + (fx - sx) * frac + rng.uniform(-28, 28) * (1 - frac)
            my = sy + (fy - sy) * frac + rng.uniform(-28, 28) * (1 - frac)
            mid.append((mx - fx, my - fy))
        d0 = (sx - fx, sy - fy)
        keyframes.append(
            f"@keyframes p{i} {{"
            f"0% {{ transform: translate({d0[0]:.0f}px,{d0[1]:.0f}px); opacity: 0; fill: {c['dot']}; }}"
            f"6% {{ transform: translate({d0[0]:.0f}px,{d0[1]:.0f}px); opacity: 1; }}"
            f"30% {{ transform: translate({mid[0][0]:.0f}px,{mid[0][1]:.0f}px); }}"
            f"52% {{ transform: translate({mid[1][0]:.0f}px,{mid[1][1]:.0f}px); fill: {c['dot']}; }}"
            f"72%, 90% {{ transform: translate(0,0); opacity: 1; fill: {c['blue']}; }}"
            f"100% {{ transform: translate(0,0); opacity: 0; fill: {c['blue']}; }} }}"
            f".p{i} {{ animation: p{i} {cycle}s cubic-bezier(.45,0,.25,1) {rng.uniform(0, .25):.2f}s infinite; }}"
        )
        dots.append(f'<circle class="p{i}" cx="{fx:.1f}" cy="{fy:.1f}" r="5" fill="{c["blue"]}"/>')

    contours = "".join(
        f'<ellipse cx="{ox}" cy="{oy}" rx="{rx}" ry="{rx * 0.62:.0f}" fill="none" '
        f'stroke="{c["faint"]}" stroke-width="1.5" transform="rotate(-12 {ox} {oy})"/>'
        for rx in (34, 72, 114, 160, 210, 262)
    )

    gens = [("generation 0", 0, 24), ("generation 12", 26, 50), ("generation 30", 52, 70), ("best found", 72, 100)]
    gen_css = ""
    gen_svg = ""
    for i, (label, start, end) in enumerate(gens):
        gen_css += (
            f"@keyframes g{i} {{ 0%, {max(start - 1, 0)}% {{ opacity: 0; }} {start + 1}%, {end - 1}% {{ opacity: 1; }} "
            f"{min(end + 1, 100)}%, 100% {{ opacity: 0; }} }}"
            f".g{i} {{ opacity: 0; animation: g{i} {cycle}s linear infinite; }}"
        )
        # The last label is the one shown when motion is reduced.
        gen_svg += (
            f'<text class="g{i}" x="1170" y="284" text-anchor="end" font-size="15" '
            f'fill="{c["muted"]}" font-family="{FONT}">{label}</text>'
        )
    gen_css += ".g3 { opacity: 1; }"

    style = "\n".join(keyframes) + f"""
@keyframes star {{ 0%, 70% {{ opacity: .25; transform: scale(.7); }} 76% {{ opacity: 1; transform: scale(1.25); }} 82%, 92% {{ opacity: 1; transform: scale(1); }} 100% {{ opacity: .25; transform: scale(.7); }} }}
.star {{ transform-box: fill-box; transform-origin: center; animation: star {cycle}s ease-in-out infinite; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
.t1 {{ animation: rise .6s ease-out both; }}
.t2 {{ animation: rise .6s ease-out .15s both; }}
.t3 {{ animation: rise .6s ease-out .3s both; }}
.t4 {{ animation: rise .6s ease-out .45s both; }}
{gen_css}"""

    body = f"""{panel(w, h, c)}
<g font-family="{FONT}">
  <text class="t1" x="56" y="112" font-size="54" font-weight="700" fill="{c['text']}">Ahmed Gad</text>
  <text class="t2" x="58" y="156" font-size="22" fill="{c['muted']}">Machine learning researcher and technical author</text>
  <text class="t3" x="58" y="200" font-size="22" fill="{c['text']}">Founder of <tspan font-weight="700" fill="{c['blue']}">Vilvik</tspan>  ·  Creator of <tspan font-weight="700" fill="{c['pygad']}">PyGAD</tspan></text>
  <text class="t4" x="58" y="244" font-size="17" fill="{c['muted']}">Evolutionary algorithms, deep learning, and the tools that make them easy to use.</text>
</g>
<g>
  {contours}
  {''.join(dots)}
  <path class="star" d="M{ox} {oy - 11} L{ox + 3.2} {oy - 3.4} L{ox + 11} {oy - 3.4} L{ox + 4.8} {oy + 1.6} L{ox + 7} {oy + 9.5} L{ox} {oy + 4.7} L{ox - 7} {oy + 9.5} L{ox - 4.8} {oy + 1.6} L{ox - 11} {oy - 3.4} L{ox - 3.2} {oy - 3.4} Z" fill="{c['amber']}"/>
  {gen_svg}
</g>"""
    return svg_doc(w, h, "Ahmed Gad. Machine learning researcher and technical author. Founder of Vilvik, creator of PyGAD.", style, body)


# --------------------------------------------------------- product cards ---

def nested_mark(src, x, y, size):
    """Re-wrap a standalone logo SVG as a nested <svg> placed at (x, y)."""
    text = re.sub(r"<\?xml[^>]*>\s*", "", src)
    open_tag = re.match(r"\s*<svg[^>]*>", text).group(0)
    view_box = re.search(r'viewBox="([^"]+)"', open_tag).group(1)
    inner = text[len(open_tag):text.rindex("</svg>")]
    inner = re.sub(r"<title[^>]*>.*?</title>", "", inner, flags=re.S)
    return (
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{view_box}" '
        f'aria-hidden="true" overflow="visible">{inner}</svg>'
    )


def card(c, *, label, kicker, title, title_color, lines, link, mark, mark_style):
    w, h = 1200, 230
    text_lines = "".join(
        f'<text class="t{i + 3}" x="262" y="{136 + i * 30}" font-size="20" fill="{c["muted"]}">{line}</text>'
        for i, line in enumerate(lines)
    )
    style = f"""
@keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
.t1 {{ animation: rise .5s ease-out .5s both; }}
.t2 {{ animation: rise .5s ease-out .65s both; }}
.t3 {{ animation: rise .5s ease-out .8s both; }}
.t4 {{ animation: rise .5s ease-out .95s both; }}
.t5 {{ animation: rise .5s ease-out 1.1s both; }}
{mark_style}"""
    body = f"""{panel(w, h, c)}
{mark}
<g font-family="{FONT}">
  <text class="t1" x="264" y="56" font-size="14" font-weight="700" letter-spacing="2.5" fill="{c['muted']}">{kicker}</text>
  <text class="t2" x="260" y="104" font-size="46" font-weight="800" fill="{title_color}">{title}</text>
  {text_lines}
  <text class="t5" x="1164" y="200" text-anchor="end" font-size="18" font-weight="600" fill="{title_color}">{link} →</text>
</g>"""
    return svg_doc(w, h, label, style, body)


VILVIK_STYLE = """
/* Only the animated parts get a fill-box origin; the inner mirror groups keep
   their own transform attribute untouched. */
.vm [class^="vlogo-anim__"] { transform-box: fill-box; transform-origin: center; }
@keyframes drop {
  0%   { opacity: 0; transform: translateY(-220%) scale(.75); }
  60%  { opacity: 1; transform: translateY(8%) scale(1.04); }
  80%  { transform: translateY(-3%) scale(.98); }
  100% { opacity: 1; transform: none; }
}
@keyframes glint {
  0%, 86%, 100% { transform: none; }
  90% { transform: translateY(-9%) scale(1.06); }
  94% { transform: translateY(2%) scale(.99); }
}
.vlogo-anim__horn-l  { animation: drop .85s cubic-bezier(.34,1.56,.64,1) both 0s, glint 7s ease-in-out 1.9s infinite; }
.vlogo-anim__outer-l { animation: drop .85s cubic-bezier(.34,1.56,.64,1) both .2s; }
.vlogo-anim__inner-l { animation: drop .85s cubic-bezier(.34,1.56,.64,1) both .4s; }
.vlogo-anim__inner-r { animation: drop .85s cubic-bezier(.34,1.56,.64,1) both .6s; }
.vlogo-anim__outer-r { animation: drop .85s cubic-bezier(.34,1.56,.64,1) both .8s; }
.vlogo-anim__horn-r  { animation: drop .85s cubic-bezier(.34,1.56,.64,1) both 1s, glint 7s ease-in-out 2.1s infinite; }
"""

# Converge the PyGAD parts in waves (rungs, strands, jaw, head), then run a soft
# ripple through the DNA rungs every few seconds, like pygad.com does with JS.
PYGAD_STYLE = """
.pm g { transform-box: fill-box; transform-origin: 50% 50%; }
@keyframes in-a { from { opacity: 0; transform: translate(-60px,-40px) rotate(-20deg) scale(.4); } 35% { opacity: 1; } to { opacity: 1; transform: none; } }
@keyframes in-b { from { opacity: 0; transform: translate(70px,30px) rotate(18deg) scale(.4); } 35% { opacity: 1; } to { opacity: 1; transform: none; } }
@keyframes in-c { from { opacity: 0; transform: translate(-30px,60px) rotate(14deg) scale(.4); } 35% { opacity: 1; } to { opacity: 1; transform: none; } }
@keyframes in-d { from { opacity: 0; transform: translate(40px,-60px) rotate(-16deg) scale(.4); } 35% { opacity: 1; } to { opacity: 1; transform: none; } }
@keyframes blink { 0%, 50% { transform: scaleY(.08); } 100% { transform: none; } }
@keyframes ripple { 0%, 88%, 100% { transform: none; } 92% { transform: scale(1.12); } 96% { transform: scale(.97); } }
.pm .helix-left  .rung-outer  { animation: in-a .9s cubic-bezier(.22,1,.36,1) .00s backwards, ripple 5.2s ease-in-out 2.2s infinite; }
.pm .helix-left  .rung-middle { animation: in-b .9s cubic-bezier(.22,1,.36,1) .05s backwards, ripple 5.2s ease-in-out 2.3s infinite; }
.pm .helix-left  .rung-inner  { animation: in-c .9s cubic-bezier(.22,1,.36,1) .10s backwards, ripple 5.2s ease-in-out 2.4s infinite; }
.pm .helix-right .rung-inner  { animation: in-d .9s cubic-bezier(.22,1,.36,1) .15s backwards, ripple 5.2s ease-in-out 2.4s infinite; }
.pm .helix-right .rung-middle { animation: in-a .9s cubic-bezier(.22,1,.36,1) .20s backwards, ripple 5.2s ease-in-out 2.3s infinite; }
.pm .helix-right .rung-outer  { animation: in-b .9s cubic-bezier(.22,1,.36,1) .25s backwards, ripple 5.2s ease-in-out 2.2s infinite; }
.pm .helix-left  .strand-upper { animation: in-c .9s cubic-bezier(.22,1,.36,1) .21s backwards; }
.pm .helix-left  .strand-lower { animation: in-d .9s cubic-bezier(.22,1,.36,1) .25s backwards; }
.pm .helix-right .strand-upper { animation: in-a .9s cubic-bezier(.22,1,.36,1) .29s backwards; }
.pm .helix-right .strand-lower { animation: in-b .9s cubic-bezier(.22,1,.36,1) .33s backwards; }
.pm .jaw      { animation: in-c .9s cubic-bezier(.22,1,.36,1) .42s backwards; }
.pm .crown    { animation: in-d .9s cubic-bezier(.22,1,.36,1) .63s backwards; }
.pm .snout    { animation: in-a .9s cubic-bezier(.22,1,.36,1) .67s backwards; }
.pm .nostrils { animation: in-b .9s cubic-bezier(.22,1,.36,1) .71s backwards; }
.pm .eye      { animation: blink 1.1s cubic-bezier(.34,1.56,.64,1) .84s backwards; }
"""


def vilvik(c):
    src = (TOOLS / "vilvik-mark.src.svg").read_text()
    mark = f'<g class="vm">{nested_mark(src, 52, 34, 162)}</g>'
    return card(
        c,
        label="Vilvik. Evolutionary optimization on the cloud, for your decisions, models, and games. No setup. vilvik.com",
        kicker="MY COMPANY",
        title="vilvik",
        title_color=c["blue"],
        lines=[
            "Evolutionary optimization on the cloud, for your decisions,",
            "models, and games. No setup.",
        ],
        link="vilvik.com",
        mark=mark,
        mark_style=VILVIK_STYLE,
    )


def pygad(c):
    src = (TOOLS / "pygad-mark.src.svg").read_text()
    mark = f'<g class="pm">{nested_mark(src, 36, 26, 190)}</g>'
    return card(
        c,
        label="PyGAD. Open-source Python library for genetic algorithms. Optimize anything and train Keras and PyTorch models. pygad.com",
        kicker="OPEN SOURCE",
        title="PyGAD",
        title_color=c["pygad"],
        lines=[
            "Open-source Python library for genetic algorithms.",
            "Optimize anything, and train Keras and PyTorch models.",
        ],
        link="pygad.com",
        mark=mark,
        mark_style=PYGAD_STYLE,
    )


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme, colors in THEMES.items():
        for name, build in (("header", header), ("vilvik", vilvik), ("pygad", pygad)):
            path = ASSETS / f"{name}-{theme}.svg"
            path.write_text(build(colors))
            print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
