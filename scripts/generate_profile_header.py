from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "profile"
HEADER_SIZE = (1200, 220)
HEADER_MOBILE_SIZE = (720, 270)
ABOUT_SIZE = (1200, 350)
ABOUT_MOBILE_SIZE = (720, 440)
FOOTER_SIZE = (1200, 200)
MESSAGES = (
    "Hi there, I'm Tan Junlin 👋",
    "技术改变生活 · Code Changes Life",
    "Keep Building, Keep Growing ✨",
)
NAME = "Tan Junlin"
PROFILE_FIELDS = (
    ("education", "西安电子科技大学 · 硕士在读"),
    ("focus", "AI 应用开发 · Agent 工程实践"),
    ("languages", "Python · Go"),
)
PROFILE_DESCRIPTION = NAME + "；" + "；".join(value for _, value in PROFILE_FIELDS)
FOOTER_TITLE = "Keep Coding 🚀"
FOOTER_SUBTITLE = "技术改变生活"

TYPE_MS = 70
DELETE_MS = 40
HOLD_FRAME_MS = 500
GAP_MS = 300
TEXT_Y = 95
CURSOR_HEIGHT = 56
CURSOR_GAP = 5


THEMES = {
    "light": {
        "background": "#F7F9FC",
        "border": "#CAD6E4",
        "rule": "#E2E8F0",
        "accent": "#3F7FB7",
        "headline": "#00CFF1",
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
        "headline": "#00CFF1",
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


ASCII_FONT = font("CascadiaMono.ttf", 52)
ASCII_FONT.set_variation_by_axes([700])
CJK_FONT = font("msyhbd.ttc", 50)
EMOJI_FONT = font("seguiemj.ttf", 48)
PATH_FONT = font("consola.ttf", 16)


def character_font(character: str) -> ImageFont.FreeTypeFont:
    codepoint = ord(character)
    if codepoint >= 0x1F000 or 0x2600 <= codepoint <= 0x27BF:
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


def base_frame(theme: dict[str, str], mobile: bool = False) -> Image.Image:
    width, height = HEADER_MOBILE_SIZE if mobile else HEADER_SIZE
    image = Image.new("RGB", (width, height), theme["background"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=14, fill=theme["background"], outline=theme["border"], width=2)
    for x, color in WINDOW_LIGHTS:
        draw.ellipse((x - 6, 24, x + 6, 36), fill=color)
    draw.text((106, 19), "theHerta27 / profile", font=PATH_FONT, fill=theme["secondary"])
    draw.line((24, 58, width - 24, 58), fill=theme["rule"], width=1)
    draw.line((width / 2 - 140, height - 28, width / 2 + 140, height - 28), fill=theme["underline"], width=3)
    return image


def message_lines(message: str, mobile: bool) -> list[str]:
    if not mobile:
        return [message]
    # Break at semantic boundaries; every character still comes from MESSAGES.
    marker = "I'm " if "I'm " in message else " · " if " · " in message else ", "
    split = message.index(marker) + len(marker)
    return [message[:split], message[split:]]


def message_frame(
    background: Image.Image,
    theme: dict[str, str],
    full_message: str,
    visible_message: str,
    cursor_visible: bool,
) -> Image.Image:
    frame = background.copy().convert("RGBA")
    draw = ImageDraw.Draw(frame)
    mobile = background.size == HEADER_MOBILE_SIZE
    consumed = 0
    cursor_x, cursor_y = 0.0, TEXT_Y
    for index, line in enumerate(message_lines(full_message, mobile)):
        start_x = (background.width - text_width(draw, line)) / 2
        if start_x < 24:
            raise ValueError(f"Header text overflows: {line}")
        y = (85 + index * 72) if mobile else TEXT_Y
        count = max(0, min(len(line), len(visible_message) - consumed))
        end_x = draw_mixed_text(draw, (start_x, y), line[:count], theme["headline"])
        if len(visible_message) >= consumed:
            cursor_x, cursor_y = end_x, y
        consumed += len(line)
    if cursor_visible:
        draw.rounded_rectangle(
            (cursor_x + CURSOR_GAP, cursor_y + 5, cursor_x + CURSOR_GAP + 5, cursor_y + CURSOR_HEIGHT),
            radius=1,
            fill=theme["headline"],
        )
    return frame.convert("P", palette=Image.Palette.ADAPTIVE)


def render_header_gif(theme_name: str, mobile: bool = False) -> None:
    theme = THEMES[theme_name]
    background = base_frame(theme, mobile)
    frames: list[Image.Image] = []
    durations: list[int] = []

    for index, message in enumerate(MESSAGES):
        # Start with the complete greeting, including for clients showing frame 0 only.
        for cursor_visible in (False, True, False, True, False):
            frames.append(message_frame(background, theme, message, message, cursor_visible))
            durations.append(HOLD_FRAME_MS)

        for visible_count in range(len(message) - 1, -1, -1):
            frames.append(message_frame(background, theme, message, message[:visible_count], True))
            durations.append(DELETE_MS)

        frames.append(message_frame(background, theme, message, "", False))
        durations.append(GAP_MS)

        next_message = MESSAGES[(index + 1) % len(MESSAGES)]
        for visible_count in range(1, len(next_message) + 1):
            frames.append(message_frame(background, theme, next_message, next_message[:visible_count], True))
            durations.append(TYPE_MS)

    suffix = f"mobile-{theme_name}" if mobile else theme_name
    output = OUTPUT_DIR / f"header-{suffix}.gif"
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


def render_header_svg(theme_name: str, mobile: bool = False) -> None:
    theme = THEMES[theme_name]
    title = "Tan Junlin developer profile"
    description = " / ".join(MESSAGES)
    width, height = (720, 370) if mobile else HEADER_SIZE
    lines = []
    y = 102
    for index, message in enumerate(MESSAGES):
        for line in message_lines(message, mobile):
            size = (42 if mobile else 48) if index == 0 else (32 if mobile else 30)
            color = theme['headline'] if index == 0 else theme['text']
            lines.append(f'  <text x="{width / 2}" y="{y}" text-anchor="middle" fill="{color}" font-family="{SVG_MONO_FONT}, {SVG_CJK_FONT}" font-size="{size}" font-weight="700">{escape(line)}</text>')
            y += 44 if mobile else 46
    text_elements = "\n".join(lines)
    content = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
{svg_window_chrome(theme, 'theHerta27 / profile', width, height)}
{text_elements}
</svg>
"""
    suffix = f"mobile-{theme_name}" if mobile else theme_name
    output = OUTPUT_DIR / f"header-{suffix}.svg"
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"generated {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")


def about_layout(mobile: bool = False) -> list[tuple[int, int, str, str, int]]:
    """Shared text and coordinates for SVG output and Pillow previews."""
    layout = [
        (42, 105, "$ whoami", "accent", 26),
        (42, 147, NAME, "text", 26),
        (42, 207, "$ cat .profile", "accent", 26),
    ]
    for index, (key, value) in enumerate(PROFILE_FIELDS):
        y = 250 + index * (64 if mobile else 36)
        layout.extend([
            (42, y, key, "key", 24),
            (192, y, ":", "secondary", 24),
            (218, y, value, "text", 24),
        ])
    return layout


def render_about_svg(theme_name: str, mobile: bool = False) -> None:
    theme = THEMES[theme_name]
    width, height = ABOUT_MOBILE_SIZE if mobile else ABOUT_SIZE
    lines = "\n".join(
        f'  <text x="{x}" y="{y}" fill="{theme[color]}" font-family="{SVG_MONO_FONT}, {SVG_CJK_FONT}" font-size="{size}">{escape(value)}</text>'
        for x, y, value, color, size in about_layout(mobile)
    )
    content = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{NAME} · About</title>
  <desc id="desc">{escape(PROFILE_DESCRIPTION)}</desc>
{svg_window_chrome(theme, 'theHerta27 / identity', width, height)}
{lines}
</svg>
"""
    suffix = f"mobile-{theme_name}" if mobile else theme_name
    output = OUTPUT_DIR / f"about-{suffix}.svg"
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


def about_preview_image(theme_name: str, mobile: bool = False) -> Image.Image:
    theme = THEMES[theme_name]
    size = ABOUT_MOBILE_SIZE if mobile else ABOUT_SIZE
    image = Image.new("RGB", size, theme["background"])
    draw = ImageDraw.Draw(image)
    draw_window_chrome(draw, theme, "theHerta27 / identity", size)
    for x, y, value, color, font_size in about_layout(mobile):
        for character in value:
            glyph_font = font("msyh.ttc" if 0x3400 <= ord(character) <= 0x9FFF else "CascadiaMono.ttf", font_size)
            draw.text((x, y), character, font=glyph_font, fill=theme[color], anchor="ls")
            x += draw.textlength(character, font=glyph_font)
        if x > size[0] - 24:
            raise ValueError(f"About text overflows: {value}")
    return image


def render_footer_svg(theme_name: str) -> None:
    theme = THEMES[theme_name]
    width, height = FOOTER_SIZE
    content = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{escape(FOOTER_TITLE)}</title>
  <desc id="desc">{FOOTER_SUBTITLE}</desc>
  <path d="M0 40 C200 0 360 80 600 40 S1000 0 1200 40 V200 H0 Z" fill="{theme['underline']}" opacity=".16"/>
  <path d="M0 55 C200 20 370 88 600 55 S1000 20 1200 55 V200 H0 Z" fill="{theme['background']}"/>
  <path d="M0 55 C200 20 370 88 600 55 S1000 20 1200 55" stroke="{theme['accent']}" opacity=".45"/>
  <text x="600" y="122" text-anchor="middle" fill="{theme['accent']}" font-family="{SVG_MONO_FONT}, Segoe UI Emoji, sans-serif" font-size="40" font-weight="600">{escape(FOOTER_TITLE)}</text>
  <text x="600" y="166" text-anchor="middle" fill="{theme['secondary']}" font-family="{SVG_CJK_FONT}" font-size="30">{FOOTER_SUBTITLE}</text>
</svg>
"""
    output = OUTPUT_DIR / f"footer-{theme_name}.svg"
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"generated {output.relative_to(ROOT)} ({output.stat().st_size} bytes)")


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
        preview.paste(about_preview_image(theme_name, mobile=True), (mobile_x, mobile_y))
    output.parent.mkdir(parents=True, exist_ok=True)
    preview.save(output, optimize=True)
    print(f"generated preview {output} ({output.stat().st_size} bytes)")


def render_badges() -> None:
    for name, label, value, color, width, split in (
        ("blog", "个人博客", "herta27.top", "#65D9FF", 232, 92),
        ("email", "联系我", "EMAIL", "#C4B5FD", 170, 80),
    ):
        content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="38" viewBox="0 0 {width} 38" role="img" aria-label="{label}：{value}">
  <title>{label}：{value}</title>
  <rect width="{width}" height="38" rx="5" fill="#142338"/>
  <path d="M{split} 0 H{width - 5} Q{width} 0 {width} 5 V33 Q{width} 38 {width - 5} 38 H{split} Z" fill="{color}"/>
  <text x="{split / 2}" y="24" text-anchor="middle" fill="#FFFFFF" font-family="{SVG_CJK_FONT}" font-size="14" font-weight="700">{label}</text>
  <text x="{(split + width) / 2}" y="24" text-anchor="middle" fill="#142338" font-family="{SVG_MONO_FONT}" font-size="15" font-weight="700">{value}</text>
</svg>
'''
        (OUTPUT_DIR / f"badge-{name}.svg").write_text(content, encoding="utf-8", newline="\n")


def render(theme_name: str) -> None:
    render_header_gif(theme_name)
    render_header_svg(theme_name)
    render_header_gif(theme_name, mobile=True)
    render_header_svg(theme_name, mobile=True)
    render_about_svg(theme_name)
    render_about_svg(theme_name, mobile=True)
    render_footer_svg(theme_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic GitHub Profile visual assets.")
    parser.add_argument("--preview", type=Path, help="Optional Light/Dark PNG preview output path.")
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    render("light")
    render("dark")
    render_badges()
    if args.preview:
        render_preview(args.preview)


if __name__ == "__main__":
    main()
