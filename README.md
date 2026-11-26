# The World in One Image — 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/nvtuananhh/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/nvtuananhh/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Entry for the make.fun bounty
[“Sum up 26 November's world news in one image”](https://make.fun/bounty/news-image-20261126)
($100, ends 28 Nov 2026 07:00 +07).

`main.py` (Python 3, standard library only, no network) draws a 1024×1024
newspaper-style front page summarising the world news of Thursday
26 November 2026 and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(or `/output/entry.png`):

- **Lead story** — a powerful Thanksgiving storm batters the East Coast;
  Macy's parade is postponed for the first time in 100 years.
- **US unveils new tariffs** on China, the EU, Brazil and a dozen partners.
- **30 killed in a Cairo fire** as a fuel tanker bursts into flames.
- **Hostages freed** in a Cartagena supermarket siege (17 hours).
- **Pakistan's first astronaut** named for China's Tiangong station.
- **Huawei found guilty** of stealing US trade secrets.
- **No deal at COP31**; climate talks may resume next year.
- **Mine flood in West Java** — 9 dead, 17 missing.
- **Australia–Solomon Islands** landmark security partnership.
- **Chinese H-6 bomber** spotted 170 nautical miles from Manila.
- **Also today** — US Army detonates five tons of explosives in Iowa;
  a wrongly deported migrant leaves the US for Spain; North Korea moves
  to shut Switzerland's Pyongyang office; two charged over a break-in at
  Sandringham; Nvidia brings back Jensen Huang as chief executive.

The image is rendered with a hand-written 5×7 bitmap font and a minimal
PNG encoder (zlib), so running the program twice produces byte-identical
output (verified: same SHA-256 across runs, 25,210 bytes).

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```
