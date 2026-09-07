"""
=============================================================================
NUVI - Desktop Pet Assistant UI Widget
=============================================================================
Features:
- Transparent animated desktop pet on Windows.
- Event-based reactions (greet, listen, think, success, error).
- Compact status speech bubbles for rapid state feedback (listening, heard).
- Extended, scrollable Answer Window for questions, explanations, and data analysis:
  * Persistent display: waits for user acknowledgement ("okay", "done", "thank you")
  * Selectable and copyable text with dedicated "📋 Copy" button
  * Draggable by header bar
  * Smooth native scrollbar for lengthy AI answers or datasets.
=============================================================================
"""

import math
import os
import queue
import re
import threading
import tkinter as tk

from PIL import Image, ImageTk


class AssistantWidget(tk.Tk):
    """
    Transparent desktop pet with voice recognition, non-blocking animations,
    and a dedicated scrollable Answer Card for informational queries.
    """

    PET_SIZE = 96
    WINDOW_W = 270
    WINDOW_H = 190
    TRANSPARENT = "#010101"
    PET_CENTER_X = 135
    PET_CENTER_Y = 125

    def __init__(self, command_callback):
        super().__init__()

        self.command_callback = command_callback
        self.title("NUVI Desktop Assistant")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", self.TRANSPARENT)
        self.configure(bg=self.TRANSPARENT)

        self._drag_x = 0
        self._drag_y = 0
        self._busy = False
        self._dragging = False
        self._motion_job = None
        self._busy_job = None
        self._bubble_job = None
        self._result_queue = queue.Queue()

        # Answer Window State
        self.answer_window = None
        self.answer_text = None
        self.answer_copy_btn = None
        self._card_drag_x = 0
        self._card_drag_y = 0
        self._waiting_for_acknowledgement = False

        # Two-Way Chatbox State (3-Click trigger)
        self._click_job = None
        self.chat_window = None
        self.chat_text = None
        self.chat_entry = None
        self._chat_drag_x = 0
        self._chat_drag_y = 0

        self._frames = {}
        self._static_frame = None
        self.pet_id = None
        self.shadow_id = None
        self.bubble_id = None
        self.text_id = None

        self._place_window()
        self._build_canvas()
        self._load_pet_frames()
        self._draw_pet(self._static_frame)
        self._bind_interactions()

        self.after(100, self._drain_results)
        self.after(700, lambda: self._show_bubble("2 clicks: Speak 🎙️\n3 clicks: Chat 💬", auto_hide=3500))

    def _place_window(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() - self.WINDOW_W - 24
        y = self.winfo_screenheight() - self.WINDOW_H - 70
        self.geometry(f"{self.WINDOW_W}x{self.WINDOW_H}+{x}+{y}")

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self,
            width=self.WINDOW_W,
            height=self.WINDOW_H,
            bg=self.TRANSPARENT,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_interactions(self):
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Triple-Button-1>", self._on_triple_click)
        self.canvas.bind("<Enter>", lambda _event: self._play_motion("greet"))
        self.canvas.bind("<Leave>", lambda _event: self._hide_bubble(delay=1200))
        self.canvas.bind("<Button-3>", lambda _event: self._show_bubble("2 clicks: Speak 🎙️ • 3 clicks: Chat 💬", auto_hide=4000))

    def _on_double_click(self, _event=None):
        """Debounced 2-click handler for voice input."""
        if self._click_job:
            self.after_cancel(self._click_job)
        self._click_job = self.after(300, self._start_voice)

    def _on_triple_click(self, _event=None):
        """3-click handler to open the two-way interactive text Chatbox."""
        if self._click_job:
            self.after_cancel(self._click_job)
            self._click_job = None
        self._toggle_chat_window()

    def _load_pet_frames(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        png_path = os.path.join(base_dir, "pet.gif")

        if os.path.exists(png_path):
            source = Image.open(png_path).convert("RGBA")
        else:
            source = self._fallback_pet_image()

        source.thumbnail((self.PET_SIZE, self.PET_SIZE), Image.LANCZOS)
        self._static_frame = ImageTk.PhotoImage(source)
        self._frames = {
            "greet": self._make_motion_frames(source, count=12, bounce=4, tilt=5, squash=0.025),
            "listen": self._make_motion_frames(source, count=18, bounce=6, tilt=3, squash=0.035),
            "think": self._make_motion_frames(source, count=20, bounce=3, tilt=7, squash=0.02),
            "success": self._make_motion_frames(source, count=14, bounce=8, tilt=4, squash=0.045),
            "error": self._make_motion_frames(source, count=10, bounce=1, tilt=10, squash=0.01),
        }

    def _fallback_pet_image(self):
        image = Image.new("RGBA", (self.PET_SIZE, self.PET_SIZE), (0, 0, 0, 0))
        import PIL.ImageDraw as ImageDraw

        draw = ImageDraw.Draw(image)
        cx = self.PET_SIZE // 2
        cy = self.PET_SIZE // 2
        draw.ellipse((cx - 34, cy - 31, cx + 34, cy + 34), fill="#ffd86b", outline="#f3a928", width=3)
        draw.ellipse((cx - 13, cy - 10, cx - 6, cy - 3), fill="#2f241c")
        draw.ellipse((cx + 6, cy - 10, cx + 13, cy - 3), fill="#2f241c")
        draw.polygon((cx - 7, cy + 7, cx + 7, cy + 7, cx, cy + 15), fill="#ff8a3d")
        return image

    def _make_motion_frames(self, source, *, count, bounce, tilt, squash):
        frames = []
        for index in range(count):
            t = index / max(count - 1, 1)
            wave = math.sin(t * math.pi)
            wobble = math.sin(t * math.pi * 2)
            scale_x = 1.0 + squash * wave
            scale_y = 1.0 - squash * wave
            width = max(1, int(source.width * scale_x))
            height = max(1, int(source.height * scale_y))
            sprite = source.resize((width, height), Image.LANCZOS)
            sprite = sprite.rotate(tilt * wobble, resample=Image.BICUBIC, expand=True)

            canvas = Image.new("RGBA", (self.PET_SIZE + 28, self.PET_SIZE + 28), (0, 0, 0, 0))
            x = (canvas.width - sprite.width) // 2
            y = (canvas.height - sprite.height) // 2 - int(bounce * wave)
            canvas.paste(sprite, (x, y), sprite)
            frames.append(ImageTk.PhotoImage(canvas))
        return frames

    def _draw_pet(self, frame):
        if self.shadow_id is None:
            self.shadow_id = self.canvas.create_oval(95, 158, 175, 171, fill="#000000", outline="", stipple="gray50")
        if self.pet_id is None:
            self.pet_id = self.canvas.create_image(self.PET_CENTER_X, self.PET_CENTER_Y, image=frame)
        else:
            self.canvas.itemconfig(self.pet_id, image=frame)

    def _play_motion(self, name, *, loop=False, on_done=None):
        if self._motion_job:
            self.after_cancel(self._motion_job)
            self._motion_job = None

        frames = self._frames.get(name) or []
        if not frames:
            if on_done:
                on_done()
            return

        def step(index=0):
            self._draw_pet(frames[index])
            next_index = index + 1
            if next_index < len(frames):
                self._motion_job = self.after(33, lambda: step(next_index))
            elif loop:
                self._motion_job = self.after(33, lambda: step(0))
            else:
                self._draw_pet(self._static_frame)
                self._motion_job = None
                if on_done:
                    on_done()

        step()

    def _start_busy_motion(self, name):
        self._stop_busy_motion()

        def pulse():
            if not self._busy:
                self._draw_pet(self._static_frame)
                return
            self._play_motion(name, on_done=pulse)

        pulse()

    def _stop_busy_motion(self):
        if self._busy_job:
            self.after_cancel(self._busy_job)
            self._busy_job = None

    # =========================================================================
    # Small Status Bubble (For Quick States: "Listening...", "Heard: ...")
    # =========================================================================
    def _show_bubble(self, text, *, auto_hide=None):
        self._cancel_bubble_timer()
        display = text if len(text) <= 150 else text[:147] + "..."
        lines = self._wrap_text(display, limit=36)
        height = 28 + (len(lines) - 1) * 15
        y2 = 18 + height

        if self.bubble_id is None:
            self.bubble_id = self._rounded_rect(18, 12, 252, y2, radius=13, fill="#fff8dc", outline="#e7d7a8")
            self.text_id = self.canvas.create_text(
                135,
                24,
                text="\n".join(lines),
                fill="#362717",
                font=("Segoe UI", 9),
                width=220,
                justify="center",
                anchor="n",
            )
        else:
            self._update_rounded_rect(self.bubble_id, 18, 12, 252, y2, radius=13)
            self.canvas.itemconfig(self.text_id, text="\n".join(lines))
            self.canvas.itemconfig(self.bubble_id, state=tk.NORMAL)
            self.canvas.itemconfig(self.text_id, state=tk.NORMAL)

        self.canvas.tag_raise(self.bubble_id)
        self.canvas.tag_raise(self.text_id)

        if auto_hide:
            self._bubble_job = self.after(auto_hide, self._hide_bubble)

    def _hide_bubble(self, delay=0):
        self._cancel_bubble_timer()
        if delay:
            self._bubble_job = self.after(delay, self._hide_bubble)
            return
        if self.bubble_id is not None:
            self.canvas.itemconfig(self.bubble_id, state=tk.HIDDEN)
            self.canvas.itemconfig(self.text_id, state=tk.HIDDEN)

    def _cancel_bubble_timer(self):
        if self._bubble_job:
            self.after_cancel(self._bubble_job)
            self._bubble_job = None

    def _wrap_text(self, text, *, limit):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > limit and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines or [""]

    def _rounded_rect(self, x1, y1, x2, y2, *, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def _update_rounded_rect(self, item_id, x1, y1, x2, y2, *, radius):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        self.canvas.coords(item_id, *points)

    # =========================================================================
    # Expanded Scrollable Answer Card (For Q&A, Explanations, Data Analysis)
    # =========================================================================
    def _is_question_or_info(self, command: str, result: str) -> bool:
        """Determines if a response warrants opening the dedicated Answer Window."""
        if not result:
            return False
        # Any multi-line output or long explanation should use the Answer Window
        if "\n" in result or len(result) > 65:
            return True
        cmd_lower = (command or "").lower().strip()
        info_keywords = [
            "what", "why", "how", "who", "where", "explain", "tell me",
            "summarize", "analyze", "describe", "read", "dataset", "insights",
            "statistics", "mean", "median", "help", "information", "define",
        ]
        return any(k in cmd_lower for k in info_keywords)

    def _show_answer_window(self, text: str, title: str = "NUVI Answer"):
        """Displays answers in a compact, scrollable, copyable card positioned snugly above Nuvi."""
        self._close_answer_window()

        card_w = 285
        card_h = 160
        pet_x = self.winfo_x()
        pet_y = self.winfo_y()
        screen_w = self.winfo_screenwidth()

        # Position snug right above Nuvi (centered horizontally and sitting close to the pet's head)
        card_x = max(10, min(screen_w - card_w - 10, pet_x + (self.WINDOW_W - card_w) // 2))
        card_y = max(15, pet_y - card_h + 25)

        self.answer_window = tk.Toplevel(self)
        self.answer_window.overrideredirect(True)
        self.answer_window.attributes("-topmost", True)
        self.answer_window.geometry(f"{card_w}x{card_h}+{card_x}+{card_y}")
        # Color matches original pet speech bubble: #fff8dc (cornsilk) with #e7d7a8 border
        self.answer_window.configure(bg="#fff8dc", highlightthickness=2, highlightbackground="#e7d7a8")

        # --- 1. Header Bar (Draggable) ---
        header = tk.Frame(self.answer_window, bg="#fff8dc", height=28, cursor="fleur")
        header.pack(fill=tk.X, side=tk.TOP, padx=4, pady=2)
        header.bind("<ButtonPress-1>", self._on_card_press)
        header.bind("<B1-Motion>", self._on_card_drag)

        title_lbl = tk.Label(
            header,
            text=f"🤖 {title}",
            bg="#fff8dc",
            fg="#362717",
            font=("Segoe UI", 9, "bold"),
            cursor="fleur",
        )
        title_lbl.pack(side=tk.LEFT, padx=4)
        title_lbl.bind("<ButtonPress-1>", self._on_card_press)
        title_lbl.bind("<B1-Motion>", self._on_card_drag)

        btn_box = tk.Frame(header, bg="#fff8dc")
        btn_box.pack(side=tk.RIGHT)

        self.answer_copy_btn = tk.Button(
            btn_box,
            text="📋 Copy",
            command=lambda: self._copy_answer_text(text),
            bg="#f3e8c9",
            fg="#362717",
            activebackground="#e7d7a8",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=6,
            pady=1,
            cursor="hand2",
        )
        self.answer_copy_btn.pack(side=tk.LEFT, padx=2)

        done_btn = tk.Button(
            btn_box,
            text="✕ Done",
            command=self._close_answer_window,
            bg="#f3e8c9",
            fg="#362717",
            activebackground="#e7d7a8",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=6,
            pady=1,
            cursor="hand2",
        )
        done_btn.pack(side=tk.LEFT, padx=2)

        # --- 2. Body Area (Scrollable Text) ---
        body = tk.Frame(self.answer_window, bg="#fffdf2")
        body.pack(fill=tk.BOTH, expand=True, padx=4, pady=1)

        self.answer_text = tk.Text(
            body,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#fffdf2",
            fg="#362717",
            padx=6,
            pady=4,
            bd=0,
            selectbackground="#e7d7a8",
            selectforeground="#362717",
        )
        scrollbar = tk.Scrollbar(body, orient=tk.VERTICAL, command=self.answer_text.yview)
        self.answer_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.answer_text.insert("1.0", text)
        self.answer_text.configure(state=tk.DISABLED)

        # Right-click context menu on text
        menu = tk.Menu(self.answer_text, tearoff=0)
        menu.add_command(label="Copy All", command=lambda: self._copy_answer_text(text))
        menu.add_command(label="Select All", command=self._select_all_text)
        self.answer_text.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))
        self.answer_text.bind("<Control-c>", self._on_copy_selection)
        self.answer_text.bind("<Control-C>", self._on_copy_selection)
        self.answer_window.bind("<Escape>", lambda _e: self._close_answer_window())

        # --- 3. Footer Bar (Voice acknowledgement guidance) ---
        footer = tk.Frame(self.answer_window, bg="#fff8dc")
        footer.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=2)

        hint_lbl = tk.Label(
            footer,
            text="💡 Say 'okay' or 'thank you' to close • or click Done",
            bg="#fff8dc",
            fg="#755f45",
            font=("Segoe UI", 8, "italic"),
        )
        hint_lbl.pack(side=tk.LEFT)

        self._waiting_for_acknowledgement = True

    def _copy_answer_text(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            if self.answer_copy_btn and self.answer_copy_btn.winfo_exists():
                self.answer_copy_btn.configure(text="✓ Copied!", bg="#d4edda")
                self.after(1600, self._reset_copy_btn)
        except Exception as exc:
            print(f"Clipboard error: {exc}")

    def _reset_copy_btn(self):
        if self.answer_copy_btn and self.answer_copy_btn.winfo_exists():
            self.answer_copy_btn.configure(text="📋 Copy", bg="#f3e8c9")

    def _select_all_text(self):
        if self.answer_text and self.answer_text.winfo_exists():
            self.answer_text.configure(state=tk.NORMAL)
            self.answer_text.tag_add("sel", "1.0", "end")
            self.answer_text.configure(state=tk.DISABLED)

    def _on_copy_selection(self, event=None):
        try:
            if self.answer_text and self.answer_text.winfo_exists():
                selected = self.answer_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected:
                    self.clipboard_clear()
                    self.clipboard_append(selected)
                    return "break"
        except tk.TclError:
            pass
        return None

    def _on_card_press(self, event):
        if self.answer_window and self.answer_window.winfo_exists():
            self._card_drag_x = event.x_root - self.answer_window.winfo_x()
            self._card_drag_y = event.y_root - self.answer_window.winfo_y()

    def _on_card_drag(self, event):
        if self.answer_window and self.answer_window.winfo_exists():
            new_x = event.x_root - self._card_drag_x
            new_y = event.y_root - self._card_drag_y
            self.answer_window.geometry(f"+{new_x}+{new_y}")

    def _close_answer_window(self):
        self._waiting_for_acknowledgement = False
        if self.answer_window:
            try:
                self.answer_window.destroy()
            except Exception:
                pass
            self.answer_window = None
            self.answer_text = None
            self.answer_copy_btn = None

    # =========================================================================
    # Two-Way Interactive Text Chatbox (3-Click Trigger)
    # =========================================================================
    def _toggle_chat_window(self):
        """Toggles the two-way interactive text Chatbox on/off."""
        if self.chat_window and self.chat_window.winfo_exists():
            self._close_chat_window()
        else:
            self._open_chat_window()

    def _open_chat_window(self):
        """Opens a compact scrollable two-way conversation window positioned snug above Nuvi."""
        self._close_answer_window()
        self._hide_bubble()

        chat_w = 320
        chat_h = 280
        pet_x = self.winfo_x()
        pet_y = self.winfo_y()
        screen_w = self.winfo_screenwidth()

        # Position snug directly above Nuvi
        chat_x = max(10, min(screen_w - chat_w - 10, pet_x + (self.WINDOW_W - chat_w) // 2))
        chat_y = max(20, pet_y - chat_h + 20)

        self.chat_window = tk.Toplevel(self)
        self.chat_window.overrideredirect(True)
        self.chat_window.attributes("-topmost", True)
        self.chat_window.geometry(f"{chat_w}x{chat_h}+{chat_x}+{chat_y}")
        self.chat_window.configure(bg="#fff8dc", highlightthickness=2, highlightbackground="#e7d7a8")

        # --- 1. Header Bar (Draggable) ---
        header = tk.Frame(self.chat_window, bg="#fff8dc", height=28, cursor="fleur")
        header.pack(fill=tk.X, side=tk.TOP, padx=4, pady=2)
        header.bind("<ButtonPress-1>", self._on_chat_press)
        header.bind("<B1-Motion>", self._on_chat_drag)

        title_lbl = tk.Label(
            header,
            text="💬 NUVI Chat",
            bg="#fff8dc",
            fg="#362717",
            font=("Segoe UI", 9, "bold"),
            cursor="fleur",
        )
        title_lbl.pack(side=tk.LEFT, padx=4)
        title_lbl.bind("<ButtonPress-1>", self._on_chat_press)
        title_lbl.bind("<B1-Motion>", self._on_chat_drag)

        btn_box = tk.Frame(header, bg="#fff8dc")
        btn_box.pack(side=tk.RIGHT)

        clear_btn = tk.Button(
            btn_box,
            text="Clear",
            command=self._clear_chat_history,
            bg="#f3e8c9",
            fg="#362717",
            activebackground="#e7d7a8",
            font=("Segoe UI", 8),
            relief="flat",
            padx=5,
            pady=1,
            cursor="hand2",
        )
        clear_btn.pack(side=tk.LEFT, padx=2)

        close_btn = tk.Button(
            btn_box,
            text="✕",
            command=self._close_chat_window,
            bg="#f3e8c9",
            fg="#362717",
            activebackground="#e7d7a8",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=5,
            pady=1,
            cursor="hand2",
        )
        close_btn.pack(side=tk.LEFT, padx=2)

        # --- 2. Bottom Text Input Area (Packed to BOTTOM first) ---
        inp_frame = tk.Frame(self.chat_window, bg="#fff8dc")
        inp_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=6)

        self.chat_entry = tk.Entry(
            inp_frame,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#362717",
            insertbackground="#362717",
            relief="solid",
            bd=1,
        )
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=3)
        self.chat_entry.bind("<Return>", lambda _e: self._send_chat_message())
        self.chat_entry.focus_set()

        send_btn = tk.Button(
            inp_frame,
            text="Send ➔",
            command=self._send_chat_message,
            bg="#e7d7a8",
            fg="#362717",
            activebackground="#dfcaa2",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
        )
        send_btn.pack(side=tk.RIGHT)

        # --- 3. Chat Conversation History Area (Fills middle) ---
        body = tk.Frame(self.chat_window, bg="#fffdf2")
        body.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=6, pady=2)

        self.chat_text = tk.Text(
            body,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#fffdf2",
            fg="#362717",
            padx=6,
            pady=4,
            bd=0,
            selectbackground="#e7d7a8",
            selectforeground="#362717",
        )
        scrollbar = tk.Scrollbar(body, orient=tk.VERTICAL, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure style tags
        self.chat_text.tag_configure("user_hdr", foreground="#8a4b08", font=("Segoe UI", 9, "bold"))
        self.chat_text.tag_configure("bot_hdr", foreground="#2e6930", font=("Segoe UI", 9, "bold"))

        self.chat_text.insert("1.0", "NUVI: ", "bot_hdr")
        self.chat_text.insert("end", "Hi! Chat with me or type commands (e.g. 'open chrome', 'what is ML').\n\n")
        self.chat_text.configure(state=tk.DISABLED)

        self.chat_window.bind("<Escape>", lambda _e: self._close_chat_window())

    def _close_chat_window(self):
        if self.chat_window:
            try:
                self.chat_window.destroy()
            except Exception:
                pass
            self.chat_window = None
            self.chat_text = None
            self.chat_entry = None

    def _clear_chat_history(self):
        if self.chat_text and self.chat_text.winfo_exists():
            self.chat_text.configure(state=tk.NORMAL)
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.insert("1.0", "NUVI: ", "bot_hdr")
            self.chat_text.insert("end", "Chat history cleared. How can I help?\n\n")
            self.chat_text.configure(state=tk.DISABLED)

    def _on_chat_press(self, event):
        if self.chat_window:
            self._chat_drag_x = event.x_root - self.chat_window.winfo_x()
            self._chat_drag_y = event.y_root - self.chat_window.winfo_y()

    def _on_chat_drag(self, event):
        if self.chat_window and self.chat_window.winfo_exists():
            new_x = event.x_root - self._chat_drag_x
            new_y = event.y_root - self._chat_drag_y
            self.chat_window.geometry(f"+{new_x}+{new_y}")

    def _append_chat(self, sender: str, message: str):
        if self.chat_text and self.chat_text.winfo_exists():
            self.chat_text.configure(state=tk.NORMAL)
            tag = "user_hdr" if sender == "You" else "bot_hdr"
            self.chat_text.insert("end", f"{sender}: ", tag)
            self.chat_text.insert("end", f"{message}\n\n")
            self.chat_text.see("end")
            self.chat_text.configure(state=tk.DISABLED)

    def _send_chat_message(self):
        if not self.chat_entry:
            return
        user_text = self.chat_entry.get().strip()
        if not user_text:
            return

        self.chat_entry.delete(0, tk.END)
        self._append_chat("You", user_text)
        self._start_busy_motion("think")

        # Run command / query in background thread
        threading.Thread(target=self._chat_worker, args=(user_text,), daemon=True).start()

    def _chat_worker(self, command: str):
        try:
            result = self.command_callback(command)
        except Exception as exc:
            result = f"Error: {exc}"
        self._result_queue.put(("chat_reply", result, "success", command))

    # =========================================================================
    # Voice Interaction & Worker
    # =========================================================================
    def _start_voice(self):
        if self._busy or self._dragging:
            return
        self._busy = True
        self._show_bubble("Listening...")
        self._start_busy_motion("listen")
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self):
        from ui.voice import listen_and_transcribe

        command = listen_and_transcribe()
        if not command:
            self._result_queue.put(("done", "I did not hear that.", "error", ""))
            return

        cmd_lower = command.lower().strip()
        ack_phrases = {
            "okay", "ok", "done", "thank you", "thanks", "thank",
            "got it", "understood", "close", "clear", "cancel", "bye", "fine",
        }
        spoken_tokens = set(re.findall(r"\b\w+\b", cmd_lower))

        # Check if the user is saying "okay", "thank you", etc. to dismiss the answer box
        if self._waiting_for_acknowledgement and (cmd_lower in ack_phrases or spoken_tokens.intersection(ack_phrases)):
            self._result_queue.put(("ack", "You're welcome! Glad I could help. 😊", "greet", command))
            return

        self._result_queue.put(("message", f"Heard: {command}", "think", command))
        self._execute_command(command)

    def _execute_command(self, command: str):
        try:
            result = self.command_callback(command)
        except Exception as exc:
            result = f"Command failed: {exc}"
        self._result_queue.put(("done", result, "success", command))

    def _drain_results(self):
        try:
            while True:
                item = self._result_queue.get_nowait()
                if len(item) == 4:
                    kind, message, state, cmd = item
                else:
                    kind, message, state = item
                    cmd = ""

                if kind == "message":
                    self._show_bubble(message)
                    self._start_busy_motion(state)
                elif kind == "ack":
                    self._close_answer_window()
                    self._busy = False
                    self._show_bubble(message, auto_hide=3500)
                    self._play_motion("greet")
                elif kind == "chat_reply":
                    self._busy = False
                    self._play_motion(state)
                    self._append_chat("NUVI", message)
                    if self.chat_entry and self.chat_entry.winfo_exists():
                        self.chat_entry.focus_set()
                else:  # kind == "done"
                    self._busy = False
                    if self._is_question_or_info(cmd, message):
                        self._hide_bubble()
                        self._show_answer_window(message)
                        self._play_motion(state)
                    else:
                        # For short action commands (e.g. 'Opened: Chrome'), show for 8 seconds
                        self._show_bubble(message, auto_hide=8000)
                        self._play_motion(state)
        except queue.Empty:
            pass
        self.after(100, self._drain_results)

    def _on_press(self, event):
        self._dragging = False
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _on_drag(self, event):
        self._dragging = True
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

        # Keep answer card positioned snug right above pet if open
        if self.answer_window and self.answer_window.winfo_exists():
            card_w = 285
            card_h = 160
            card_x = max(10, min(self.winfo_screenwidth() - card_w - 10, x + (self.WINDOW_W - card_w) // 2))
            card_y = max(15, y - card_h + 25)
            self.answer_window.geometry(f"+{card_x}+{card_y}")

        # Keep chat window positioned snug right above pet if open
        if self.chat_window and self.chat_window.winfo_exists():
            chat_w = 320
            chat_h = 280
            chat_x = max(10, min(self.winfo_screenwidth() - chat_w - 10, x + (self.WINDOW_W - chat_w) // 2))
            chat_y = max(20, y - chat_h + 20)
            self.chat_window.geometry(f"+{chat_x}+{chat_y}")

    def _on_release(self, _event):
        if self._dragging:
            self._play_motion("greet")
        self.after(120, lambda: setattr(self, "_dragging", False))

    def run(self):
        self.mainloop()
