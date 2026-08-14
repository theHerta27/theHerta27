from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "profile"
HEADER_SIZE = (1200, 280)
ABOUT_SIZE = (1200, 430)
ABOUT_MOBILE_SIZE = (720, 710)
MESSAGES = (
    "Hi there, I'm Tan Junlin 👋",
    "Building Backend & AI Systems",
    "让 AI 触手可及 · AI within reach",
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
        "background": "#F7F9FC",
        "border": "#CAD6E4",
        "rule": "#E2E8F0",
        "accent": "#3F7FB7",
        "secondary": "#62748A",
        "underline": "#8A78C2",
        "prompt": "#8A78C2",
        "key": "#587390",
        "text": "#24324A",
        "active": "#3D8F79",
    },
    "dark": {
        "background": "#0E131B",
        "border": "#2A3545",
        "rule": "#202938",
        "accent": "#7CC4F2",
        "secondary": "#91A0B5",
        "underline": "#B39DDB",
        "prompt": "#B39DDB",
        "key": "#8CB7D6",
        "text": "#DFE8F3",
        "active": "#74C9B1",
    },
}

WINDOW_LIGHTS = ((34, "#FF7B72"), (56, "#D29922"), (78, "#3FB950"))
SVG_MONO_FONT = "Cascadia Mono, SFMono-Regular, Consolas, Liberation Mono, monospace"
SVG_CJK_FONT = "Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


ASCII_FONT = font("CascadiaMono.ttf", 34)
CJK_FONT = font("msyh.ttc", 32)
EMOJI_FONT = font("seguiemj.ttf", 32)
SMALL_FONT = font("consola.ttf", 15)
PATH_FONT = font("consola.ttf", 16)
ABOUT_COMMAND_FONT = font("CascadiaMono.ttf", 24)
ABOUT_VALUE_FONT = font("CascadiaMono.ttf", 20)
ABOUT_IDENTITY_FONT = font("CascadiaMono.ttf", 22)
ABOUT_CJK_FONT = font("msyh.ttc", 21)
ABOUT_STATUS_FONT = font("consola.ttf", 15)


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
    x = (HEADER_SIZE[0] - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=text_font, fill=fill)


def base_frame(theme: dict[str, str]) -> Image.Image:
    image = Image.new("RGB", HEADER_SIZE, theme["background"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, 1198, 278), radius=14, fill=theme["background"], outline=theme["border"], width=2)
    for x, color in WINDOW_LIGHTS:
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
    start_x = (HEADER_SIZE[0] - text_width(draw, full_message)) / 2
    cursor_x = draw_mixed_text(draw, (start_x, TEXT_Y), visible_message, theme["accent"])
    if cursor_visible:
        draw.rounded_rectangle(
            (cursor_x + CURSOR_GAP, TEXT_Y + 1, cursor_x + CURSOR_GAP + 3, TEXT_Y + CURSOR_HEIGHT),
            radius=1,
            fill=theme["accent"],
        )
    return frame.convert("P", palette=Image.Palette.ADAPTIVE)


def render_header_gif(theme_name: str) -> None:
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


def svg_window_chrome(theme: dict[str, str], label: str, width: int, height: int) -> str:
    circles = "\n".join(
        f'  <circle cx="{x}" cy="30" r="6" fill="{color}"/>' for x, color in WINDOW_LIGHTS
    )
    return f"""  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
{circles}
  <text x="106" y="36" fill="{theme['secondary']}" font-family="{SVG_MONO_FONT}" font-size="16">{escape(label)}</text>
  <line x1="24" y1="58" x2="{width - 24}" y2="58" stroke="{theme['rule']}"/>"""


def render_header_svg(theme_name: str) -> None:
    theme = THEMES[theme_name]
    title = "Tan Junlin developer profile"
    description = "Hi there, I'm Tan Junlin. Backend and AI systems developer profile."
    content = f"""<svg width="{HEADER_SIZE[0]}" height="{HEADER_SIZE[1]}" viewBox="0 0 {HEADER_SIZE[0]} {HEADER_SIZE[1]}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
{svg_window_chrome(theme, 'theHerta27 / profile', HEADER_SIZE[0], HEADER_SIZE[1])}
  <text x="600" y="145" text-anchor="middle" fill="{theme['accent']}" font-family="{SVG_MONO_FONT}, {SVG_CJK_FONT}" font-size="34">{escape(MESSAGES[0])}</text>
  <line x1="404" y1="205" x2="796" y2="205" stroke="{theme['underline']}" stroke-width="3"/>
  <text x="600" y="242" text-anchor="middle" fill="{theme['secondary']}" font-family="{SVG_MONO_FONT}" font-size="15">XIDIAN UNIVERSITY  /  GRADUATE STUDENT  /  BUILDING PRACTICAL SOFTWARE</text>
</svg>
"""
    output = OUTPUT_DIR / f"header-{theme_name}.svg"
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"generated {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")


def profile_line(y: int, key: str, value: str, theme: dict[str, str], value_color: str | None = None) -> str:
    return (
        f'  <text x="42" y="{y}" fill="{theme["key"]}" font-family="{SVG_MONO_FONT}" font-size="20">{escape(key)}</text>\n'
        f'  <text x="166" y="{y}" fill="{theme["secondary"]}" font-family="{SVG_MONO_FONT}" font-size="20">:</text>\n'
        f'  <text x="190" y="{y}" fill="{value_color or theme["text"]}" font-family="{SVG_MONO_FONT}" font-size="20">{escape(value)}</text>'
    )


def render_about_svg(theme_name: str) -> None:
    theme = THEMES[theme_name]
    lines = (
        (247, "name", "Tan Junlin", None),
        (279, "education", "Master's Student @ Xidian University", None),
        (311, "focus", "Backend · AI/LLM Applications · Agent Systems", None),
        (343, "currently", "Building practical AI and backend systems", theme["active"]),
        (375, "exploring", "Go · Backend Systems · AI Engineering", None),
        (407, "interests", "Software Engineering · Open Source · AI Applications", None),
    )
    profile_lines = "\n".join(profile_line(y, key, value, theme, color) for y, key, value, color in lines)
    content = f"""<svg width="{ABOUT_SIZE[0]}" height="{ABOUT_SIZE[1]}" viewBox="0 0 {ABOUT_SIZE[0]} {ABOUT_SIZE[1]}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Tan Junlin profile terminal</title>
  <desc id="desc">Tan Junlin is a master's student at Xidian University focused on backend, AI/LLM applications, and agent systems.</desc>
{svg_window_chrome(theme, 'theHerta27 / identity', ABOUT_SIZE[0], ABOUT_SIZE[1])}
  <circle cx="1048" cy="30" r="5" fill="{theme['active']}"/>
  <text x="1062" y="36" fill="{theme['secondary']}" font-family="{SVG_MONO_FONT}" font-size="15">session active</text>
  <text x="42" y="105" font-family="{SVG_MONO_FONT}" font-size="24" font-weight="600"><tspan fill="{theme['prompt']}">$</tspan><tspan fill="{theme['accent']}"> whoami</tspan></text>
  <text x="42" y="148" font-family="{SVG_MONO_FONT}" font-size="22"><tspan fill="{theme['text']}">Tan Junlin</tspan><tspan fill="{theme['secondary']}"> | </tspan><tspan fill="{theme['underline']}" font-family="{SVG_CJK_FONT}" font-size="21">让 AI 触手可及</tspan><tspan fill="{theme['underline']}" font-family="{SVG_MONO_FONT}"> · AI within reach</tspan></text>
  <text x="42" y="207" font-family="{SVG_MONO_FONT}" font-size="24" font-weight="600"><tspan fill="{theme['prompt']}">$</tspan><tspan fill="{theme['accent']}"> cat .profile</tspan></text>
{profile_lines}
</svg>
"""
    output = OUTPUT_DIR / f"about-{theme_name}.svg"
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"generated {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")


def mobile_profile_line(
    y: int,
    key: str,
    values: tuple[str, ...],
    theme: dict[str, str],
    value_color: str | None = None,
) -> str:
    value_lines = "\n".join(
        f'  <text x="190" y="{y + index * 32}" fill="{value_color or theme["text"]}" font-family="{SVG_MONO_FONT}" font-size="22">{escape(value)}</text>'
        for index, value in enumerate(values)
    )
    return (
        f'  <text x="42" y="{y}" fill="{theme["key"]}" font-family="{SVG_MONO_FONT}" font-size="22">{escape(key)}</text>\n'
        f'  <text x="166" y="{y}" fill="{theme["secondary"]}" font-family="{SVG_MONO_FONT}" font-size="22">:</text>\n'
        f"{value_lines}"
    )


def render_about_mobile_svg(theme_name: str) -> None:
    theme = THEMES[theme_name]
    lines = (
        (286, "name", ("Tan Junlin",), None),
        (330, "education", ("Master's Student", "@ Xidian University"), None),
        (406, "focus", ("Backend · AI/LLM Applications", "· Agent Systems"), None),
        (482, "currently", ("Building practical AI and", "backend systems"), theme["active"]),
        (558, "exploring", ("Go · Backend Systems", "· AI Engineering"), None),
        (634, "interests", ("Software Engineering", "· Open Source · AI Applications"), None),
    )
    profile_lines = "\n".join(
        mobile_profile_line(y, key, values, theme, color) for y, key, values, color in lines
    )
    content = f"""<svg width="{ABOUT_MOBILE_SIZE[0]}" height="{ABOUT_MOBILE_SIZE[1]}" viewBox="0 0 {ABOUT_MOBILE_SIZE[0]} {ABOUT_MOBILE_SIZE[1]}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Tan Junlin mobile profile terminal</title>
  <desc id="desc">Tan Junlin is a master's student at Xidian University focused on backend, AI/LLM applications, and agent systems.</desc>
{svg_window_chrome(theme, 'theHerta27 / identity', ABOUT_MOBILE_SIZE[0], ABOUT_MOBILE_SIZE[1])}
  <circle cx="568" cy="30" r="5" fill="{theme['active']}"/>
  <text x="582" y="36" fill="{theme['secondary']}" font-family="{SVG_MONO_FONT}" font-size="15">session active</text>
  <text x="42" y="105" font-family="{SVG_MONO_FONT}" font-size="26" font-weight="600"><tspan fill="{theme['prompt']}">$</tspan><tspan fill="{theme['accent']}"> whoami</tspan></text>
  <text x="42" y="151" font-family="{SVG_MONO_FONT}" font-size="23"><tspan fill="{theme['text']}">Tan Junlin</tspan><tspan fill="{theme['secondary']}"> | </tspan><tspan fill="{theme['underline']}" font-family="{SVG_CJK_FONT}" font-size="22">让 AI 触手可及</tspan></text>
  <text x="42" y="187" fill="{theme['underline']}" font-family="{SVG_MONO_FONT}" font-size="23">· AI within reach</text>
  <text x="42" y="245" font-family="{SVG_MONO_FONT}" font-size="26" font-weight="600"><tspan fill="{theme['prompt']}">$</tspan><tspan fill="{theme['accent']}"> cat .profile</tspan></text>
{profile_lines}
</svg>
"""
    output = OUTPUT_DIR / f"about-mobile-{theme_name}.svg"
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"generated {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")


def draw_window_chrome(draw: ImageDraw.ImageDraw, theme: dict[str, str], label: str, size: tuple[int, int]) -> None:
    width, height = size
    draw.rounded_rectangle(
        (1, 1, width - 2, height - 2),
        radius=14,
        fill=theme["background"],
        outline=theme["border"],
        width=2,
    )
    for x, color in WINDOW_LIGHTS:
        draw.ellipse((x - 6, 24, x + 6, 36), fill=color)
    draw.text((106, 19), label, font=PATH_FONT, fill=theme["secondary"])
    draw.line((24, 58, width - 24, 58), fill=theme["rule"], width=1)


def about_preview_image(theme_name: str) -> Image.Image:
    theme = THEMES[theme_name]
    image = Image.new("RGB", ABOUT_SIZE, theme["background"])
    draw = ImageDraw.Draw(image)
    draw_window_chrome(draw, theme, "theHerta27 / identity", ABOUT_SIZE)
    draw.ellipse((1043, 25, 1053, 35), fill=theme["active"])
    draw.text((1062, 19), "session active", font=ABOUT_STATUS_FONT, fill=theme["secondary"])

    draw.text((42, 78), "$", font=ABOUT_COMMAND_FONT, fill=theme["prompt"])
    draw.text((59, 78), " whoami", font=ABOUT_COMMAND_FONT, fill=theme["accent"])
    draw.text((42, 119), "Tan Junlin", font=ABOUT_IDENTITY_FONT, fill=theme["text"])
    identity_x = 42 + draw.textlength("Tan Junlin", font=ABOUT_IDENTITY_FONT)
    draw.text((identity_x, 119), " | ", font=ABOUT_IDENTITY_FONT, fill=theme["secondary"])
    identity_x += draw.textlength(" | ", font=ABOUT_IDENTITY_FONT)
    draw.text((identity_x, 119), "让 AI 触手可及", font=ABOUT_CJK_FONT, fill=theme["underline"])
    identity_x += draw.textlength("让 AI 触手可及", font=ABOUT_CJK_FONT)
    draw.text((identity_x, 119), " · AI within reach", font=ABOUT_IDENTITY_FONT, fill=theme["underline"])

    draw.text((42, 180), "$", font=ABOUT_COMMAND_FONT, fill=theme["prompt"])
    draw.text((59, 180), " cat .profile", font=ABOUT_COMMAND_FONT, fill=theme["accent"])
    preview_lines = (
        (222, "name", "Tan Junlin", None),
        (254, "education", "Master's Student @ Xidian University", None),
        (286, "focus", "Backend · AI/LLM Applications · Agent Systems", None),
        (318, "currently", "Building practical AI and backend systems", theme["active"]),
        (350, "exploring", "Go · Backend Systems · AI Engineering", None),
        (382, "interests", "Software Engineering · Open Source · AI Applications", None),
    )
    for y, key, value, value_color in preview_lines:
        draw.text((42, y), key, font=ABOUT_VALUE_FONT, fill=theme["key"])
        draw.text((166, y), ":", font=ABOUT_VALUE_FONT, fill=theme["secondary"])
        draw.text((190, y), value, font=ABOUT_VALUE_FONT, fill=value_color or theme["text"])
    return image


def about_mobile_preview_image(theme_name: str) -> Image.Image:
    theme = THEMES[theme_name]
    image = Image.new("RGB", ABOUT_MOBILE_SIZE, theme["background"])
    draw = ImageDraw.Draw(image)
    draw_window_chrome(draw, theme, "theHerta27 / identity", ABOUT_MOBILE_SIZE)
    draw.ellipse((563, 25, 573, 35), fill=theme["active"])
    draw.text((582, 19), "session active", font=ABOUT_STATUS_FONT, fill=theme["secondary"])

    draw.text((42, 76), "$", font=ABOUT_COMMAND_FONT, fill=theme["prompt"])
    draw.text((61, 76), " whoami", font=ABOUT_COMMAND_FONT, fill=theme["accent"])
    draw.text((42, 121), "Tan Junlin", font=ABOUT_IDENTITY_FONT, fill=theme["text"])
    identity_x = 42 + draw.textlength("Tan Junlin", font=ABOUT_IDENTITY_FONT)
    draw.text((identity_x, 121), " | ", font=ABOUT_IDENTITY_FONT, fill=theme["secondary"])
    identity_x += draw.textlength(" | ", font=ABOUT_IDENTITY_FONT)
    draw.text((identity_x, 121), "让 AI 触手可及", font=ABOUT_CJK_FONT, fill=theme["underline"])
    draw.text((42, 157), "· AI within reach", font=ABOUT_IDENTITY_FONT, fill=theme["underline"])

    draw.text((42, 216), "$", font=ABOUT_COMMAND_FONT, fill=theme["prompt"])
    draw.text((61, 216), " cat .profile", font=ABOUT_COMMAND_FONT, fill=theme["accent"])
    preview_lines = (
        (259, "name", ("Tan Junlin",), None),
        (303, "education", ("Master's Student", "@ Xidian University"), None),
        (379, "focus", ("Backend · AI/LLM Applications", "· Agent Systems"), None),
        (455, "currently", ("Building practical AI and", "backend systems"), theme["active"]),
        (531, "exploring", ("Go · Backend Systems", "· AI Engineering"), None),
        (607, "interests", ("Software Engineering", "· Open Source · AI Applications"), None),
    )
    for y, key, values, value_color in preview_lines:
        draw.text((42, y), key, font=ABOUT_IDENTITY_FONT, fill=theme["key"])
        draw.text((166, y), ":", font=ABOUT_IDENTITY_FONT, fill=theme["secondary"])
        for index, value in enumerate(values):
            draw.text(
                (190, y + index * 32),
                value,
                font=ABOUT_IDENTITY_FONT,
                fill=value_color or theme["text"],
            )
    return image


def render_preview(output: Path) -> None:
    gutter = 20
    preview = Image.new(
        "RGB",
        (
            HEADER_SIZE[0] * 2 + gutter,
            HEADER_SIZE[1] + ABOUT_SIZE[1] + ABOUT_MOBILE_SIZE[1] + gutter * 2,
        ),
        "#D5DEE9",
    )
    for column, theme_name in enumerate(("light", "dark")):
        x = column * (HEADER_SIZE[0] + gutter)
        theme = THEMES[theme_name]
        header = message_frame(base_frame(theme), theme, MESSAGES[2], MESSAGES[2], True).convert("RGB")
        preview.paste(header, (x, 0))
        preview.paste(about_preview_image(theme_name), (x, HEADER_SIZE[1] + gutter))
        mobile_x = x + (HEADER_SIZE[0] - ABOUT_MOBILE_SIZE[0]) // 2
        mobile_y = HEADER_SIZE[1] + ABOUT_SIZE[1] + gutter * 2
        preview.paste(about_mobile_preview_image(theme_name), (mobile_x, mobile_y))
    output.parent.mkdir(parents=True, exist_ok=True)
    preview.save(output, optimize=True)
    print(f"generated preview {output} ({output.stat().st_size} bytes)")


def render(theme_name: str) -> None:
    render_header_gif(theme_name)
    render_header_svg(theme_name)
    render_about_svg(theme_name)
    render_about_mobile_svg(theme_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic GitHub Profile visual assets.")
    parser.add_argument("--preview", type=Path, help="Optional Light/Dark PNG preview output path.")
    args = parser.parse_args()
    render("light")
    render("dark")
    if args.preview:
        render_preview(args.preview)


if __name__ == "__main__":
    main()
