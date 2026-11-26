# news-image-20261126 — The World Today: 26 November 2026

[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/c/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/bimasetmuse61/news-image-20261126/rank.svg)](https://make.fun/c/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/bimasetmuse61/news-image-20261126/reward.svg)](https://make.fun/c/news-image-20261126)

A newspaper front page summing up Thursday 26 November 2026's world
news in one image, for the
[make.fun](https://make.fun/c/news-image-20261126) competition
"Sum up 26 November's world news in one image".

## The day's news

- **Lead — Middle East / Energy:** Yemen's Houthis claim strikes on
  Saudi Arabia's Ras Tanura refinery and Riyadh's financial district;
  Brent crude tops $94.
- **Trade:** the US proposes new tariffs of up to 15% on 14 trading
  partners to fight factory overcapacity.
- **Markets:** the Nasdaq slides nearly 4% as the AI-stock rout deepens.
- **Egypt:** a fuel-tanker crash on a Cairo highway ignites a blaze
  that kills at least 30 people.
- **Space:** BepiColombo, Europe and Japan's probe, reaches Mercury
  orbit after an eight-year journey.
- **War in Ukraine:** Kyiv says its strike on a Russian air base
  damaged five planes.
- **Asia:** North Korea orders Switzerland to shut its new diplomatic
  office in Pyongyang.
- **Also today:** Russia's own figures put its war dead near 500,000;
  Israeli judges urge dropping the gravest charges against Netanyahu;
  Gukesh draws Game 2 of the World Chess Championship final; India
  marks Constitution Day.

## How it works

`main.py` (Python 3.13, standard library only) draws the whole front
page in code — masthead, headlines, body copy and every illustration —
and writes it as a 1024x1024 PNG to `$MAKEFUN_OUTPUT_DIR/entry.png`
(or `/output/entry.png`). No network, no fonts, no image files: the
5x7 bitmap font and the PNG encoder are written in the program itself,
so the two grading runs produce byte-identical output.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
