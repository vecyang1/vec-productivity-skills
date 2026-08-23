# Catch-Up, Retry & Credit

A scheduler trigger can be missed — the machine slept, the network was down, you woke up late. What the task does *after* a miss should be a deliberate choice in the cadence card, not an accident of when the runtime happened to fire.

## Catch-Up Policy

| Policy | Behavior | Use for |
|---|---|---|
| `cheap_window_only` | Only run inside the allowed (cheap) window. A missed run does **not** fire later. | Expensive, non-urgent work (digests, reindexing, batch summaries) |
| `catch_up_when_awake` | Run the missed job when the machine/agent next wakes, even if late. | Sync, health checks, ops where lateness is still valuable |
| `skip_if_stale` | Skip entirely if too much time has passed (see `Max Catch Up Age Hours`). | Tasks where a late run would mislead |
| `manual_review` | Surface the miss; let a human decide. | High-side-effect or financial tasks |

### The midnight-credit trap

If an expensive job is scheduled for 2 AM to use a cheaper/quieter credit window and the machine was asleep, a naive `catch_up_when_awake` will fire it at, say, 9 AM — burning your **daytime** credit on work that was supposed to be cheap.

For that class of job, pin it down:

```yaml
Preferred Window: midnight_credit
Credit Policy: prefer_midnight_5h_cap
Catch Up Policy: cheap_window_only
```

Now a missed 2 AM run is simply skipped until the next cheap window. Use `catch_up_when_awake` **only** when a late run is genuinely still worth the daytime cost.

## Retry Policy

| Policy | Behavior |
|---|---|
| `retry_until_success` | Keep retrying on the `Retry Interval Minutes` cadence until a success marker is written |
| `retry_3_times` | Bounded retries, then stop and surface |
| `no_retry` | One attempt; failure waits for the next scheduled run |
| `manual_review` | Do not auto-retry; flag for a human |

Pair with:

- `Retry Interval Minutes` — spacing between retries.
- `Max Catch Up Age Hours` — how stale a missed run may be before `skip_if_stale` / `manual_review` kicks in.
- `Stale After Hours` — when the output itself should be treated as stale.

## Preferred Window & Credit

| `Preferred Window` | Meaning |
|---|---|
| `midnight_credit` | Run in the cheap/quiet overnight window |
| `morning_review` | Run when a human is around to review output |
| `business_hours` | Run during the working day |
| `anytime` | No timing preference |

| `Credit Policy` | Meaning |
|---|---|
| `prefer_midnight_5h_cap` | Prefer overnight credit; respect a capped window |
| `normal` | No special credit handling |
| `no_ai_credit` | Must not consume metered AI credit (pure local work) |

## Idempotency Is The Backstop

Catch-up policy reduces *when* a duplicate run can happen; **idempotency** is what makes a duplicate run safe when it does. The incremental loop guarantees it:

1. read checkpoint + success marker,
2. detect inputs changed since `last_success_at` / `last_cursor` / `input_signature`,
3. no-op with a receipt if nothing changed,
4. update the output owner first,
5. write the success marker only after the owner is safely updated.

A task that re-runs and finds no changed inputs should cost almost nothing and change nothing. If a second run within the same period would double-write, the task is not yet idempotent — fix that before relaxing the catch-up policy.
