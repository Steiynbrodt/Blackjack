
---

# ♠ Blackjack — Tkinter Edition (Chips Only)

A small, self-contained Blackjack game written in pure Python with Tkinter.

No assets.
No dependencies.
No real money.
Just cards, chips, and questionable decisions.

This is a single-file project meant to be easy to read, easy to run, and easy to tinker with.

---

## Features

* Classic Blackjack rules
* 4-deck shoe with reshuffle (cut card)
* Dealer stands on **all 17** (including soft 17)
* Blackjack pays **3:2**
* Double down supported
* Chip system (starts at 200)
* Friendly UI with visible hand values (soft/hard shown)
* Zero external libraries

It’s designed to feel like a real table, minus the cigarette smoke and financial regret.

---

## Requirements

* Python 3.8+
* Tkinter (comes with standard Python on most systems)

No pip installs required.

---

## Run

```bash
python blackjack.py
```

That’s it.

---

## Rules Implemented

| Situation           | Result                    |
| ------------------- | ------------------------- |
| Normal win          | +bet                      |
| Blackjack (2 cards) | +1.5 × bet (rounded down) |
| Push                | 0                         |
| Lose / Bust         | −bet                      |
| Dealer rule         | Stands on all 17          |

Double down:

* Only immediately after the deal
* One card only
* Bet is doubled

---

## Controls

* **+ / −** adjust bet
* **All-in** sets bet to current chips
* **Deal** starts the round
* **Hit / Stand / Double** during the round
* **New Round** resets the table after a result

If you run out of chips, the game gives you a small pity refill so you’re not soft-locked.

Because this is for fun, not punishment.

---

## Project Goals

This project is intentionally:

* Single file
* Readable
* Hackable
* UI-first
* Logic kept simple and explicit

It’s a good little example of how to build a complete interactive app with Tkinter without turning it into a spaghetti mess.

---

## Hacking Ideas

Easy things to add if you feel like tinkering:

* Split hands
* Insurance
* Sound effects
* Card counting stats
* Animations
* Persistent chips between runs
* Configurable deck count / rules

The structure is simple on purpose so changes don’t hurt.

---

## Disclaimer

No real money.
No gambling logic beyond basic Blackjack rules.
No strategy advice included. You’re on your own there.

---

## Screenshot
<img width="1531" height="626" alt="image" src="https://github.com/user-attachments/assets/640c1dd8-dfbe-4acb-864b-f239daca3db3" />

<img width="1519" height="965" alt="image" src="https://github.com/user-attachments/assets/c747d512-4e29-40cf-b231-e470f0e775d0" />



---

Have fun. Try not to bust on 12.
