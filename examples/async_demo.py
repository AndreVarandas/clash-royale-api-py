"""The async twin — same API, with await in front.

uv run python examples/async_demo.py 2PP
"""

from __future__ import annotations

import asyncio

from clash_royale_api_py import AsyncClashRoyaleAPI


async def main() -> None:
    tag = "#2PP"

    async with AsyncClashRoyaleAPI() as api:
        clan = await api.clans.get(tag)
        print(f"⚔️  {clan.name} — {clan.members} members, score {clan.clan_score}")

        # Pagination reads just like the sync version.
        print("\nTop donators this week:")
        members = await api.clans.members(tag, limit=10)
        for member in sorted(members, key=lambda m: m.donations or 0, reverse=True)[:3]:
            print(f"   {member.name} gave {member.donations} troops 🎁")

        leaderboards = await api.leaderboards.list()
        print(f"\n{len(leaderboards)} leaderboards available this season.")


if __name__ == "__main__":
    asyncio.run(main())
