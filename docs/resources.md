# Resources

One consistent grammar across everything: `get` for one, `search` / `list`
for many. Every method has a sync and an async version with the same name.

Every method that returns a `Page` also accepts `limit=`, `after=` and
`before=`. You normally only pass `limit`, and let `page.iter_all()` follow
the cursors; the `after` / `before` arguments exist for when you want to drive
paging yourself.

## `api.clans`

| Method | Returns | Notes |
|---|---|---|
| `clans.get(tag)` | `Clan` | Tags are normalized for you |
| `clans.search(name=..., location_id=..., min_members=..., max_members=..., min_score=..., limit=...)` | `Page[Clan]` | `name` needs 3+ characters |
| `clans.members(tag, limit=...)` | `Page[ClanMember]` | |
| `clans.war_log(tag, limit=...)` | `Page[ClanWarLogEntry]` | Classic war history — currently disabled upstream (404) |
| `clans.current_war(tag)` | `CurrentClanWar` | Retired upstream: raises `GoneError` (410) — use `current_river_race` |
| `clans.river_race_log(tag, limit=...)` | `Page[RiverRaceLogEntry]` | Clan Wars 2 history |
| `clans.current_river_race(tag)` | `CurrentRiverRace` | `.our_clan` picks out the requested clan |

## `api.players`

| Method | Returns |
|---|---|
| `players.get(tag)` | `Player` |
| `players.upcoming_chests(tag)` | `UpcomingChests` (iterable) |
| `players.battle_log(tag)` | `list[Battle]` |

## `api.cards`

| Method | Returns |
|---|---|
| `cards.list(limit=...)` | `Page[Card]` |
| `cards.all()` | `CardList` (iterable) |

## `api.events`

| Method | Returns |
|---|---|
| `events.list()` | `list[TrailEvent]` |

## `api.tournaments` / `api.global_tournaments`

| Method | Returns |
|---|---|
| `tournaments.search(name=..., limit=...)` | `Page[TournamentHeader]` |
| `tournaments.get(tag)` | `Tournament` |
| `global_tournaments.list()` | `list[LadderTournament]` |

## `api.locations`

| Method | Returns |
|---|---|
| `locations.list(limit=...)` | `Page[Location]` |
| `locations.get(id)` | `Location` |
| `locations.clan_rankings(id, limit=...)` | `Page[ClanRanking]` |
| `locations.clan_war_rankings(id, limit=...)` | `Page[ClanRanking]` |
| `locations.player_rankings(id, limit=...)` | `Page[PlayerRanking]` |
| `locations.path_of_legend_players(id, limit=...)` | `Page[PlayerPathOfLegendRanking]` |
| `locations.path_of_legend_season_rankings(season_id, limit=...)` | `Page[PlayerPathOfLegendRanking]` |
| `locations.league_seasons()` | `list[LeagueSeason]` |
| `locations.league_seasons_v2()` | `list[LeagueSeason]` |
| `locations.league_season(season_id)` | `LeagueSeason` |
| `locations.league_season_rankings(season_id, limit=...)` | `Page[PlayerRanking]` |
| `locations.global_tournament_rankings(tournament_tag, limit=...)` | `Page[LadderTournamentRanking]` |

!!! warning "Deprecated upstream"
    `locations.player_rankings` returns an empty list these days —
    prefer `path_of_legend_players`.

!!! warning "Legacy seasons"
    Season rankings only exist for legacy seasons (newest working: `2022-09`);
    newer seasons answer 404. `league_seasons_v2` currently sends `unique_id`,
    `end_time` and `code` as nulls.

## `api.leaderboards`

| Method | Returns |
|---|---|
| `leaderboards.list()` | `list[Leaderboard]` |
| `leaderboards.get(leaderboard_id, limit=...)` | `Page[LeaderboardEntry]` |
| `leaderboards.league(leaderboard_id, league_id, limit=...)` | `Page[LeaderboardEntry]` |

`leaderboards.league` only makes sense for competitive leaderboards, which
declare their leagues; `leagues` is empty outside an active season.

## `api.raw`

The escape hatch for anything this library has not wrapped. It performs the
same authenticated, retried GET and returns the decoded JSON untouched:

```python
data = api.raw.get("/players/%232PP")
data = api.raw.get("/clans/%232PP/members", params={"limit": 10})
```

## Paging

A `Page` is a sequence: iterate it, index it, take its length.

```python
page = api.clans.members("2PP")     # one request
for member in page:                 # that page only
    print(member.name)

for member in page.iter_all():      # follows the cursors for you
    print(member.name)
```

To page manually, use `page.cursors` and `page.next_page()`.
