from __future__ import annotations

import argparse
import re
from pathlib import Path


LABEL_PATTERN = re.compile(r"Contributed to \(last year\):")
VALUE_PATTERN = re.compile(
    r'(<text\s+class="stat  bold"\s+x="224\.01"\s+y="12\.5"\s+'
    r'data-testid="contribs"\s*>\s*)\d+(</text>)'
)
DESC_PATTERN = re.compile(r"Contributed to \(last year\): \d+")


def patch_card(path: Path, total: int) -> None:
    content = path.read_text(encoding="utf-8")

    content, desc_count = DESC_PATTERN.subn(
        f"Contributions (last year): {total}", content
    )
    content, label_count = LABEL_PATTERN.subn("Contributions (last year):", content)
    content, value_count = VALUE_PATTERN.subn(rf"\g<1>{total}\g<2>", content)

    if (label_count, value_count, desc_count) != (1, 1, 1):
        raise RuntimeError(
            f"Unexpected stats card structure in {path}: "
            f"label={label_count}, value={value_count}, desc={desc_count}"
        )

    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace the repository-count metric with GitHub's contribution total."
    )
    parser.add_argument("--total", type=int, required=True)
    parser.add_argument("cards", nargs="+", type=Path)
    args = parser.parse_args()

    if args.total < 0:
        parser.error("--total must be non-negative")

    for card in args.cards:
        patch_card(card, args.total)
        print(f"updated {card} with {args.total} contributions")


if __name__ == "__main__":
    main()
