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
  <text class="t2" x="58" y="156" font-size="22" fill="{c['muted']}">Senior AI engineer and researcher</text>
  <text class="t3" x="58" y="200" font-size="22" fill="{c['text']}">Founder of <tspan font-weight="700" fill="{c['blue']}">Vilvik</tspan>  ·  Creator of <tspan font-weight="700" fill="{c['pygad']}">PyGAD</tspan></text>
  <text class="t4" x="58" y="244" font-size="17" fill="{c['muted']}">Evolutionary algorithms, deep learning, and the tools that make them easy to use.</text>
</g>
<g>
  {contours}
  {''.join(dots)}
  <path class="star" d="M{ox} {oy - 11} L{ox + 3.2} {oy - 3.4} L{ox + 11} {oy - 3.4} L{ox + 4.8} {oy + 1.6} L{ox + 7} {oy + 9.5} L{ox} {oy + 4.7} L{ox - 7} {oy + 9.5} L{ox - 4.8} {oy + 1.6} L{ox - 11} {oy - 3.4} L{ox - 3.2} {oy - 3.4} Z" fill="{c['amber']}"/>
  {gen_svg}
</g>"""
    return svg_doc(w, h, "Ahmed Gad. Senior AI engineer and researcher. Founder of Vilvik, creator of PyGAD.", style, body)


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


# ------------------------------------------------------- looping motion ---
#
# GitHub shows README images with <img>, so the logos can't run the JavaScript
# that animates them on vilvik.com and pygad.com. Instead each moving part gets
# one CSS keyframe track covering a whole loop. A track is built from
# "segments" (an animation that starts at a given time), with the part resting
# in place between them. Each loop ends in the same state it starts in, so the
# repeat is seamless.

OUT = "cubic-bezier(.22,1,.36,1)"
IN_OUT = "cubic-bezier(.65,0,.35,1)"
SPRING = "cubic-bezier(.34,1.56,.64,1)"
EXIT = "cubic-bezier(.55,0,.75,.2)"
REST = {"transform": "none", "opacity": "1"}


def track(name, selector, total_ms, segments, first=None):
    """CSS for one part: `segments` is a list of (start_ms, duration_ms, easing, frames),
    where frames are (offset 0..1, {property: value}). `first` is the state at t=0."""
    points = [(0.0, dict(first or REST), "linear")]
    for start, duration, easing, frames in sorted(segments, key=lambda s: s[0]):
        for offset, props in frames:
            points.append((start + offset * duration, props, easing))
    points.append((float(total_ms), dict(points[-1][1]), "linear"))
    merged = {}
    for at, props, easing in points:
        pct = round(at / total_ms * 100, 3)
        slot = merged.setdefault(pct, [{}, easing])
        slot[0].update(props)
        slot[1] = easing
    rules = []
    for pct, (props, easing) in merged.items():
        body = " ".join(f"{k}: {v};" for k, v in props.items())
        rules.append(f"{pct}% {{ {body} animation-timing-function: {easing}; }}")
    return (
        f"@keyframes {name} {{ {' '.join(rules)} }}\n"
        f"{selector} {{ animation: {name} {total_ms}ms linear infinite; }}"
    )


def vilvik_style():
    """The vilvik.com cascade build: the six parts drop in one after another, the
    horns lift once, then everything falls away and the build starts again."""
    total = 8000
    hidden = {"transform": "translateY(-220%) scale(.75)", "opacity": "0"}
    drop = [
        (0, hidden),
        (.6, {"transform": "translateY(8%) scale(1.04)", "opacity": "1"}),
        (.8, {"transform": "translateY(-3%) scale(.98)"}),
        (1, REST),
    ]
    glint = [
        (0, REST),
        (.4, {"transform": "translateY(-9%) scale(1.06)"}),
        (.7, {"transform": "translateY(2%) scale(.99)"}),
        (1, REST),
    ]
    leave = [(0, REST), (1, {"transform": "translateY(120%) scale(.7)", "opacity": "0"})]
    parts = ["horn-l", "outer-l", "inner-l", "inner-r", "outer-r", "horn-r"]
    css = ['.vm [class^="vlogo-anim__"] { transform-box: fill-box; transform-origin: center; }']
    for i, part in enumerate(parts):
        segments = [(i * 200, 850, SPRING, drop), (6600 + i * 100, 700, EXIT, leave)]
        if part.startswith("horn"):
            segments.append((4200 + (100 if part == "horn-r" else 0), 700, "ease-in-out", glint))
        css.append(track(f"v-{part}", f".vm .vlogo-anim__{part}", total, segments, first=hidden))
    return "\n".join(css)


def seeded(seed):
    """Port of the seeded generator in pygad-site/logo-motion.js, so the parts
    scatter to the same places as on pygad.com."""
    state = seed

    def imul(a, b):
        return ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF

    def rand():
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(state ^ (state >> 15), 1 | state)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rand


def pygad_style():
    """The pygad.com mark motion (converge, ripple, blink and strike from
    logo-motion.js) laid out on one 16 s loop that ends by scattering the
    parts back out to where the next loop gathers them from."""
    total = 16000
    rand = seeded(7)
    waves = [
        [".helix-left .rung-outer", ".helix-left .rung-middle", ".helix-left .rung-inner",
         ".helix-right .rung-outer", ".helix-right .rung-middle", ".helix-right .rung-inner"],
        [".helix-left .strand-lower", ".helix-left .strand-upper",
         ".helix-right .strand-lower", ".helix-right .strand-upper"],
        [".jaw"],
        [".crown", ".snout", ".nostrils"],
    ]
    segments, first = {}, {}

    def add(selector, *segment):
        segments.setdefault(selector, []).append(segment)

    # Converge in, and the reverse at the end of the loop (head first).
    for w, wave in enumerate(waves):
        for i, sel in enumerate(wave):
            dx, dy, turn = (rand() - .5) * 260, (rand() - .5) * 200, (rand() - .5) * 70
            away = {"transform": f"translate({dx:.1f}px, {dy:.1f}px) rotate({turn:.1f}deg) scale(.4)", "opacity": "0"}
            first[sel] = away
            add(sel, w * 210 + i * 40, 900, OUT, [(0, away), (.35, {"opacity": "1"}), (1, REST)])
            add(sel, 14450 + (3 - w) * 150 + i * 30, 700, EXIT, [(0, REST), (.4, {"opacity": "1"}), (1, away)])

    eye_shut = {"transform": "scaleY(.08)", "opacity": "0"}
    for eye in (".eye-left", ".eye-right"):
        first[eye] = eye_shut
        add(eye, 840, 1100, SPRING, [(0, eye_shut), (.25, {"transform": "scaleY(.08)", "opacity": "1"}),
                                     (.5, {"transform": "scaleY(.08)"}), (1, REST)])
        # The second ripple of each loop ends with a blink, as on the site.
        add(eye, 9700 + 1500, 220, IN_OUT, [(0, REST), (.5, {"transform": "scaleY(.1)"}), (1, REST)])
        add(eye, 14300, 300, EXIT, [(0, REST), (1, eye_shut)])

    # Ripple through the DNA rungs, inner to outer, while the strands breathe out.
    for start in (4540, 9700):
        for step, ring in enumerate(("rung-inner", "rung-middle", "rung-outer")):
            for side in ("helix-left", "helix-right"):
                add(f".{side} .{ring}", start + step * 140, 900, IN_OUT, [
                    (0, REST), (.4, {"transform": "scaleY(.62)", "opacity": ".55"}),
                    (.75, {"transform": "scaleY(1.04)", "opacity": "1"}), (1, REST)])
        for side, push in (("helix-left", -7), ("helix-right", 7)):
            add(f".{side}", start + 260, 1100, IN_OUT, [
                (0, REST), (.45, {"transform": f"translateX({push}px)"}), (1, REST)])

    # The strike (a hover effect on pygad.com, played once per loop here).
    strike = 12500
    add(".face", strike, 760, IN_OUT, [
        (0, REST), (.28, {"transform": "translateY(8px) scale(.95)"}),
        (.5, {"transform": "translateY(-6px) scale(1.1)"}), (1, REST)])
    add(".jaw", strike, 760, IN_OUT, [
        (0, REST), (.3, REST), (.52, {"transform": "translateY(14px) scaleY(1.08)"}), (1, REST)])
    for eye in (".eye-left", ".eye-right"):
        add(f"{eye} .pupil", strike, 760, IN_OUT, [
            (0, REST), (.3, {"transform": "scaleX(.5)"}), (.6, {"transform": "scaleX(.5)"}), (1, REST)])
    for side, pull in (("helix-left", 20), ("helix-right", -20)):
        add(f".{side}", strike + 120, 900, OUT, [
            (0, REST), (.45, {"transform": f"translateX({pull}px) scaleX(.9)"}),
            (.75, {"transform": f"translateX({-pull * .25:.0f}px) scaleX(1.02)"}), (1, REST)])

    css = [
        ".pm g { transform-box: fill-box; transform-origin: 50% 50%; }",
        ".pm .helix-left { transform-origin: 100% 50%; }",
        ".pm .helix-right { transform-origin: 0 50%; }",
        ".pm .jaw { transform-origin: 50% 0; }",
        ".pm .face { transform-origin: 50% 70%; }",
    ]
    for n, (sel, segs) in enumerate(segments.items()):
        css.append(track(f"pg{n}", f".pm {sel}", total, segs, first=first.get(sel)))
    return "\n".join(css)


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
        mark_style=vilvik_style(),
    )


def pygad(c):
    src = (TOOLS / "pygad-mark.src.svg").read_text()
    mark = f'<g class="pm">{nested_mark(src, 26, 10, 212)}</g>'
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
        mark_style=pygad_style(),
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
