---
tags:
  - nicholas-crown
  - process
---

# How we collect

## Why you don’t get a captcha and the agent does

You and the agent can sit on the **same** shared TikTok tab and still look like **two different users**.

- **Your clicks** are a real mouse, human timing, often with TikTok cookies from a normal session.
- **Agent clicks** go through computer-control (CDP / accessibility). TikTok treats that like a bot: slider captcha, then **Something went wrong**.
- This cloud Chrome also uses a **datacenter IP**. TikTok already **403s** plain HTTP from here. Your home/phone IP is trusted; this VM’s IP is not.
- After the agent hammers Latest, the **tab stays poisoned** even if you click next. That is why the profile can show an error with **no captcha on screen**.

So: **you open the video, I only read.** I do not click through the grid.

## Do not use Playwright (or Puppeteer) on TikTok

Playwright sets `navigator.webdriver` and other automation fingerprints. TikTok is built to block that. A “Playwright formula” would get **more** captchas, not fewer, and it is against TikTok’s terms (no unofficial scrapers). We will not add a TikTok Playwright crawler to this repo.

## What works

| Method | Result (2026-08-20) |
|---|---|
| HTTP fetch of tiktok.com | **403** (Akamai) |
| Agent clicking videos | 4 clips, then captcha / error |
| **You click, agent transcribes** | Intended path for the rest of the month |
| YouTube `@NicholasCrownYouTube` | No uploads in the last 30 days |
| LinkedIn public posts | Captions Jul 22–Aug 15 ([[Creators/Nicholas Crown/LinkedIn month]]) |

## Shared-browser protocol

1. You open [tiktok.com/@nicholas_crown](https://www.tiktok.com/@nicholas_crown) on a session that still loads videos (refresh or a new tab if this VM tab is stuck).
2. Click **one** clip. Leave it playing with the caption visible.
3. Tell the agent **transcribe this one**. Do not ask it to click the next twenty.
4. Notes go under `Creators/Nicholas Crown/TikTok/` using the template below.

Do not paste Crown Macro paid-issue text into the vault.

## Note template (new TikTok)

```yaml
---
tags: [nicholas-crown, tiktok]
date: YYYY-MM-DD
url: https://www.tiktok.com/@nicholas_crown/video/...
type: macro | options | pitch | skit
tickers: []
---
```

Then: **Caption**, **What he said** (paraphrase of points, not a full script dump), **So what**, links to [[Creators/Nicholas Crown/Glossary]].
