"""
╔══════════════════════════════════════════════════════╗
║           ✨ AURORA CALCULATOR ✨                    ║
║      A glassmorphism-inspired Python calculator      ║
║            Built with tkinter & love 💙              ║
╚══════════════════════════════════════════════════════╝

Requirements: Python 3.x (tkinter is included by default)
Run: python calculator.py
"""

import tkinter as tk
from tkinter import font as tkfont
import math
import time


# ── Colour Palette ─────────────────────────────────────────────────────────────
BG_DEEP        = "#0a0f2e"   # deep midnight blue (window bg)
BG_CARD        = "#0d1540"   # slightly lighter card bg
GLASS_FILL     = "#111d55"   # glass panel fill
GLASS_BORDER   = "#2a3a8a"   # glass border
DISPLAY_BG     = "#080d28"   # display area

BLUE_LIGHT     = "#a8c8ff"   # soft cool text
BLUE_MID       = "#5b9bf5"   # mid-tone blue
BLUE_GLOW      = "#4a7cf7"   # glow accent
BLUE_BRIGHT    = "#89d4ff"   # bright highlight
BLUE_ELECTRIC  = "#00b4ff"   # electric pop

WHITE          = "#e8f0ff"   # near-white text
MUTED          = "#4a5a90"   # muted text

BTN_NUM_BG     = "#131c52"   # number button bg
BTN_NUM_FG     = "#c0d8ff"   # number button text
BTN_NUM_HOV    = "#1a2768"   # hover

BTN_OP_BG      = "#0e2070"   # operator bg  (rich blue)
BTN_OP_FG      = "#89d4ff"   # operator text
BTN_OP_HOV     = "#1530a0"   # hover

BTN_SPEC_BG    = "#1a0e50"   # special (AC, ±, %) bg  (indigo)
BTN_SPEC_FG    = "#b8aaff"   # special text
BTN_SPEC_HOV   = "#281680"

BTN_EQ_BG      = "#0050cc"   # equals button (bright blue)
BTN_EQ_HOV     = "#0066ff"
BTN_EQ_FG      = "#ffffff"

SHADOW         = "#050a1e"


class AuroraCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aurora Calculator")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DEEP)

        # ── State ──────────────────────────────────────────────────────────────
        self.current     = "0"
        self.previous    = ""
        self.operator    = ""
        self.reset_next  = False
        self.history     = []
        self.anim_job    = None

        self._build_ui()
        self._bind_keyboard()
        self._animate_glow()

        # Center window
        self.root.update_idletasks()
        w, h = 400, 660
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI Construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # Outer glow frame
        outer = tk.Frame(self.root, bg=BLUE_GLOW, padx=1, pady=1)
        outer.pack(padx=18, pady=18, fill="both", expand=True)

        # Main card
        card = tk.Frame(outer, bg=GLASS_FILL, padx=0, pady=0)
        card.pack(fill="both", expand=True)

        # Title bar
        title_bar = tk.Frame(card, bg=BG_DEEP, height=36)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text="✦  AURORA  ✦",
                 bg=BG_DEEP, fg=BLUE_GLOW,
                 font=("Courier", 11, "bold"),
                 letter_spacing=4).pack(side="left", padx=16, pady=8)

        # Traffic light dots
        dots_frame = tk.Frame(title_bar, bg=BG_DEEP)
        dots_frame.pack(side="right", padx=14, pady=10)
        for color in ("#ff5f56", "#febc2e", "#28c840"):
            d = tk.Label(dots_frame, bg=color, width=2, height=1, relief="flat")
            d.pack(side="left", padx=3)

        # Display area
        disp_outer = tk.Frame(card, bg=GLASS_BORDER, padx=1, pady=1)
        disp_outer.pack(fill="x", padx=14, pady=(10, 4))

        disp_inner = tk.Frame(disp_outer, bg=DISPLAY_BG)
        disp_inner.pack(fill="x")

        # Expression label (small, shows previous + operator)
        self.expr_var = tk.StringVar(value="")
        tk.Label(disp_inner, textvariable=self.expr_var,
                 bg=DISPLAY_BG, fg=MUTED,
                 font=("Courier", 11),
                 anchor="e", padx=16).pack(fill="x", pady=(8, 0))

        # Main display
        self.display_var = tk.StringVar(value="0")
        self.display_lbl = tk.Label(
            disp_inner, textvariable=self.display_var,
            bg=DISPLAY_BG, fg=BLUE_BRIGHT,
            font=("Courier", 38, "bold"),
            anchor="e", padx=16, pady=6
        )
        self.display_lbl.pack(fill="x")

        # Unit hint
        self.unit_var = tk.StringVar(value="")
        tk.Label(disp_inner, textvariable=self.unit_var,
                 bg=DISPLAY_BG, fg=MUTED,
                 font=("Courier", 9),
                 anchor="e", padx=16).pack(fill="x", pady=(0, 8))

        # Separator
        tk.Frame(card, bg=GLASS_BORDER, height=1).pack(fill="x", padx=14, pady=4)

        # History strip
        self.hist_var = tk.StringVar(value="")
        tk.Label(card, textvariable=self.hist_var,
                 bg=GLASS_FILL, fg=MUTED,
                 font=("Courier", 9),
                 anchor="e").pack(fill="x", padx=20, pady=2)

        # Buttons grid
        btn_frame = tk.Frame(card, bg=GLASS_FILL)
        btn_frame.pack(padx=14, pady=(4, 14), fill="both", expand=True)

        # Button layout  [text, col, row, colspan, style]
        buttons = [
            # Row 0 – special
            ("AC",  0, 0, 1, "spec"),
            ("±",   1, 0, 1, "spec"),
            ("%",   2, 0, 1, "spec"),
            ("÷",   3, 0, 1, "op"),
            # Row 1
            ("7",   0, 1, 1, "num"),
            ("8",   1, 1, 1, "num"),
            ("9",   2, 1, 1, "num"),
            ("×",   3, 1, 1, "op"),
            # Row 2
            ("4",   0, 2, 1, "num"),
            ("5",   1, 2, 1, "num"),
            ("6",   2, 2, 1, "num"),
            ("−",   3, 2, 1, "op"),
            # Row 3
            ("1",   0, 3, 1, "num"),
            ("2",   1, 3, 1, "num"),
            ("3",   2, 3, 1, "num"),
            ("+",   3, 3, 1, "op"),
            # Row 4
            ("0",   0, 4, 2, "num"),   # wide zero
            (".",   2, 4, 1, "num"),
            ("=",   3, 4, 1, "eq"),
        ]

        for col in range(4):
            btn_frame.columnconfigure(col, weight=1, uniform="btn")
        for row in range(5):
            btn_frame.rowconfigure(row, weight=1, uniform="btn")

        for (text, col, row, span, style) in buttons:
            self._make_button(btn_frame, text, col, row, span, style)

    def _make_button(self, parent, text, col, row, colspan, style):
        styles = {
            "num":  (BTN_NUM_BG,  BTN_NUM_FG,  BTN_NUM_HOV),
            "op":   (BTN_OP_BG,   BTN_OP_FG,   BTN_OP_HOV),
            "spec": (BTN_SPEC_BG, BTN_SPEC_FG, BTN_SPEC_HOV),
            "eq":   (BTN_EQ_BG,   BTN_EQ_FG,   BTN_EQ_HOV),
        }
        bg, fg, hov = styles[style]

        # Outer glow wrapper
        glow_color = BLUE_GLOW if style == "eq" else GLASS_BORDER
        wrapper = tk.Frame(parent, bg=glow_color, padx=1, pady=1)
        wrapper.grid(row=row, column=col, columnspan=colspan,
                     sticky="nsew", padx=4, pady=4)

        btn = tk.Label(
            wrapper, text=text,
            bg=bg, fg=fg,
            font=("Courier", 18, "bold"),
            cursor="hand2",
            relief="flat",
        )
        btn.pack(fill="both", expand=True, ipadx=0, ipady=12)

        # Hover effects
        btn.bind("<Enter>",  lambda e, b=btn, h=hov, g=wrapper, gc=glow_color:
                             (b.config(bg=h), gc if style != "eq" else
                              wrapper.config(bg=BLUE_ELECTRIC)))
        btn.bind("<Leave>",  lambda e, b=btn, ob=bg, g=wrapper, gc=glow_color:
                             (b.config(bg=ob), wrapper.config(bg=gc)))
        btn.bind("<Button-1>", lambda e, t=text: self._on_click(t))

        # Press animation
        btn.bind("<ButtonPress-1>",   lambda e, b=btn, ob=bg:
                                       b.config(bg=BLUE_ELECTRIC if style == "eq" else BLUE_MID,
                                                fg=WHITE))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn, ob=bg, of=fg:
                                       b.config(bg=ob, fg=of))

    # ── Logic ──────────────────────────────────────────────────────────────────

    def _on_click(self, text):
        if text == "AC":
            self._clear_all()
        elif text == "±":
            self._toggle_sign()
        elif text == "%":
            self._percentage()
        elif text == "=":
            self._calculate()
        elif text in ("÷", "×", "−", "+"):
            self._set_operator(text)
        elif text == ".":
            self._add_decimal()
        else:
            self._add_digit(text)

        self._refresh_display()

    def _add_digit(self, d):
        if self.reset_next:
            self.current   = d
            self.reset_next = False
        elif self.current == "0":
            self.current = d
        else:
            if len(self.current) < 12:
                self.current += d

    def _add_decimal(self):
        if self.reset_next:
            self.current    = "0."
            self.reset_next = False
            return
        if "." not in self.current:
            self.current += "."

    def _set_operator(self, op):
        if self.operator and not self.reset_next:
            self._calculate(chain=True)
        self.previous    = self.current
        self.operator    = op
        self.reset_next  = True

    def _calculate(self, chain=False):
        if not self.operator or not self.previous:
            return
        try:
            a = float(self.previous)
            b = float(self.current)
            op = self.operator
            if   op == "+": result = a + b
            elif op == "−": result = a - b
            elif op == "×": result = a * b
            elif op == "÷":
                if b == 0:
                    self._show_error("÷ 0  undefined")
                    return
                result = a / b
            else:
                return

            # Format result cleanly
            if result == int(result) and abs(result) < 1e12:
                result_str = str(int(result))
            else:
                result_str = f"{result:.8g}"

            # History
            expr = f"{self._fmt(a)} {op} {self._fmt(b)} = {result_str}"
            self.history.append(expr)
            if len(self.history) > 3:
                self.history.pop(0)
            self.hist_var.set("  |  ".join(self.history[-2:]))

            self.expr_var.set(f"{self._fmt(a)} {op} {self._fmt(b)} =")
            self.current    = result_str
            self.previous   = result_str if chain else ""
            self.operator   = "" if not chain else self.operator
            self.reset_next = not chain

            self._flash_display()

        except Exception:
            self._show_error("Error")

    def _fmt(self, n):
        return str(int(n)) if n == int(n) else str(n)

    def _clear_all(self):
        self.current    = "0"
        self.previous   = ""
        self.operator   = ""
        self.reset_next = False
        self.expr_var.set("")
        self.unit_var.set("")

    def _toggle_sign(self):
        if self.current not in ("0", ""):
            if self.current.startswith("-"):
                self.current = self.current[1:]
            else:
                self.current = "-" + self.current

    def _percentage(self):
        try:
            val = float(self.current) / 100
            self.current = f"{val:.8g}"
        except Exception:
            pass

    def _show_error(self, msg):
        self.current    = msg
        self.operator   = ""
        self.previous   = ""
        self.reset_next = True
        self.display_var.set(msg)
        self.display_lbl.config(fg="#ff6b6b")
        self.root.after(1200, lambda: self.display_lbl.config(fg=BLUE_BRIGHT))
        self.root.after(1200, self._clear_all)

    def _refresh_display(self):
        # Auto-shrink font for long numbers
        txt = self.current
        fsize = 38 if len(txt) <= 9 else max(20, 38 - (len(txt) - 9) * 3)
        self.display_lbl.config(font=("Courier", fsize, "bold"))
        self.display_var.set(txt)

        # Show operator in expr label
        if self.operator and self.previous:
            self.expr_var.set(f"{self.previous}  {self.operator}")
        elif not self.operator:
            pass  # keep last expr shown after equals

    def _flash_display(self):
        """Quick colour flash on equals result."""
        self.display_lbl.config(fg=BLUE_ELECTRIC)
        self.root.after(180, lambda: self.display_lbl.config(fg=BLUE_BRIGHT))

    # ── Keyboard ───────────────────────────────────────────────────────────────

    def _bind_keyboard(self):
        bindings = {
            "0":"0","1":"1","2":"2","3":"3","4":"4",
            "5":"5","6":"6","7":"7","8":"8","9":"9",
            ".":".", "+":"+", "-":"−", "*":"×", "/":"÷",
            "Return":"=", "KP_Enter":"=",
            "BackSpace":"AC", "Escape":"AC", "percent":"%",
        }
        for key, val in bindings.items():
            self.root.bind(f"<{key}>", lambda e, v=val: self._on_click(v))

    # ── Ambient glow animation ─────────────────────────────────────────────────

    def _animate_glow(self):
        """Slowly cycle the outer glow border colour for ambient effect."""
        colors = [
            "#2a5af5", "#2a3ff5", "#3a2af5", "#5a2af5",
            "#2a5af5", "#2a7af5", "#2a9af5", "#2a7af5",
        ]
        self._glow_step = getattr(self, "_glow_step", 0)

        outer = self.root.winfo_children()[0]   # outer glow frame
        try:
            outer.config(bg=colors[self._glow_step % len(colors)])
        except Exception:
            pass

        self._glow_step += 1
        self.root.after(600, self._animate_glow)

    # ── Run ────────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AuroraCalculator()
    app.run()
