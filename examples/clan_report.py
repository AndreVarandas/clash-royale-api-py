"""Explore your clan like it's the morning paper.

uv run python examples/clan_report.py 2PP
"""

from __future__ import annotations

import sys

from clash_royale_api_py import ClashRoyaleAPI


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "2PP"

    # No token passed? The client looks for CLASH_ROYALE_API_TOKEN.
    api = ClashRoyaleAPI()

    clan = api.clans.get(tag)
    print(f"⚔️  {clan.name} {clan.tag}")
    print(f"   score {clan.clan_score} · {clan.members} members · {clan.type}")
    if clan.description:
        print(f"   “{clan.description}”")
    print()

    print("Top 5 members:")
    for member in api.clans.members(tag, limit=5):
        print(f"  {member.clan_rank:>2}. {member.name} — {member.trophies} 🏆")

    race = api.clans.current_river_race(tag)
    if race.clans:
        print(f"\nCurrent river race ({race.period_type} {race.period_index}):")
        ranked = sorted(race.clans, key=lambda c: c.points, reverse=True)
        for position, standing in enumerate(ranked, start=1):
            marker = " ← us" if standing.tag == clan.tag else ""
            print(f"   {position}. {standing.name} — {standing.points} points{marker}")
    else:
        print("\nNo river race right now — perfect time for a friendly.")


if __name__ == "__main__":
    main()
