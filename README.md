# Tiny Chess Bot

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/malapetakasatu/tiny-chess-bot/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/malapetakasatu/tiny-chess-bot/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A deterministic grandmaster chess engine in under 4KB of Python for the make.fun tiny-chess-01 bounty with PeSTO evaluation and dynamic anti-repetition.

## Architecture
- Deterministic alpha-beta search with quiescence search to resolve captures.
- Midgame and endgame piece-square tables adapted from PeSTO.
- Dynamic repetition penalty to prevent forced draws in advantageous positions.
