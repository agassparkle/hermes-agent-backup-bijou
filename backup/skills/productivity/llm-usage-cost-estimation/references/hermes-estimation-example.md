# Worked Example: Estimating Hermes Agent Token Usage

**User:** Alp (agas), Ubuntu 20.04 server, Hermes default install (MiniMax M3 model).

## Data Gathered

| Source | Finding |
|--------|---------|
| `~/.hermes/.hermes_history` | 61 CLI commands over 8 days (Jun 10–19). Heavy early days: 13/18/21 commands Jun 10/11/12. Quiet after: 1–3 commands/day. |
| `hermes prompt-size` | Baseline = **~23K input tokens per turn**: system 5K + tool schemas 14K + skills 2.1K + memory 0.6K + profile 0.4K + volatile 1.1K. 39 tools. |
| `config.yaml` compression | threshold 0.5, target_ratio 0.2, protect_last_n 20, hygiene_hard_message_limit 400. Default model context = 1M (MiniMax M3). |
| `hermes auth list` | openai-codex rate-limited (429, 21d 11h left) → was used enough to hit limits. |
| `sessions/` (29 request dumps) | Mostly failed Codex calls, ~10K tokens each before failing. |
| Cron jobs | Pill reminder: every minute 09:00–11:59 = 180 runs/day. |

## Run A: Bottom-Up Tier Estimate

| Component | Turns/day | Input/turn | Output/turn | Daily In | Daily Out |
|-----------|-----------|------------|-------------|----------|-----------|
| Heavy turns (5+ tools, vision, web) | 5 | 80,000 | 3,000 | 400,000 | 15,000 |
| Medium turns (2–4 tools) | 10 | 35,000 | 1,500 | 350,000 | 15,000 |
| Light turns (Q&A, 0–1 tool) | 15 | 25,000 | 500 | 375,000 | 7,500 |
| Cron (pill reminder) | 180 | 8,000 | 300 | 1,440,000 | 54,000 |
| Failed Codex calls | 2 | 10,000 | 500 | 20,000 | 1,000 |
| **TOTAL** | | | | **2,585,000** | **92,500** |

**Daily total: ~2.68M tokens/day**

## Run B: Top-Down Compression Estimate

Signals:
- Sessions regularly reach ~500K tokens before compression (1M × 0.5)
- After compression: ~100K tokens kept (500K × 0.2)
- protect_last_n=20 implies 30+ messages before compression → ~15 turns/session
- Sessions/day estimate: 2 (based on heavy early-day clustering)

```
Daily interactive = 2 sessions × 15 turns × 100K avg input  = 3,000,000 in
                    2 sessions × 15 turns × 2K   avg output = 60,000 out
+ Cron: 180 × 8K = 1,440,000 in, 54,000 out
+ Failed calls: 20,000 in, 1,000 out
TOTAL = 4,460,000 in / 115,000 out → 4.58M tokens/day
```

## Combined Estimate

| Method | Daily IN | Daily OUT | Monthly Total |
|--------|----------|-----------|---------------|
| Run A (bottom-up) | 2.59M | 0.09M | 80M |
| Run B (top-down) | 4.46M | 0.12M | 137M |
| **Average** | **3.52M** | **0.10M** | **~109M** |

## Cost Projections (if paying out-of-pocket)

| Model | $/1M in | $/1M out | Monthly @ avg |
|-------|---------|----------|---------------|
| DeepSeek V4 Flash | $0.10 | $0.20 | $11 |
| Tencent HY3 | $0.066 | $0.26 | $8 |
| **MiniMax M3 (default)** | **$0.60** | **$2.40** | **$71** |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $364 |
| Claude Opus 4.8 | $5.00 | $25.00 | $606 |

## Key Insights

1. **Cron job dominates cost.** 1.44M tokens/day just from one pill reminder (53% of total). Reducing frequency from every minute to every 5 minutes cuts that to 288K — saves ~70% on cron overhead.
2. **Baseline prompt is the floor.** Even a "trivial" Q&A still costs ~23K input tokens due to system prompt + tool schemas. Reducing tool count (load skills selectively) helps.
3. **Compression settings reveal session shape.** protect_last_n=20 + hygiene_hard_message_limit=400 implies sessions can grow very long before being cleaned up. If cost matters, lower target_ratio or shorten sessions.

## Recommended Optimizations

| Action | Estimated savings |
|--------|-------------------|
| Reduce cron frequency (every 5 min instead of 1) | -1M tokens/day (~30%) |
| Switch cron to `no_agent=true` script-only mode | -1.5M tokens/day (~50% of cron cost) |
| Compress conversations more aggressively (lower threshold) | -10–20% on long sessions |
| Use Haiku-class model for cron + simple queries | -40% on those turns |

## What This Estimate Misses

- Sub-agent delegation token amplification (parent + child burn tokens)
- Vision/image upload tokens (1–2K per image, not counted here)
- Tool result caching (if enabled, can cut redundant calls by 90%)
- Model-switching mid-session (different models = different pricing)