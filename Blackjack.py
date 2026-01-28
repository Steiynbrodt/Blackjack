import random
import tkinter as tk
from tkinter import messagebox

# ----------------------------
# Blackjack (Tkinter, single file)
# ----------------------------

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♠", "♥", "♦", "♣"]
SUIT_COLOR = {"♠": "#e6e6e6", "♣": "#e6e6e6", "♥": "#ff5a5a", "♦": "#ff5a5a"}

# Payout rules (simple):
# - Win: +bet
# - Blackjack (A+10 on first 2 cards) win: +1.5 * bet (rounded down)
# - Push: 0
# - Lose: -bet
# - Bust: lose bet
# Dealer stands on all 17 (including soft 17)


def make_shoe(decks=4):
    shoe = [(r, s) for _ in range(decks) for s in SUITS for r in RANKS]
    random.shuffle(shoe)
    return shoe


def card_str(card):
    r, s = card
    return f"{r}{s}"


def hand_value(cards):
    # Returns (best_value, is_soft)
    total = 0
    aces = 0
    for r, _ in cards:
        if r == "A":
            aces += 1
            total += 11
        elif r in ("K", "Q", "J"):
            total += 10
        else:
            total += int(r)

    # downgrade aces from 11 to 1 as needed
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    # soft if any ace still counted as 11
    is_soft = any(r == "A" for r, _ in cards) and (sum(11 if r == "A" else (10 if r in ("K", "Q", "J") else int(r)) for r, _ in cards) != total)
    # The soft check above is approximate; for UI it's fine, but we can do a clearer one:
    # Soft is true if there exists an ace counted as 11 in the final total.
    # We'll recompute:
    base = 0
    aces_total = 0
    for r, _ in cards:
        if r == "A":
            aces_total += 1
        elif r in ("K", "Q", "J"):
            base += 10
        else:
            base += int(r)
    # If we can add 11 for one ace without busting, it's soft (with remaining aces as 1)
    is_soft = False
    if aces_total > 0:
        if base + 11 + (aces_total - 1) * 1 <= 21:
            is_soft = True

    return total, is_soft


def is_blackjack(cards):
    if len(cards) != 2:
        return False
    v, _ = hand_value(cards)
    return v == 21


class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack — Chips Only (No Real Money)")

        self.bg = "#121212"
        self.fg = "#e6e6e6"
        self.muted = "#a8a8a8"
        self.btn_bg = "#1f1f1f"
        self.btn_fg = "#e6e6e6"
        self.accent = "#67d7ff"

        self.root.configure(bg=self.bg)
        self.root.resizable(False, False)

        # Game state
        self.chips = 200
        self.bet = 10
        self.shoe = make_shoe(decks=4)
        self.cut_card_at = 40  # reshuffle when shoe low

        self.player = []
        self.dealer = []
        self.in_round = False
        self.player_stood = False
        self.round_over = False
        self.reveal_dealer = False
        self.allow_double = False

        self._build_ui()
        self._refresh_ui()
        self._set_message("Welcome! Set a bet and press Deal. 🎩")

    # ---------- UI ----------
    def _build_ui(self):
        pad = 10

        top = tk.Frame(self.root, bg=self.bg)
        top.pack(padx=pad, pady=(pad, 0), fill="x")

        self.lbl_title = tk.Label(
            top,
            text="♠ Blackjack ♣  (chips only, for laughs)",
            bg=self.bg,
            fg=self.fg,
            font=("Segoe UI", 14, "bold"),
        )
        self.lbl_title.pack(anchor="w")

        info = tk.Frame(self.root, bg=self.bg)
        info.pack(padx=pad, pady=(6, 0), fill="x")

        self.lbl_chips = tk.Label(info, text="", bg=self.bg, fg=self.fg, font=("Segoe UI", 11))
        self.lbl_chips.pack(side="left")

        self.lbl_bet = tk.Label(info, text="", bg=self.bg, fg=self.fg, font=("Segoe UI", 11))
        self.lbl_bet.pack(side="right")

        # Table area
        table = tk.Frame(self.root, bg=self.bg)
        table.pack(padx=pad, pady=pad, fill="x")

        # Dealer
        self.dealer_title = tk.Label(table, text="Dealer", bg=self.bg, fg=self.muted, font=("Segoe UI", 11, "bold"))
        self.dealer_title.grid(row=0, column=0, sticky="w")

        self.dealer_cards_frame = tk.Frame(table, bg=self.bg)
        self.dealer_cards_frame.grid(row=1, column=0, sticky="w")

        self.lbl_dealer_value = tk.Label(table, text="", bg=self.bg, fg=self.muted, font=("Segoe UI", 10))
        self.lbl_dealer_value.grid(row=2, column=0, sticky="w", pady=(2, 10))

        # Player
        self.player_title = tk.Label(table, text="You", bg=self.bg, fg=self.muted, font=("Segoe UI", 11, "bold"))
        self.player_title.grid(row=3, column=0, sticky="w")

        self.player_cards_frame = tk.Frame(table, bg=self.bg)
        self.player_cards_frame.grid(row=4, column=0, sticky="w")

        self.lbl_player_value = tk.Label(table, text="", bg=self.bg, fg=self.muted, font=("Segoe UI", 10))
        self.lbl_player_value.grid(row=5, column=0, sticky="w", pady=(2, 0))

        # Message
        self.lbl_msg = tk.Label(
            self.root,
            text="",
            bg=self.bg,
            fg=self.accent,
            font=("Segoe UI", 10),
            wraplength=520,
            justify="left",
        )
        self.lbl_msg.pack(padx=pad, pady=(0, pad), anchor="w")

        # Controls
        controls = tk.Frame(self.root, bg=self.bg)
        controls.pack(padx=pad, pady=(0, pad), fill="x")

        # Bet controls
        bet_box = tk.Frame(controls, bg=self.bg)
        bet_box.pack(side="left")

        self.btn_bet_minus = tk.Button(bet_box, text="−", width=3, command=lambda: self.change_bet(-10))
        self.btn_bet_minus.grid(row=0, column=0, padx=(0, 4))

        self.btn_bet_plus = tk.Button(bet_box, text="+", width=3, command=lambda: self.change_bet(+10))
        self.btn_bet_plus.grid(row=0, column=1, padx=(0, 10))

        self.btn_all_in = tk.Button(bet_box, text="All-in (kinda)", command=self.all_in)
        self.btn_all_in.grid(row=0, column=2, padx=(0, 10))

        # Action buttons
        actions = tk.Frame(controls, bg=self.bg)
        actions.pack(side="right")

        self.btn_deal = tk.Button(actions, text="Deal", width=10, command=self.deal)
        self.btn_hit = tk.Button(actions, text="Hit", width=10, command=self.hit)
        self.btn_stand = tk.Button(actions, text="Stand", width=10, command=self.stand)
        self.btn_double = tk.Button(actions, text="Double", width=10, command=self.double_down)
        self.btn_new = tk.Button(actions, text="New Round", width=10, command=self.new_round)

        self.btn_deal.grid(row=0, column=0, padx=4)
        self.btn_hit.grid(row=0, column=1, padx=4)
        self.btn_stand.grid(row=0, column=2, padx=4)
        self.btn_double.grid(row=0, column=3, padx=4)
        self.btn_new.grid(row=0, column=4, padx=4)

        # Style buttons
        for b in [
            self.btn_bet_minus, self.btn_bet_plus, self.btn_all_in,
            self.btn_deal, self.btn_hit, self.btn_stand, self.btn_double, self.btn_new
        ]:
            b.configure(
                bg=self.btn_bg,
                fg=self.btn_fg,
                activebackground="#2a2a2a",
                activeforeground=self.btn_fg,
                relief="flat",
                padx=8,
                pady=6,
                highlightthickness=0,
                bd=0,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )

    def _set_message(self, text):
        self.lbl_msg.config(text=text)

    def _draw_cards(self, parent, cards, hide_first=False):
        for w in parent.winfo_children():
            w.destroy()

        for i, (r, s) in enumerate(cards):
            if hide_first and i == 0:
                txt = "🂠"
                fg = self.muted
            else:
                txt = f"{r}{s}"
                fg = SUIT_COLOR.get(s, self.fg)

            card = tk.Label(
                parent,
                text=txt,
                bg="#1a1a1a",
                fg=fg,
                font=("Segoe UI", 20, "bold"),
                width=4,
                height=2,
                relief="ridge",
                bd=2,
            )
            card.pack(side="left", padx=4, pady=2)

    def _refresh_ui(self):
        self.lbl_chips.config(text=f"Chips: {self.chips}")
        self.lbl_bet.config(text=f"Bet: {self.bet}")

        # Dealer view
        if self.in_round and not self.reveal_dealer:
            # show only dealer upcard value
            up = self.dealer[1:] if len(self.dealer) > 1 else []
            up_val = hand_value(up)[0] if up else 0
            self._draw_cards(self.dealer_cards_frame, self.dealer, hide_first=True)
            self.lbl_dealer_value.config(text=f"Dealer shows: {up_val} (and something mysterious)")
        else:
            self._draw_cards(self.dealer_cards_frame, self.dealer, hide_first=False)
            dv = hand_value(self.dealer)[0] if self.dealer else 0
            soft = " (soft)" if self.dealer and hand_value(self.dealer)[1] else ""
            self.lbl_dealer_value.config(text=f"Dealer total: {dv}{soft}" if self.dealer else "")

        # Player view
        self._draw_cards(self.player_cards_frame, self.player, hide_first=False)
        pv = hand_value(self.player)[0] if self.player else 0
        softp = " (soft)" if self.player and hand_value(self.player)[1] else ""
        self.lbl_player_value.config(text=f"Your total: {pv}{softp}" if self.player else "")

        # Enable/disable buttons
        can_bet = not self.in_round
        self.btn_bet_minus.config(state=("normal" if can_bet else "disabled"))
        self.btn_bet_plus.config(state=("normal" if can_bet else "disabled"))
        self.btn_all_in.config(state=("normal" if can_bet else "disabled"))

        self.btn_deal.config(state=("normal" if (not self.in_round and self.chips > 0) else "disabled"))
        self.btn_hit.config(state=("normal" if self.in_round and not self.round_over else "disabled"))
        self.btn_stand.config(state=("normal" if self.in_round and not self.round_over else "disabled"))
        self.btn_double.config(state=("normal" if self.in_round and self.allow_double and not self.round_over else "disabled"))
        self.btn_new.config(state=("normal" if self.round_over else "disabled"))

    # ---------- Game logic ----------
    def _ensure_shoe(self):
        if len(self.shoe) < self.cut_card_at:
            self.shoe = make_shoe(decks=4)
            self._set_message("🔄 Reshuffled the shoe. Fresh chaos deployed.")

    def _draw(self):
        self._ensure_shoe()
        return self.shoe.pop()

    def clamp_bet(self):
        if self.bet < 1:
            self.bet = 1
        if self.bet > max(1, self.chips):
            self.bet = max(1, self.chips)

    def change_bet(self, delta):
        if self.in_round:
            return
        self.bet += delta
        self.clamp_bet()
        self._refresh_ui()

    def all_in(self):
        if self.in_round:
            return
        self.bet = max(1, self.chips)
        self._refresh_ui()

    def deal(self):
        if self.in_round:
            return
        if self.chips <= 0:
            messagebox.showinfo("No chips", "You have no chips left. Reset the app to magically get more.")
            return

        self.clamp_bet()
        if self.bet > self.chips:
            self.bet = self.chips

        self.player = [self._draw(), self._draw()]
        self.dealer = [self._draw(), self._draw()]
        self.in_round = True
        self.round_over = False
        self.reveal_dealer = False
        self.player_stood = False
        self.allow_double = True  # allowed only immediately after deal

        self._set_message("Cards dealt. Try not to anger the Dealer Bot 3000.")

        # Immediate blackjack checks
        p_bj = is_blackjack(self.player)
        d_bj = is_blackjack(self.dealer)

        if p_bj or d_bj:
            self.reveal_dealer = True
            if p_bj and d_bj:
                self._end_round("push", "🟰 Double blackjack. The universe shrugs.")
            elif p_bj:
                self._end_round("blackjack", "✨ BLACKJACK! You win with maximum style.")
            else:
                self._end_round("lose", "💀 Dealer has blackjack. You have… character development.")
        else:
            self._refresh_ui()

    def hit(self):
        if not self.in_round or self.round_over:
            return
        self.player.append(self._draw())
        self.allow_double = False

        pv = hand_value(self.player)[0]
        if pv > 21:
            self.reveal_dealer = True
            self._end_round("bust", "💥 Bust! You exceeded 21. The cards are judging you.")
        else:
            self._set_message(random.choice([
                "You hit. Bold.",
                "You hit. The tension intensifies.",
                "You hit. Somewhere, a mathematician sighs.",
                "You hit. Fortune spins its tiny mustache."
            ]))
            self._refresh_ui()

    def stand(self):
        if not self.in_round or self.round_over:
            return
        self.player_stood = True
        self.allow_double = False
        self.reveal_dealer = True
        self._dealer_play_and_settle()

    def double_down(self):
        if not self.in_round or self.round_over or not self.allow_double:
            return
        if self.bet >= self.chips:
            self._set_message("You can’t double — not enough chips. Tragic.")
            self._refresh_ui()
            return

        self.bet *= 2
        self.allow_double = False
        self._set_message("DOUBLE DOWN! One card only. Dramatic music plays in the distance...")
        self.player.append(self._draw())

        pv = hand_value(self.player)[0]
        if pv > 21:
            self.reveal_dealer = True
            self._end_round("bust", "💥 Double-down bust! That was a brave (questionable) choice.")
        else:
            self.reveal_dealer = True
            self._dealer_play_and_settle()

    def _dealer_play_and_settle(self):
        # Dealer draws until 17+
        while True:
            dv, _ = hand_value(self.dealer)
            if dv < 17:
                self.dealer.append(self._draw())
            else:
                break

        pv = hand_value(self.player)[0]
        dv = hand_value(self.dealer)[0]

        if dv > 21:
            self._end_round("win", "🔥 Dealer busts! You win. Please accept this imaginary trophy: 🏆")
        elif pv > dv:
            self._end_round("win", f"✅ You win! {pv} beats {dv}.")
        elif pv < dv:
            self._end_round("lose", f"❌ You lose. {dv} beats {pv}. Dealer smirks in binary.")
        else:
            self._end_round("push", f"🟰 Push. {pv} ties {dv}. Nobody wins (except suspense).")

    def _end_round(self, result, msg):
        # Adjust chips based on result
        if result == "blackjack":
            gain = (self.bet * 3) // 2  # 1.5x bet, rounded down
            self.chips += gain
            msg += f"  (+{gain} chips)"
        elif result == "win":
            self.chips += self.bet
            msg += f"  (+{self.bet} chips)"
        elif result == "push":
            msg += "  (+0 chips)"
        else:
            # lose / bust
            self.chips -= self.bet
            msg += f"  (-{self.bet} chips)"

        self.round_over = True
        self.in_round = True  # still in round until New Round pressed
        self.allow_double = False

        if self.chips <= 0:
            self.chips = 0
            msg += "\n🪦 You’re out of chips. The dealer offers you a coupon for emotional support."

        self._set_message(msg)
        self._refresh_ui()

    def new_round(self):
        if not self.round_over:
            return
        self.in_round = False
        self.round_over = False
        self.reveal_dealer = False
        self.player_stood = False
        self.allow_double = False
        self.player = []
        self.dealer = []

        self.clamp_bet()

        if self.chips <= 0:
            # Give a tiny "freebie" so the game doesn't dead-end (still no money involved).
            self.chips = 50
            self.bet = 10
            self._set_message("🧙 A mysterious wizard gifts you 50 pity-chips. Press Deal.")
        else:
            self._set_message("New round ready. Press Deal to tempt fate again.")

        self._refresh_ui()


if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()
