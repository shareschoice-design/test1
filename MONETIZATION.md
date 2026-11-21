# Wild Rewind – monetisation plan

> Thresholds below are YouTube's published rules as of 2025 – double-check the current numbers in
> YouTube Studio → Earn before relying on them.

## 1. What YouTube requires

| Tier | Requirement | Unlocks |
|---|---|---|
| YPP lower tier | 500 subs + 3 uploads in last 90 days + **3M Shorts views in 90 days** (or 3,000 long-form watch hours / 12 months) | Memberships, Super Thanks, Shopping |
| YPP full | 1,000 subs + **10M Shorts views in 90 days** (or 4,000 long-form watch hours / 12 months) | Ad revenue share (Shorts + long-form) |

Shorts views do **not** count toward watch hours. Every application is reviewed **by a human**, who looks at the channel as a whole.

## 2. The two policies that kill channels like this

1. **Reused content.** If the reviewer sees mostly other people's footage (BBC logos, someone else's watermark), the channel is rejected, even with a voiceover. → Footage must be **licensed / free-to-use**, and our own work (script, explainer visuals, edit) must clearly dominate.
2. **Inauthentic / mass-produced content.** The same template, same synthetic voice and same structure in every video looks automated. → Vary the structure, write a unique researched script each time, and ideally use a human or premium voice.

Plus **Content ID:** a short with a claimed clip sends its revenue to the claimant. BBC / Nat Geo / Discovery clips will be claimed.

## 3. Decisions

| Item | Decision |
|---|---|
| BBC croc + tiger shorts | **Do not upload** to this channel. Rebuild them with licensed footage (the scripts and infographics are reusable). |
| Owl short | Upload only after written permission from @nickloveswildlife (template below). |
| Footage share | Real footage ≤ 30–35 % of runtime, explainer visuals ≥ 65 % (already the case). |
| Voice | Short term: current voice. Before applying to YPP: switch to your own recorded voice or a premium TTS (e.g. ElevenLabs) – it's the single biggest "this is a real creator" signal. |
| Format variety | Rotate 3 formats: **Rewind** (outcome → cause), **Myth vs Fact**, **Ranking** ("3 animals that…"). Don't use the identical template every day. |
| AI disclosure | Tick "altered or synthetic content" only if a clip shows realistic AI animals/events. Stylised infographics + TTS narration usually don't need it. |

## 4. Where to get footage you can monetise (best first)

1. **Creator permission:** DM wildlife filmmakers on Instagram/TikTok/YouTube. Many say yes for credit + link. Keep the written "yes" (screenshot/email).
2. **Public domain (US government):** NPS, US Fish & Wildlife Service, NOAA, USGS b-roll is usually public domain. Check each item's page.
3. **Free stock:** Pexels, Pixabay (commercial use allowed, no attribution needed). Great for b-roll, rarely has dramatic hunts.
4. **Paid stock:** Storyblocks / Artgrid (subscription) or Pond5 (per clip). Best for dramatic hunting shots.
5. **Wikimedia Commons:** only CC0 / CC-BY / CC-BY-SA (credit as required). Avoid "NC" (non-commercial) licences.

**Permission request template:**
```
Hi <name>! I run Wild Rewind, a wildlife explainer channel on YouTube Shorts.
I'd love to use ~6–9 seconds of your <animal> clip inside an explainer short
(voiceover + diagrams), with your name and a link in the title/description.
Would that be OK? Happy to send you the edit before it goes live. Thanks!
```

## 5. What it can realistically earn

- **Shorts** pay little: roughly $0.02–0.10 per 1,000 views (varies by audience/country). 10M views ≈ a few hundred dollars.
- **Long-form pays 20–50× more per view.** After ~30 shorts, compile them into 8–12 min horizontal "Wild Rewind" episodes. This also counts toward the 4,000-watch-hour route.
- **Other platforms:** TikTok pays only for videos over 1 minute (make 61–70 s cuts); Facebook Reels and Instagram also pay. The same footage licence must cover them.

## 6. 90-day roadmap

| Weeks | Goal |
|---|---|
| 1–2 | Create channel, upload logo + banner + description. Secure footage for 10 shorts (permissions / stock). Publish 1 per day. |
| 3–6 | Read analytics: aim for > 70 % "viewed vs swiped away" and > 80 % average view percentage. Double down on the best topics. |
| 6–8 | First long-form compilation (8–12 min). Start TikTok / Reels cross-posting. |
| 8–12 | Switch to human/premium voice. Apply to YPP as soon as thresholds are hit. |

## 7. Footage workflow (how we actually get clips)

The cloud environment that builds the videos can't download from stock sites directly
(Pexels/Pixabay block automated access, Pexels has paused new API keys, Wikimedia rate-limits the shared cloud IP).
So: **you download in your browser, upload the file to the chat, and say where it's from.**

For every clip keep a line in the video description:
- Pexels / Pixabay: no attribution required, but credit anyway: `Footage: <author> / Pexels`
- Wikimedia Commons CC BY: `Footage: "<file title>" by <author>, CC BY 3.0, via Wikimedia Commons`
- **CC BY-SA:** usable commercially, but the whole short must then be released under CC BY-SA too – prefer CC BY / CC0 / public domain.
- Never NC (non-commercial) or ND (no derivatives).

`shorts_tool/commons_file.py <File:...>` prints licence, author, length and resolution of any Commons file page.
