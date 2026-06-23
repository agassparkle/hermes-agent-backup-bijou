---
name: llm-usage-cost-estimation
description: Estimate daily/monthly LLM API token usage and cost for a user or agent from observable signals (CLI history, session DBs, prompt size, compression settings). Combines bottom-up per-turn tier estimates with top-down compression-based sanity checks.
category: productivity
tags: [llm, token-usage, cost-estimation, api-billing, hermes, openai, anthropic]
---

# LLM Usage & Cost Estimation

Estimate token consumption and projected API cost for an LLM-powered system (Hermes Agent, custom agents, chat apps) when explicit per-request usage data isn't available.

## When to Use

- User asks "how much am I spending on AI / tokens?"
- User asks "what's my daily token usage?" or "monthly API bill estimate?"
- Setting budgets / deciding which provider/model to switch to
- Optimizing an agent's token footprint (cron jobs, tool schemas, conversation length)

## Inputs You Need

Collect whatever is available — every signal helps cross-check the estimate:

| Source | What it tells you | Where to look |
|--------|-------------------|---------------|
| **CLI / shell history** | Commands per day = minimum session count | `~/.bash_history`, `~/.hermes/.hermes_history` |
| **System prompt size** | Baseline input tokens per turn | `hermes prompt-size` |
| **Compression settings** | How long sessions run before being summarized | `compression.threshold`, `target_ratio`, `protect_last_n` in config |
| **Session DB** | Actual messages, tool calls, token counts | SQLite sessions DB, JSON request dumps |
| **Cron jobs** | Scheduled invocations that consume tokens silently | `hermes cron list`, per-job schedule |
| **Provider logs** | Exact input/output tokens per request | Provider dashboards, request_dump JSONs |
| **Auth status** | Rate limits hit → indicates heavy use of that provider | `hermes auth list` |

## Methodology: Two Cross-Checking Runs

Always do **two independent estimates** and report the range. Single-method estimates have a 2–3× error band.

### Run A: Bottom-Up (per-component tier estimate)

Classify every turn into a tier and multiply:

| Tier | Definition | Typical Input | Typical Output |
|------|------------|---------------|----------------|
| **Light** | Q&A, 0–1 tool calls | 25K | 500 |
| **Medium** | 2–4 tool calls, basic search/read | 35K | 1.5K |
| **Heavy** | 5+ tools, vision, browser, web_extract | 80K | 3K |
| **Extreme** | Multi-agent delegation, large extract | 100K+ | 4K+ |

**Per-channel breakdown:**

```
Daily input  = Σ (turns_per_day × input_per_turn)  across all channels
Daily output = Σ (turns_per_day × output_per_turn) across all channels
```

Channels to enumerate:
- CLI commands (turns = CLI history count)
- Telegram/Discord/Slack bot messages (turns = incoming messages)
- Cron jobs (turns = schedule frequency, e.g., every minute × 180 = 180 runs)
- Failed/retried calls (turns = number of 429/5xx in logs)

### Run B: Top-Down (compression-signal sanity check)

Compression settings imply mid-session context size:

```
Context growth per turn ≈ previous + (input_this_turn + output_this_turn)
Compression triggers when context ≈ max_context × threshold
Average per-turn input during long session ≈ max_context × threshold / 2
```

Then:
```
Daily input  ≈ sessions_per_day × turns_per_session × avg_per_turn_input
Daily output ≈ sessions_per_day × turns_per_session × avg_per_turn_output
```

Cross-check inputs from Run A:
- `hygiene_hard_message_limit` → max messages per session
- `protect_last_n` → compression granularity
- `target_ratio` → how much survives compression

## Reporting Format

Always present **range + average**, never a single number:

| Method | Daily IN | Daily OUT | Monthly Total |
|--------|----------|-----------|---------------|
| Run A (bottom-up) | 2.59M | 0.09M | 80M |
| Run B (top-down) | 4.46M | 0.12M | 137M |
| Average | 3.52M | 0.10M | 109M |
| Range | 2.6–4.5M | 0.09–0.12M | 80–137M |

Then project costs across 3–4 representative models:

| Model | $/1M in | $/1M out | Monthly @ avg |
|-------|---------|----------|---------------|
| Cheapest viable | $0.066 | $0.20 | $X |
| Default (cheap tier) | $0.60 | $2.40 | $X |
| Mid-tier | $3.00 | $15.00 | $X |
| Premium | $5.00 | $25.00 | $X |

## Pitfalls

- **Don't fabricate usage data.** If you can't find a session DB, say so — extrapolate from observable signals instead, but flag the gap.
- **Baseline prompt dominates.** For tool-using agents, the system prompt + tool schemas (often 20–40K tokens) is the floor per turn. A "Light" turn that *only* answers a question still costs 20K+ tokens of input.
- **Cron jobs are silent killers.** A every-minute cron job = 1,440 runs/day. Even with minimal output, each run burns baseline + small input. Calculate their cost explicitly.
- **Compression makes context grow non-linearly.** A session at turn 10 has ~10× the input of turn 1. The "average per turn" in a long session is much higher than a short one.
- **Output tokens are 2–5× more expensive than input.** Don't underweight them.
- **Subscription models hide per-token cost.** A "free" tier user may actually have lower true usage than a pay-as-you-go user with rate limits.
- **Web extracts and vision add bulk fast.** A single `web_extract` of a 30KB page ≈ 7.5K input tokens. Vision adds ~1K per image.

## Cross-Validation Heuristics

If Run A and Run B differ by more than 3×, one of them is wrong. Common causes:

| Symptom | Likely cause |
|---------|-------------|
| Run A >> Run B | A is over-counting turns or over-estimating per-turn tokens |
| Run B >> Run A | B is assuming sessions are longer than they really are (check actual session_search results) |
| Both give implausibly large numbers | Baseline prompt is bigger than expected; check `hermes prompt-size` |

## Quick Estimate Cheat Sheet

For an unknown system, these rules of thumb get within 50%:

| Pattern | Daily tokens (rough) |
|---------|----------------------|
| Casual chat user (10–20 messages/day, simple Q&A) | 200K–500K |
| Power user with tool agent (50+ messages, mixed) | 2M–5M |
| Heavy automation (cron every minute + active use) | 3M–10M |
| Multi-agent pipeline (delegate_task + parallel) | 10M–50M+ |

## Worked Example: Hermes Agent

See `references/hermes-estimation-example.md` for a full worked example using bottom-up + top-down on a real Hermes install.