"""Capturas de un deck en su estado final (todos los pasos visibles), para revisar el diseño.

Uso: python3 capturas.py deck.html salida_dir [ancho alto] [n1 n2 …]
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

deck = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
w, h = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1600, 900)
solo = [int(x) for x in sys.argv[5:]]
FINAL = ".slide [data-step]{opacity:1!important;transform:none!important;clip-path:none!important} *{transition:none!important}"


async def main() -> None:
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": w, "height": h})
        await pg.goto(deck.as_uri())
        n = await pg.evaluate("document.querySelectorAll('.slide').length")
        for k in (solo or range(1, n + 1)):
            await pg.goto(deck.as_uri() + f"#{k}")
            await pg.reload()
            await pg.add_style_tag(content=FINAL)
            await pg.wait_for_timeout(150)
            await pg.screenshot(path=str(out / f"{deck.stem}-{k:02d}.png"))
        await b.close()
        print(n, "slides")


asyncio.run(main())
