#!/usr/bin/env python3
"""Assemble the Blowback notes + transcripts into a MkDocs docs/ tree + nav.
Source of truth stays in poopie/random/blowback; this only ever reads it.
Re-run any time the notes change, then `mkdocs gh-deploy`.
"""
import re
import shutil
from pathlib import Path

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

    nav = ["  - Home: index.md"]

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
            body = ep.read_text(encoding="utf-8")

            has_t = k in transcripts
            if has_t:
                tname = ep.stem + ".md"
                # transcript page: preserve line breaks, link back to note
                raw = transcripts[k].read_text(encoding="utf-8").strip()
                hard = raw.replace("\n", "  \n")
                (tdir / tname).write_text(
                    f"# {title} — Transcript\n\n"
                    f"[← Back to episode notes](../{ep.name})\n\n"
                    f"{hard}\n",
                    encoding="utf-8",
                )
                transcript_nav.append(
                    f"        - {title}: season-{s}/transcripts/{tname}"
                )
                link = f"> 📄 **[Read the full transcript](transcripts/{tname})**\n\n"
                body = re.sub(r"(^# .*\n)", r"\1\n" + link, body, count=1)

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
