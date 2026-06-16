# About & Methodology

This is an **unofficial fan companion** to the *Blowback* podcast (hosts **Brendan James & Noah Kulwin**) — a transparency-first set of read-along notes and transcripts. Here's exactly how it was made, so you can judge it for what it is.

!!! warning "Read this first"
    The transcripts and notes are **machine-generated** (speech-to-text + an AI language model). They are a study aid, **not** an authoritative record. They contain errors — especially in spellings of names/places and exact dates. When something matters, **trust the audio and the original cited sources**, not this site.

## 1. Transcription — OpenAI Whisper

Audio was pulled from the show's **public RSS feed** (not ripped from any paywalled service) and transcribed locally with the open-source **Whisper** model — specifically `distil-large-v3` via `faster-whisper` (int8, CPU). Processing ran at roughly **4× real-time** on a personal machine; nothing was sent to a paid API.

- Timestamps (`[hh:mm:ss]`) are **Whisper-generated** and approximate — good enough to find a moment in the audio, not frame-accurate.
- Whisper mishears proper nouns and occasionally garbles dates; obvious slips were corrected against context where caught, but some remain.

## 2. Notes — Anthropic's Claude (Opus)

The episode notes were written by **Claude (Opus model)** from two inputs only: the Whisper transcript, and the show's **own published bibliography** (see §4). The model worked to a **fixed format spec** rather than free-styling:

- Follow the episode's **narration order** (the order the hosts tell it), not reordered chronology.
- Anchor points to the audio with `[hh:mm:ss]`; put real-world dates in **bold**.
- Preserve the hosts' **analysis, arguments, asides, and quotes** — not just dry facts.
- **Don't invent facts.** Everything traces to the transcript or the sources file. Silently fix only obvious transcription errors.
- End each note with the episode's cited sources, numbered `[1] [2] …`.

Because an AI wrote them, treat the notes as a *high-quality summary that can still be wrong*, not as a primary source.

## 3. How this site is built & published

Notes and transcripts are compiled **locally** by a small Python script into a static site with **[MkDocs](https://www.mkdocs.org/) + the Material theme**, then published free on **GitHub Pages**. There is no server, database, tracking, or ads. The site is marked `noindex` — it won't show up in search engines; it's meant to be shared by link.

## 4. Sources

The sources listed under each episode are taken **from the show's own official per-season bibliographies** at [blowback.show](https://blowback.show) — i.e. the references *the hosts themselves* published. They are reproduced (and numbered) for convenience; the reporting and source-gathering is entirely the show's work.

## 5. Credit & contact

All journalism, analysis, and storytelling belongs to **Brendan James, Noah Kulwin, and the Blowback team**. Please **support the show** and listen officially at **[blowback.show](https://blowback.show)**.

This companion exists only to help listeners follow and remember the series. If you're affiliated with the show and would like it changed or taken down, that request will be honored — reach out via the repository it's published from.
