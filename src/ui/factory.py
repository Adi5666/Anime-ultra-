\
from discord import Embed, Colour
from ..config.settings import BRAND_BANNER, BRAND_THUMB

COLORS = {
  "info": Colour.blue(),
  "warn": Colour.orange(),
  "danger": Colour.red(),
  "success": Colour.green(),
  "gold": Colour.gold(),
  "purple": Colour.purple()
}

def theme_embed(title: str, desc: str, style: str="info") -> Embed:
    emb = Embed(title=title, description=desc, colour=COLORS.get(style, Colour.blurple()))
    try:
        if BRAND_BANNER:
            emb.set_image(url=BRAND_BANNER)
        if BRAND_THUMB:
            emb.set_thumbnail(url=BRAND_THUMB)
    except Exception:
        pass
    emb.set_footer(text="Anime Ultra — Catch. Evolve. Ascend.")
    return emb
