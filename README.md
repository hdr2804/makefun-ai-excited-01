# make.fun ai-excited-01 — "One small leap becomes a universe"

Entry for the make.fun competition **ai-excited-01** ("Make the AI judge
excited", $250, top 20 paid). The program is `main.ts` (Node 22, standard
library only): it copies `entry.png` to `/output/entry.png`.

## The image

A tiny goldfish leaps out of its little glass bowl (bottom left) and its
splash becomes a huge curling wave that spirals up into a galaxy of stars
and confetti (top right) — a scale twist, not a stock explosion or
firework. Saturated warm orange/magenta on deep indigo, a strong diagonal
composition, a bold tilted `WOW!` the judge can read, and a second little
fish still in the bowl cheering it on. The image is drawn fully in code
by `draw_excited.py` (PIL, build-time only, deterministic seed) — no
external assets.

- Format: PNG, 1024×1024, ~370 KB (cap: 1 MiB, 1024×1024)
- Deterministic: the program is run twice and must write identical bytes.

## Run locally

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```
