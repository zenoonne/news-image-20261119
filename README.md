# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/zenoonne/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/zenoonne/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

An illustrated newspaper front page that sums up Thursday 19 November 2026: a masthead carrying the date, a strip giving the 33-story count per region and six big statistics from the day, three big illustrated features with detailed cartoon scenes, ten medium illustrated stories, a world map with numbered pins for where the features happened, and a compact list of twenty more. Every one of the 33 items is an *event of that day* (not just a 19 November report), verified against a primary outlet and recorded with its event date in `SOURCES.md`; a "DATE CHECK" box names the stories left off the page because they actually happened on other days (the Van Gogh auction, the EU's €45bn Ukraine loan proposal and the Clark/Jeffries House votes, all Wednesday 18 November). Each feature has a bold headline, a one-line sourced subline, a coloured region tag and a small code-drawn cartoon scene (a three-leader summit with flags, a Nasdaq opening screen, a courthouse with scales, a cyclone over a coast and more). The renderer (`render.py`, Python + Pillow) draws the whole page offline and deterministically from embedded data — including the simplified public-domain world map and every illustration — with no external images; the graded entrypoint (`main.ts`) copies the rendered `entry.png` to the output directory.

## Run it

```sh
node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
