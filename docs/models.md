# Models

Every response comes back as a typed [Pydantic](https://docs.pydantic.dev)
model. Field names are `snake_case`; the API's `camelCase` names are handled
by aliases, so you never write `clanScore`.

```python
clan = api.clans.get("2PP")
clan.clan_score      # 50000
clan.required_trophies
```

## The shared base

All models inherit from `ClashRoyaleModel`, which provides:

- **`snake_case` fields**, read from the API's `camelCase` aliases.
- **Extra fields are kept.** The API ships new fields faster than the docs, so
  unknown ones stay reachable as attributes.
- **`.raw`** — the model as a plain dict, back in the API's `camelCase` shape.
  This is a re-serialization of the validated model, not the original bytes.

```python
clan.raw["clanScore"]
```

- **Readable `repr`/`print`** for models with a name or tag: `print(clan)`
  gives `<Clan 'Hog Riders' tag='#2PP'>` rather than a wall of fields.

## Models by resource

| Resource | Models |
|---|---|
| `api.clans` | `Clan`, `ClanMember`, `ClanWarLogEntry`, `ClanWarClan`, `ClanWarParticipant`, `ClanWarStanding`, `CurrentClanWar`, `RiverRaceLogEntry`, `RiverRaceClan`, `RiverRaceParticipant`, `RiverRaceStanding`, `PeriodLog`, `PeriodLogEntry`, `CurrentRiverRace` |
| `api.players` | `Player`, `PlayerClan`, `PlayerItemLevel`, `PlayerProgress`, `PlayerAchievementBadge`, `PlayerAchievementProgress`, `PlayerLeagueStatistics`, `LeagueSeasonResult`, `PathOfLegendSeasonResult`, `Battle`, `PlayerBattleData`, `PlayerBattleRound`, `PlayerBattleAugment`, `Chest`, `UpcomingChests` |
| `api.cards` | `Card`, `CardList` |
| `api.events` | `TrailEvent`, `Leaderboard`, `LeaderboardEntry` |
| `api.tournaments` | `Tournament`, `TournamentHeader`, `TournamentMember`, `LadderTournament`, `LadderTournamentRanking`, `SurvivalMilestoneReward` |
| `api.locations` | `Location`, `LeagueSeason`, `ClanRanking`, `PlayerRanking`, `PlayerPathOfLegendRanking` |
| shared | `Arena`, `GameMode`, `BadgeUrls`, `IconUrls`, `JsonLocalizedName` |

All of them are importable from the package root:

```python
from clash_royale_api_py.models import Card, Clan, Player
```

## Helper properties

A few models save you the nested lookups:

| Property | Model | Gives you |
|---|---|---|
| `.our_clan` | `CurrentRiverRace` | the requested clan in the race |
| `.points` | `RiverRaceClan` | live score (`period_points`, falling back to `fame`) |
| `.is_in_war` | `CurrentClanWar` | whether the clan is in a war at all |
| `.crowns_for` / `.crowns_against` | `Battle` | crowns for the player / opponent |
| `.trophy_change` | `Battle` | trophy delta for the player |

```python
race = api.clans.current_river_race("2PP")
if race.our_clan:
    print(race.our_clan.name, race.our_clan.points)

battle = api.players.battle_log("2PP")[0]
print(battle.crowns_for, "vs", battle.crowns_against)
```

## Iterable models

Some endpoints hand back a container that is also the model. `CardList` and
`UpcomingChests` support iteration, `len()`, and indexing:

```python
for chest in api.players.upcoming_chests("2PP"):
    print(chest.name)
```

## Localized names

Some fields arrive either as a plain string or as a localized object, so the
type is `str | JsonLocalizedName | None`. `JsonLocalizedName` stringifies to
its first translation and compares equal to a string, so both cases read the
same:

```python
print(card.name)            # works for either shape
card.name == "Knight"       # True
```

## Paginated results

Endpoints that can return many results give you a `Page`, not a model. See
[Resources](resources.md#paging) for iteration and manual cursors.
