# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/zenoonne/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/zenoonne/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

An illustrated newspaper front page that sums up Thursday 19 November 2026: a masthead carrying the date, a strip giving the 33-story count per region and six big statistics from the day, a "HOW SURE ARE WE?" line, three big illustrated features with detailed cartoon scenes, ten medium illustrated stories, and a compact list of twenty more. Every illustrated story carries a confidence tag — **REPORTED**, **FORECAST** or **CLAIM** — so the page is honest about what is asserted versus asserted-by-someone. Alongside the world map (numbered pins for where the features happened) are two new panels: a **MARKETS & MONEY** box with the day's market-moving numbers (Anthropic's Nasdaq debut, the Intuit–Mailchimp sale, Nvidia's subpoena, the ~900,000 AI chips cleared for China and Walmart's raised outlook) and a **THE DAY BY HOURS** timeline of five events whose clock times are verified to the minute from primary sources (the ABS jobs release, the ICJ ruling, the Nasdaq open, a US Senate roll-call and the Wall Street close). Every one of the 33 items is an *event of that day* (not just a 19 November report), verified against a primary outlet and recorded with its event date in `SOURCES.md`; a "DATE CHECK" box names the stories left off the page because they actually happened on other days (the Van Gogh auction, the EU's €45bn Ukraine loan proposal, the Clark/Jeffries House votes and the UK inflation release, all other days in that week). Each feature has a bold headline, a one-line sourced subline, a coloured region tag and a small code-drawn cartoon scene (a three-leader summit with flags, a Nasdaq opening screen, a courthouse with scales, a cyclone over a coast and more). The renderer (`render.py`, Python + Pillow) draws the whole page offline and deterministically from embedded data — including the simplified public-domain world map and every illustration — with no external images; the graded entrypoint (`main.ts`) copies the rendered `entry.png` to the output directory.

## Run it

```sh
node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
