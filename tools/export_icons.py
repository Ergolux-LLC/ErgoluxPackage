# Small helper to convert SVGs to PNGs at multiple sizes using cairosvg
import sys
from pathlib import Path

try:
    import cairosvg
except Exception as e:
    print('Missing cairosvg. Install with: pip install cairosvg')
    raise

SVG_DIR = Path(__file__).resolve().parent.parent / 'static' / 'icons'
OUT = SVG_DIR
SVG_FILES = ['valve.svg', 'alert-hexagon-off.svg']
SIZES = [192, 512]

OUT.mkdir(parents=True, exist_ok=True)

for svg in SVG_FILES:
    svg_path = SVG_DIR / svg
    if not svg_path.exists():
        print(f'Missing {svg_path}')
        continue
    stem = svg_path.stem
    for size in SIZES:
        out_path = OUT / f'{stem}-{size}.png'
        print(f'Exporting {svg_path} -> {out_path} at {size}px')
        cairosvg.svg2png(url=str(svg_path), write_to=str(out_path), output_width=size, output_height=size)

print('Done')
