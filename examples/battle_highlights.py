"""Read the player's battle log like a sports commentator.

uv run python examples/battle_highlights.py #LPP289
"""

from __future__ import annotations

import sys

from clash_royale_api_py import ClashRoyaleAPI


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "#LPP289"

    api = ClashRoyaleAPI()
    player = api.players.get(tag)
    print(f"🎮 {player.name} — {player.trophies} 🏆 (best {player.best_trophies})")
    print()

    for battle in api.players.battle_log(tag)[:5]:
        for_ = battle.crowns_for
        against = battle.crowns_against
        outcome = "✅ Victory" if (for_ or 0) > (against or 0) else "❌ Defeat"
        opponent_name = (battle.opponent or [None])[0]
        opponent = getattr(opponent_name, "name", None) or "an opponent"
        change = battle.trophy_change
        trophies = f" ({change:+d} 🏆)" if change else ""
        print(f"{outcome}  {for_} – {against} vs {opponent}{trophies}")


if __name__ == "__main__":
    main()
