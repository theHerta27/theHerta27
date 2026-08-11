from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "profile"
SIZE = (1200, 280)
MESSAGES = (
    "Hi there, I'm Tan Junlin 👋",
    "Building Backend & AI Systems",
    "把想法做成系统 · Turn Ideas into Systems",
)

TYPE_MS = 70
DELETE_MS = 40
HOLD_FRAME_MS = 400
GAP_MS = 300
TEXT_Y = 116
CURSOR_HEIGHT = 38
CURSOR_GAP = 5


THEMES = {
    "light": {
        "background": "#F6F8FA",
        "border": "#D0D7DE",
        "rule": "#D8DEE4",
        "accent": "#0969DA",
        "secondary": "#57606A",
        "underline": "#8250DF",
    },
    "dark": {
        "background": "#0D1117",
        "border": "#30363D",
        "rule": "#21262D",
        "accent": "#58A6FF",
        "secondary": "#8B949E",
        "underline": "#A371F7",
    },
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


ASCII_FONT = font("CascadiaMono.ttf", 34)
CJK_FONT = font("msyh.ttc", 32)
EMOJI_FONT = font("seguiemj.ttf", 32)
SMALL_FONT = font("consola.ttf", 15)
PATH_FONT = font("consola.ttf", 16)


def character_font(character: str) -> ImageFont.FreeTypeFont:
    codepoint = ord(character)
    if codepoint >= 0x1F000:
        return EMOJI_FONT
    if 0x3400 <= codepoint <= 0x9FFF:
        return CJK_FONT
    return ASCII_FONT


def character_width(draw: ImageDraw.ImageDraw, character: str) -> float:
    return draw.textlength(character, font=character_font(character))


def text_width(draw: ImageDraw.ImageDraw, text: str) -> float:
    return sum(character_width(draw, character) for character in text)


def draw_mixed_text(draw: ImageDraw.ImageDraw, position: tuple[float, int], text: str, fill: str) -> float:
    x, y = position
    for character in text:
        selected_font = character_font(character)
        draw.text(
            (x, y),
            character,
            font=selected_font,
            fill=fill,
            embedded_color=selected_font is EMOJI_FONT,
        )
        x += character_width(draw, character)
    return x


def centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, text_font: ImageFont.FreeTypeFont, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=text_font)
    x = (SIZE[0] - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=text_font, fill=fill)


def base_frame(theme: dict[str, str]) -> Image.Image:
    image = Image.new("RGB", SIZE, theme["background"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, 1198, 278), radius=14, fill=theme["background"], outline=theme["border"], width=2)
    for x, color in ((34, "#FF7B72"), (56, "#D29922"), (78, "#3FB950")):
        draw.ellipse((x - 6, 24, x + 6, 36), fill=color)
    draw.text((106, 19), "theHerta27 / profile", font=PATH_FONT, fill=theme["secondary"])
    draw.line((24, 58, 1176, 58), fill=theme["rule"], width=1)
    draw.line((404, 205, 796, 205), fill=theme["underline"], width=3)
    centered_text(draw, 225, "XIDIAN UNIVERSITY  /  GRADUATE STUDENT  /  BUILDING PRACTICAL SOFTWARE", SMALL_FONT, theme["secondary"])
    return image


def message_frame(
    background: Image.Image,
    theme: dict[str, str],
    full_message: str,
    visible_message: str,
    cursor_visible: bool,
) -> Image.Image:
    frame = background.copy().convert("RGBA")
    draw = ImageDraw.Draw(frame)
    start_x = (SIZE[0] - text_width(draw, full_message)) / 2
    cursor_x = draw_mixed_text(draw, (start_x, TEXT_Y), visible_message, theme["accent"])
    if cursor_visible:
        draw.rounded_rectangle(
            (cursor_x + CURSOR_GAP, TEXT_Y + 1, cursor_x + CURSOR_GAP + 3, TEXT_Y + CURSOR_HEIGHT),
            radius=1,
            fill=theme["accent"],
        )
    return frame.convert("P", palette=Image.Palette.ADAPTIVE)


def render(theme_name: str) -> None:
    theme = THEMES[theme_name]
    background = base_frame(theme)
    frames: list[Image.Image] = []
    durations: list[int] = []

    for message in MESSAGES:
        for visible_count in range(1, len(message) + 1):
            frames.append(message_frame(background, theme, message, message[:visible_count], True))
            durations.append(TYPE_MS)

        for cursor_visible in (False, True, False):
            frames.append(message_frame(background, theme, message, message, cursor_visible))
            durations.append(HOLD_FRAME_MS)

        for visible_count in range(len(message) - 1, -1, -1):
            frames.append(message_frame(background, theme, message, message[:visible_count], True))
            durations.append(DELETE_MS)

        frames.append(message_frame(background, theme, message, "", False))
        durations.append(GAP_MS)

    output = OUTPUT_DIR / f"header-{theme_name}.gif"
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
        comment="\n".join(MESSAGES).encode("utf-8"),
    )
    print(
        f"generated {output.relative_to(ROOT)} "
        f"({output.stat().st_size} bytes, {len(frames)} frames, {sum(durations)} ms)"
    )


if __name__ == "__main__":
    render("light")
    render("dark")
