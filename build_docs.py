#!/usr/bin/env python3
"""Assemble the Blowback notes + transcripts into a MkDocs docs/ tree + nav.
Source of truth stays in poopie/random/blowback; this only ever reads it.
Re-run any time the notes change, then `mkdocs gh-deploy`.
"""
import re
import shutil
from pathlib import Path
from urllib.parse import quote

SRC = Path("/home/purubuntu/projects/poopie/random/blowback")
NOTES = SRC / "notes"
TRANSCRIPTS = SRC / "transcripts"
OUT = Path(__file__).parent / "docs"

CODE = re.compile(r"s(\d+)e(\d+)", re.I)
SEASONS = range(1, 7)


def ep_key(name):
    m = CODE.search(name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def h1_title(md_path):
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            return t.replace("Blowback ", "").replace('"', "").strip()
    return md_path.stem


SRC_HEADING = "## Sources cited for this episode"


def number_sources(body):
    """Prefix each individual source in the episode's bibliography with [n]."""
    if SRC_HEADING not in body:
        return body
    head, tail = body.split(SRC_HEADING, 1)
    n = 0
    out = []
    for line in tail.split("\n"):
        m = re.match(r"^- (\*\*.*?:\*\*|_.*?:_)?\s*(.*)$", line)
        if line.startswith("- ") and m and m.group(2):
            label = (m.group(1) + " ") if m.group(1) else ""
            items = []
            for it in m.group(2).split(" · "):
                it = it.strip()
                if not it:
                    continue
                n += 1
                items.append(f"[{n}] {it}")
            out.append("- " + label + " · ".join(items))
        else:
            out.append(line)
    return head + SRC_HEADING + "\n".join(out)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # index transcripts by (season, episode)
    transcripts = {}
    for txt in TRANSCRIPTS.rglob("*.txt"):
        k = ep_key(txt.name)
        if k:
            transcripts[k] = txt

    nav = ["  - Home: index.md", "  - About & Methodology: about.md"]

    for s in SEASONS:
        sdir = OUT / f"season-{s}"
        tdir = sdir / "transcripts"
        sdir.mkdir(parents=True, exist_ok=True)
        tdir.mkdir(parents=True, exist_ok=True)

        episodes = sorted(
            (p for p in NOTES.glob(f"s{s}e*.md") if ep_key(p.name)),
            key=lambda p: ep_key(p.name),
        )

        season_nav = []

        # season-level pages first
        tl = NOTES / f"s{s}-timeline.md"
        srcfile = NOTES / f"s{s}-sources.md"
        if tl.exists():
            shutil.copy(tl, sdir / "timeline.md")
            season_nav.append(f"      - Season Timeline: season-{s}/timeline.md")
        if srcfile.exists():
            shutil.copy(srcfile, sdir / "sources.md")
            season_nav.append(f"      - Sources: season-{s}/sources.md")

        transcript_nav = []
        for ep in episodes:
            k = ep_key(ep.name)
            title = h1_title(ep)
            body = number_sources(ep.read_text(encoding="utf-8"))

            q = quote(re.sub(r"\s+", " ", f"Blowback {title}".replace("—", " ")).strip())
            listen = (
                "> 🎧 **Listen here:** "
                f"[:simple-spotify: Spotify](https://open.spotify.com/search/{q}){{target=_blank}}"
                " · [:material-web: blowback.show](https://blowback.show){target=_blank}"
            )

            has_t = k in transcripts
            if has_t:
                tname = ep.stem + ".md"
                # transcript page: preserve line breaks
                hard = transcripts[k].read_text(encoding="utf-8").strip().replace("\n", "  \n")
                (tdir / tname).write_text(
                    f"# {title} — Transcript\n\n"
                    f"{listen}\n> 📄 **[Episode notes](../{ep.name})**\n\n"
                    f"{hard}\n",
                    encoding="utf-8",
                )
                transcript_nav.append(
                    f"        - {title}: season-{s}/transcripts/{tname}"
                )
                header = listen + f"\n> 📄 **[Read the full transcript](transcripts/{tname})**\n\n"
            else:
                header = listen + "\n\n"

            first, _, rest = body.partition("\n")
            body = f"{first}\n\n{header}{rest.lstrip(chr(10))}"
            (sdir / ep.name).write_text(body, encoding="utf-8")
            season_nav.append(f"      - {title}: season-{s}/{ep.name}")

        # transcripts with no matching note (prologues/trailers)
        emitted = {ep_key(p.name) for p in episodes}
        for k, txt in sorted(transcripts.items()):
            if k[0] != s or k in emitted:
                continue
            slug = txt.stem
            title = slug.replace("-", " ").title()
            hard = txt.read_text(encoding="utf-8").strip().replace("\n", "  \n")
            (tdir / f"{slug}.md").write_text(
                f"# {title} — Transcript\n\n{hard}\n", encoding="utf-8"
            )
            transcript_nav.append(f"        - {title}: season-{s}/transcripts/{slug}.md")

        if transcript_nav:
            season_nav.append("      - Transcripts:")
            season_nav.extend(transcript_nav)

        nav.append(f"  - Season {s}:")
        nav.extend(season_nav)

    write_index()
    write_about()
    write_config("\n".join(nav))
    print(f"Built {sum(1 for _ in OUT.rglob('*.md'))} pages into {OUT}")


def write_index():
    (OUT / "index.md").write_text(
        "# Blowback — Listening Companion\n\n"
        "Read-along notes and full transcripts for the **Blowback** podcast "
        "(hosts **Brendan James & Noah Kulwin**).\n\n"
        "Each episode has a narration-order set of notes with `[hh:mm:ss]` jump "
        "points, real-world dates in **bold**, the hosts' analysis preserved, "
        "and the sources they cite — plus the **full transcript**.\n\n"
        "## How to use this\n\n"
        "- Pick a season in the left sidebar, then an episode.\n"
        "- Play the episode and read along — the `[hh:mm:ss]` markers line up with the audio.\n"
        "- Use the **search box** (top) to find any person, place, or event across all seasons.\n\n"
        "## Seasons\n\n"
        "1. **Iraq** — the road to the 2003 invasion\n"
        "2. **Cuba** — the revolution and the long US siege\n"
        "3. **Korea** — the war that never ended\n"
        "4. **Afghanistan** — empire's graveyard\n"
        "5. **The First Gulf War & after**\n"
        "6. **Apartheid South Africa**\n\n"
        "---\n\n"
        "*This is an unofficial fan companion. All credit for the reporting and "
        "analysis belongs to the show. Support it at "
        "[blowback.show](https://blowback.show).*\n",
        encoding="utf-8",
    )
    # belt-and-suspenders: keep search engines out
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")


def write_about():
    (OUT / "about.md").write_text(
        "# About & Methodology\n\n"
        "This is an **unofficial fan companion** to the *Blowback* podcast (hosts "
        "**Brendan James & Noah Kulwin**) — a transparency-first set of read-along "
        "notes and transcripts. Here's exactly how it was made, so you can judge it "
        "for what it is.\n\n"
        "!!! warning \"Read this first\"\n"
        "    The transcripts and notes are **machine-generated** (speech-to-text + an "
        "AI language model). They are a study aid, **not** an authoritative record. "
        "They contain errors — especially in spellings of names/places and exact "
        "dates. When something matters, **trust the audio and the original cited "
        "sources**, not this site.\n\n"
        "## 1. Transcription — OpenAI Whisper\n\n"
        "Audio was pulled from the show's **public RSS feed** (not ripped from any "
        "paywalled service) and transcribed locally with the open-source **Whisper** "
        "model — specifically `distil-large-v3` via `faster-whisper` (int8, CPU). "
        "Processing ran at roughly **4× real-time** on a personal machine; nothing "
        "was sent to a paid API.\n\n"
        "- Timestamps (`[hh:mm:ss]`) are **Whisper-generated** and approximate — good "
        "enough to find a moment in the audio, not frame-accurate.\n"
        "- Whisper mishears proper nouns and occasionally garbles dates; obvious slips "
        "were corrected against context where caught, but some remain.\n\n"
        "## 2. Notes — Anthropic's Claude (Opus)\n\n"
        "The episode notes were written by **Claude (Opus model)** from two inputs "
        "only: the Whisper transcript, and the show's **own published bibliography** "
        "(see §4). The model worked to a **fixed format spec** rather than free-"
        "styling:\n\n"
        "- Follow the episode's **narration order** (the order the hosts tell it), not "
        "reordered chronology.\n"
        "- Anchor points to the audio with `[hh:mm:ss]`; put real-world dates in "
        "**bold**.\n"
        "- Preserve the hosts' **analysis, arguments, asides, and quotes** — not just "
        "dry facts.\n"
        "- **Don't invent facts.** Everything traces to the transcript or the sources "
        "file. Silently fix only obvious transcription errors.\n"
        "- End each note with the episode's cited sources, numbered `[1] [2] …`.\n\n"
        "Because an AI wrote them, treat the notes as a *high-quality summary that can "
        "still be wrong*, not as a primary source.\n\n"
        "## 3. How this site is built & published\n\n"
        "Notes and transcripts are compiled **locally** by a small Python script into "
        "a static site with **[MkDocs](https://www.mkdocs.org/) + the Material "
        "theme**, then published free on **GitHub Pages**. There is no server, "
        "database, tracking, or ads. The site is marked `noindex` — it won't show up "
        "in search engines; it's meant to be shared by link.\n\n"
        "## 4. Sources\n\n"
        "The sources listed under each episode are taken **from the show's own "
        "official per-season bibliographies** at "
        "[blowback.show](https://blowback.show) — i.e. the references *the hosts "
        "themselves* published. They are reproduced (and numbered) for convenience; "
        "the reporting and source-gathering is entirely the show's work.\n\n"
        "## 5. Credit & contact\n\n"
        "All journalism, analysis, and storytelling belongs to **Brendan James, Noah "
        "Kulwin, and the Blowback team**. Please **support the show** and listen "
        "officially at **[blowback.show](https://blowback.show)**.\n\n"
        "This companion exists only to help listeners follow and remember the series. "
        "If you're affiliated with the show and would like it changed or taken down, "
        "that request will be honored — reach out via the repository it's published "
        "from.\n",
        encoding="utf-8",
    )


def write_config(nav):
    cfg = Path(__file__).parent / "mkdocs.yml"
    cfg.write_text(
        "site_name: Blowback — Listening Companion\n"
        "site_description: Read-along notes and transcripts for the Blowback podcast\n"
        "theme:\n"
        "  name: material\n"
        "  custom_dir: overrides\n"
        "  palette:\n"
        "    - scheme: slate\n"
        "      primary: red\n"
        "      accent: red\n"
        "      toggle:\n"
        "        icon: material/weather-night\n"
        "        name: Light mode\n"
        "    - scheme: default\n"
        "      primary: red\n"
        "      accent: red\n"
        "      toggle:\n"
        "        icon: material/weather-sunny\n"
        "        name: Dark mode\n"
        "  features:\n"
        "    - navigation.instant\n"
        "    - navigation.tracking\n"
        "    - navigation.top\n"
        "    - search.highlight\n"
        "    - search.suggest\n"
        "    - content.code.copy\n"
        "    - toc.follow\n"
        "plugins:\n"
        "  - search\n"
        "markdown_extensions:\n"
        "  - admonition\n"
        "  - attr_list\n"
        "  - tables\n"
        "  - pymdownx.emoji:\n"
        "      emoji_index: !!python/name:material.extensions.emoji.twemoji\n"
        "      emoji_generator: !!python/name:material.extensions.emoji.to_svg\n"
        "  - toc:\n"
        "      permalink: true\n"
        "nav:\n" + nav + "\n",
        encoding="utf-8",
    )

    ov = Path(__file__).parent / "overrides"
    ov.mkdir(exist_ok=True)
    (ov / "main.html").write_text(
        "{% extends \"base.html\" %}\n"
        "{% block extrahead %}\n"
        '  <meta name="robots" content="noindex, nofollow">\n'
        "{% endblock %}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
