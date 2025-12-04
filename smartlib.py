import tkinter as tk
from tkinter import ttk, messagebox
import time
import heapq
import webbrowser

# ================== GRAPH & POSITIONS ================== #
GRAPH = {
    "Entrance": ["Hall-1"],
    "Hall-1": ["Entrance", "Hall-2", "Shelf-A", "Shelf-B"],
    "Hall-2": ["Hall-1", "Shelf-C", "Shelf-D", "Shelf-E"],
    "Shelf-A": ["Hall-1"],
    "Shelf-B": ["Hall-1"],
    "Shelf-C": ["Hall-2"],
    "Shelf-D": ["Hall-2"],
    "Shelf-E": ["Hall-2"],
}

NODE_POS = {
    "Entrance": (30, 30),
    "Hall-1": (140, 30),
    "Hall-2": (250, 30),
    "Shelf-A": (110, 95),
    "Shelf-B": (180, 95),
    "Shelf-C": (250, 95),
    "Shelf-D": (330, 95),
    "Shelf-E": (410, 95),
}


def heuristic(n, goal):
    if n not in NODE_POS or goal not in NODE_POS:
        return 0
    x1, y1 = NODE_POS[n]
    x2, y2 = NODE_POS[goal]
    return abs(x1 - x2) + abs(y1 - y2)


def astar(graph, start, goal):
    if start not in graph or goal not in graph:
        return None

    open_heap = [(0, start)]
    g_cost = {start: 0}
    parent = {start: None}

    while open_heap:
        f, u = heapq.heappop(open_heap)
        if u == goal:
            path = []
            cur = goal
            while cur:
                path.append(cur)
                cur = parent[cur]
            return list(reversed(path))

        for v in graph[u]:
            tentative_g = g_cost[u] + 1
            if v not in g_cost or tentative_g < g_cost[v]:
                g_cost[v] = tentative_g
                f_v = tentative_g + heuristic(v, goal)
                heapq.heappush(open_heap, (f_v, v))
                parent[v] = u

    return None


# ================== DATA ================== #
BOOKS = [
    {"title": "AI", "author": "Russell", "shelf": "Shelf-A"},
    {"title": "Database", "author": "Silberschatz", "shelf": "Shelf-B"},
    {"title": "Python", "author": "Matthes", "shelf": "Shelf-C"},
]

SHELF_CAPACITY = {
    "Shelf-A": 7,
    "Shelf-B": 7,
    "Shelf-C": 7,
    "Shelf-D": 7,
    "Shelf-E": 7,
}


class SmartUI:
    def __init__(self, root):
        self.root = root
        root.title("Smart Library System · Ultra Modern UI")
        root.configure(bg="#f2faf7")
        root.geometry("1100x550")

        self.edit_index = None

        self.bg_main = "#f2faf7"
        self.bg_card = "#ffffff"
        self.primary = "#059669"
        self.primary_soft = "#a7f3d0"
        self.accent_blue = "#2563eb"
        self.accent_purple = "#6366f1"
        self.accent_red = "#ef4444"
        self.accent_orange = "#fb923c"
        self.text_dark = "#064e3b"

        self.capacity_choice = tk.StringVar(value="All Shelves")
        self.path_info_var = tk.StringVar(
            value="Double-click a book to see AI shortest route using A*."
        )
        self.route_path_var = tk.StringVar(value="Path: -")
        self.route_steps_var = tk.StringVar(value="Steps: -")
        self.status_var = tk.StringVar(value="Ready")
        self.stats_chip_var = tk.StringVar(value="Books: 0 · Shelves: 5 · Capacity: 0")

        self.init_style()
        self.build_header()
        self.build_layout()
        self.refresh_books()
        self.update_stats()

    # ---------- ttk Style ---------- #
    def init_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            rowheight=24,
            font=("Segoe UI", 10),
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            foreground=self.text_dark,
            background="#e5e7eb",
        )
        style.map("Treeview", background=[("selected", "#bfdbfe")])

        style.configure("TEntry", padding=3, relief="flat")
        style.configure("TCombobox", padding=3, relief="flat")

    # ---------- HEADER (dynamic) ---------- #
    def build_header(self):
        header = tk.Canvas(self.root, height=60, bg="#ffffff", highlightthickness=0)
        header.pack(fill="x")
        self.header = header

        # Developers button
        self.dev_btn = tk.Button(
            self.root,
            text="Developers",
            bg="#10b981",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=self.show_developers,
        )
        self.dev_btn_window = header.create_window(
            0, 0, window=self.dev_btn, anchor="e"
        )

        # Title & subtitle (always visible)
        self.title_text = header.create_text(
            20,
            30,
            anchor="w",
            text="📚 Smart Library System",
            font=("Segoe UI Semibold", 18, "bold"),
            fill=self.text_dark,
        )
        self.subtitle_text = header.create_text(
            0,
            30,
            anchor="w",
            text="AI Path Planning · A* Search",
            font=("Segoe UI", 11),
            fill="#047857",
        )

        header.bind("<Configure>", self._redraw_header)

    def _redraw_header(self, event=None):
        w = self.header.winfo_width()

        # gradient backgrounds
        self.header.delete("bg")
        self.header.create_rectangle(
            0, 0, w / 3, 60, fill=self.primary_soft, outline="", tags="bg"
        )
        self.header.create_rectangle(
            w / 3, 0, 2 * w / 3, 60, fill="#bbf7d0", outline="", tags="bg"
        )
        self.header.create_rectangle(
            2 * w / 3, 0, w, 60, fill="#dcfce7", outline="", tags="bg"
        )

        # **important**: send bg behind text so title na haray
        self.header.tag_lower("bg")

        # title & subtitle position
        self.header.coords(self.title_text, 20, 30)
        self.header.coords(self.subtitle_text, w / 2.2, 30)

        # developers button ekdom right
        self.header.coords(self.dev_btn_window, w - 10, 30)

    # ---------- MAIN LAYOUT (same as before) ---------- #
    def build_layout(self):
        main = tk.Frame(self.root, bg=self.bg_main)
        main.pack(pady=8, padx=8, fill="both", expand=True)

        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # ========== LEFT PANEL ==========
        left = tk.Frame(main, bg=self.bg_main)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 6))

        # ---- Smart Search ----
        search_card = tk.Frame(left, bg=self.bg_card, bd=1, relief="solid")
        search_card.pack(fill="x", pady=(0, 8))

        tk.Label(
            search_card,
            text="🔍 Smart Search",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 4))

        search_box = tk.Frame(
            search_card,
            bg="#f0fdf4",
            highlightthickness=1,
            highlightbackground="#a7f3d0",
        )
        search_box.pack(fill="x", padx=10, pady=(0, 8))

        self.q = tk.StringVar()

        entry_frame = tk.Frame(search_box, bg="#f0fdf4")
        entry_frame.pack(fill="x", padx=6, pady=(4, 4))

        search_entry = tk.Entry(
            entry_frame,
            textvariable=self.q,
            bg="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            font=("Segoe UI", 10),
        )
        search_entry.pack(fill="x", ipady=4)

        btn_row = tk.Frame(search_box, bg="#f0fdf4")
        btn_row.pack(fill="x", padx=6, pady=(0, 6))

        tk.Button(
            btn_row,
            text="Search",
            width=10,
            bg=self.primary,
            fg="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=self.search,
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="Reset",
            width=8,
            bg="#4b5563",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            command=self.reset_search,
        ).pack(side="left", padx=10)

        # ---- Library Stats ----
        stats_card = tk.Frame(left, bg=self.bg_card, bd=1, relief="solid")
        stats_card.pack(fill="x", pady=(0, 8))

        tk.Label(
            stats_card,
            text="📊 Library Stats",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 2))

        tk.Frame(stats_card, bg="#e5e7eb", height=1).pack(
            fill="x", padx=10, pady=(0, 6)
        )

        tk.Label(
            stats_card,
            textvariable=self.stats_chip_var,
            bg="#ecfdf5",
            fg="#047857",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
            padx=6,
            pady=3,
        ).pack(fill="x", padx=10, pady=(0, 6))

        self.total_var = tk.StringVar()
        self.capacity_var = tk.StringVar()

        tk.Label(
            stats_card,
            textvariable=self.total_var,
            bg=self.bg_card,
            fg="#111827",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=10, pady=(0, 2))

        tk.Label(
            stats_card,
            textvariable=self.capacity_var,
            bg=self.bg_card,
            fg="#6b7280",
            font=("Segoe UI", 9),
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 4))

        self.shelf_canvas = tk.Canvas(
            stats_card,
            width=220,
            height=90,
            bg=self.bg_card,
            highlightthickness=0,
        )
        self.shelf_canvas.pack(anchor="w", padx=6, pady=(0, 4))

        cap_frame = tk.Frame(stats_card, bg=self.bg_card)
        cap_frame.pack(anchor="w", padx=10, pady=(4, 10))

        tk.Label(
            cap_frame, text="Increase for:", bg=self.bg_card, font=("Segoe UI", 8)
        ).grid(row=0, column=0, sticky="w")

        cap_box = ttk.Combobox(
            cap_frame,
            textvariable=self.capacity_choice,
            values=["All Shelves"] + list(SHELF_CAPACITY.keys()),
            state="readonly",
            width=11,
        )
        cap_box.grid(row=0, column=1, padx=4, sticky="w")

        tk.Button(
            cap_frame,
            text="+1 Capacity",
            bg="#0ea5e9",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=self.expand_shelf_capacity,
        ).grid(row=0, column=2, padx=2)

        # ---- Route card ----
        route_card = tk.Frame(left, bg=self.bg_card, bd=1, relief="solid")
        route_card.pack(fill="x", pady=(0, 0))

        tk.Label(
            route_card,
            text="📌 AI Shortest Route (A* Search)",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 2))

        tk.Frame(route_card, bg="#e5e7eb", height=1).pack(
            fill="x", padx=10, pady=(0, 4)
        )

        route_box = tk.Frame(route_card, bg="#ecfdf5")
        route_box.pack(anchor="w", padx=10, pady=(0, 8), fill="x")

        tk.Label(
            route_box,
            textvariable=self.route_path_var,
            bg="#ecfdf5",
            fg="#064e3b",
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            route_box,
            textvariable=self.route_steps_var,
            bg="#ecfdf5",
            fg="#064e3b",
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(anchor="w")

        # ========== MID TABLE ==========
        mid = tk.Frame(main, bg=self.bg_card, bd=1, relief="solid")
        mid.grid(row=0, column=1, padx=6, sticky="nsew")

        tk.Label(
            mid,
            text="📘 Books (Double-click to view route)",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 0))

        cols = ("title", "author", "shelf")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("shelf", text="Shelf")

        self.tree.column("title", anchor="center", width=200)
        self.tree.column("author", anchor="center", width=170)
        self.tree.column("shelf", anchor="center", width=80)

        self.tree.tag_configure("oddrow", background="#f9fafb")
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.bind("<<TreeviewSelect>>", self.select_row)

        # ========== RIGHT PANEL ==========
        right = tk.Frame(main, bg=self.bg_main)
        right.grid(row=0, column=2, sticky="nse", padx=(6, 0))
        right.grid_rowconfigure(0, weight=0)
        right.grid_rowconfigure(1, weight=0)
        right.grid_rowconfigure(2, weight=1)

        # ---- Manage Books ----
        manage = tk.Frame(right, bg=self.bg_card, bd=1, relief="solid")
        manage.grid(row=0, column=0, sticky="new", pady=(0, 6))

        tk.Label(
            manage,
            text="✏ Manage Books",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 2))

        tk.Frame(manage, bg="#e5e7eb", height=1).pack(fill="x", padx=10, pady=(0, 6))

        form_bg = tk.Frame(manage, bg="#f9fafb", bd=1, relief="solid")
        form_bg.pack(fill="x", padx=10, pady=(0, 8))

        form = tk.Frame(form_bg, bg="#f9fafb")
        form.pack(fill="x", padx=6, pady=6)
        form.grid_columnconfigure(0, weight=1)

        tk.Label(form, text="Title", bg="#f9fafb", font=("Segoe UI", 9)).grid(
            row=0, column=0, sticky="w", pady=1
        )
        tk.Label(form, text="Author", bg="#f9fafb", font=("Segoe UI", 9)).grid(
            row=2, column=0, sticky="w", pady=1
        )
        tk.Label(form, text="Shelf", bg="#f9fafb", font=("Segoe UI", 9)).grid(
            row=4, column=0, sticky="w", pady=1
        )

        self.t = tk.StringVar()
        self.a = tk.StringVar()
        self.s = tk.StringVar(value="Shelf-A")

        ttk.Entry(form, textvariable=self.t).grid(
            row=1, column=0, pady=(0, 4), sticky="we"
        )
        ttk.Entry(form, textvariable=self.a).grid(
            row=3, column=0, pady=(0, 4), sticky="we"
        )
        ttk.Combobox(
            form,
            textvariable=self.s,
            values=list(SHELF_CAPACITY.keys()),
            state="readonly",
        ).grid(row=5, column=0, pady=(0, 4), sticky="we")

        btns = tk.Frame(manage, bg=self.bg_card)
        btns.pack(anchor="w", padx=10, pady=(0, 8))

        tk.Button(
            btns,
            text="Add",
            bg=self.accent_blue,
            fg="white",
            width=8,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=self.add_book,
        ).grid(row=0, column=0, padx=4, pady=2)

        tk.Button(
            btns,
            text="Update",
            bg=self.accent_purple,
            fg="white",
            width=8,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=self.update_book,
        ).grid(row=0, column=1, padx=4, pady=2)

        tk.Button(
            btns,
            text="Delete",
            bg=self.accent_red,
            fg="white",
            width=8,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=self.delete_book,
        ).grid(row=0, column=2, padx=4, pady=2)

        tk.Button(
            btns,
            text="Clear",
            bg="#6b7280",
            fg="white",
            width=8,
            relief="flat",
            font=("Segoe UI", 9),
            command=self.clear_form,
        ).grid(row=0, column=3, padx=4, pady=2)

        # ---- Map card ----
        map_card = tk.Frame(right, bg=self.bg_card, bd=1, relief="solid")
        map_card.grid(row=1, column=0, sticky="new")

        tk.Label(
            map_card,
            text="📍 Library Map (Animated)",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=10, pady=(6, 0))

        tk.Frame(map_card, bg="#e5e7eb", height=1).pack(
            fill="x", padx=10, pady=(2, 4)
        )

        self.map = tk.Canvas(
            map_card,
            bg="white",
            width=460,
            height=170,
            highlightthickness=0,
        )
        self.map.pack(padx=6, pady=4)

        tk.Label(
            map_card,
            textvariable=self.path_info_var,
            bg=self.bg_card,
            fg="#4b5563",
            font=("Segoe UI", 8),
            wraplength=260,
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 6))

        tk.Frame(right, bg=self.bg_main).grid(row=2, column=0, sticky="nsew")

        self.draw_map()

        bottom = tk.Frame(self.root, bg="#e5f5ef")
        bottom.pack(side="bottom", fill="x")

        tk.Label(
            bottom,
            textvariable=self.status_var,
            bg="#e5f5ef",
            fg="#374151",
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(side="left", padx=10, pady=3)

    # ---------- Developers popup ---------- #
    def show_developers(self):
        win = tk.Toplevel(self.root)
        win.title("Developers")
        win.configure(bg=self.bg_card)
        win.resizable(False, False)

        tk.Frame(win, bg=self.primary, height=4).pack(fill="x")

        tk.Label(
            win,
            text="Welcome to our Library World",
            bg=self.bg_card,
            fg=self.text_dark,
            font=("Segoe UI Semibold", 12, "bold"),
        ).pack(padx=20, pady=(12, 6))

        tk.Frame(win, bg="#e5e7eb", height=1).pack(fill="x", padx=20, pady=(0, 8))

        name_frame = tk.Frame(win, bg=self.bg_card)
        name_frame.pack(padx=24, pady=(0, 10), anchor="w")

        tk.Label(
            name_frame,
            text="👨  Saifulla Tanim",
            bg=self.bg_card,
            fg="#111827",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=3)
        tk.Label(
            name_frame,
            text="Lead Developer",
            bg=self.bg_card,
            fg="#6b7280",
            font=("Segoe UI", 8),
        ).grid(row=0, column=1, sticky="w", padx=(8, 0))

        btn_frame1 = tk.Frame(name_frame, bg=self.bg_card)
        btn_frame1.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        tk.Button(
            btn_frame1,
            text="GitHub",
            bg="#111827",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            command=lambda: webbrowser.open("https://github.com/saifullahtanim"),
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_frame1,
            text="Facebook",
            bg="#1d4ed8",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            command=lambda: webbrowser.open(
                "https://www.facebook.com/iam.saifullatanim02"
            ),
        ).pack(side="left")

        tk.Label(
            name_frame,
            text="👩  Mim Akter",
            bg=self.bg_card,
            fg="#111827",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=2, column=0, sticky="w", pady=3)
        tk.Label(
            name_frame,
            text="Co-Developer",
            bg=self.bg_card,
            fg="#6b7280",
            font=("Segoe UI", 8),
        ).grid(row=2, column=1, sticky="w", padx=(8, 0))

        btn_frame2 = tk.Frame(name_frame, bg=self.bg_card)
        btn_frame2.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))
        tk.Button(
            btn_frame2,
            text="GitHub",
            bg="#111827",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            command=lambda: webbrowser.open("https://github.com/mimakter31"),
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_frame2,
            text="Facebook",
            bg="#1d4ed8",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            command=lambda: webbrowser.open(
                "https://www.facebook.com/profile.php?id=61584310525040"
            ),
        ).pack(side="left")

        tk.Button(
            win,
            text="Close",
            bg="#6b7280",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            command=win.destroy,
        ).pack(pady=(0, 12))

    # ================== MAP / STATS / CRUD / SEARCH ================== #
    def draw_map(self):
        self.map.delete("all")
        xy = NODE_POS

        def line(a, b):
            x1, y1 = xy[a]
            x2, y2 = xy[b]
            self.map.create_line(
                x1 + 22, y1 + 22, x2 + 22, y2 + 22, fill="#9ca3af", width=2
            )

        line("Entrance", "Hall-1")
        line("Hall-1", "Hall-2")
        line("Hall-1", "Shelf-A")
        line("Hall-1", "Shelf-B")
        line("Hall-2", "Shelf-C")
        line("Hall-2", "Shelf-D")
        line("Hall-2", "Shelf-E")

        for label, (x, y) in xy.items():
            self.map.create_oval(
                x,
                y,
                x + 44,
                y + 44,
                fill=self.primary_soft,
                outline=self.text_dark,
                width=2,
            )
            short = label.replace("Shelf-", "S-").replace("Hall-", "H-")
            self.map.create_text(
                x + 22,
                y + 22,
                text=short if label != "Entrance" else "Ent",
                fill=self.text_dark,
                font=("Segoe UI", 9, "bold"),
            )

    def animate(self, nodes):
        if not nodes:
            return
        self.draw_map()
        xy = NODE_POS
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            x1, y1 = xy[a]
            x2, y2 = xy[b]
            self.map.create_line(
                x1 + 22,
                y1 + 22,
                x2 + 22,
                y2 + 22,
                fill=self.accent_orange,
                width=4,
            )

        self.root.update()
        delay = 0.25
        for node in nodes:
            x, y = xy[node]
            dot = self.map.create_oval(
                x + 14,
                y + 14,
                x + 30,
                y + 30,
                fill=self.accent_orange,
                outline="",
            )
            self.root.update()
            time.sleep(delay)
            self.map.delete(dot)

    def count_shelf_books(self, shelf):
        return sum(1 for b in BOOKS if b["shelf"] == shelf)

    def update_stats(self):
        total = len(BOOKS)
        self.total_var.set(f"Total Books: {total}")

        msg_lines = []
        per_shelf = []
        total_cap = 0

        for shelf, cap in SHELF_CAPACITY.items():
            used = self.count_shelf_books(shelf)
            msg_lines.append(f"{shelf}: {used}/{cap}")
            total_cap += cap
            per_shelf.append((shelf, used, cap))

        self.capacity_var.set("\n".join(msg_lines))
        self.stats_chip_var.set(
            f"Books: {total} · Shelves: {len(SHELF_CAPACITY)} · Capacity: {total_cap}"
        )

        self.shelf_canvas.delete("all")
        x = 6
        y = 14
        max_width = 180
        for shelf, used, cap in per_shelf:
            ratio = 0 if cap == 0 else used / cap
            w = int(max_width * ratio)
            self.shelf_canvas.create_text(
                x,
                y,
                text=shelf.replace("Shelf-", "S-"),
                anchor="w",
                font=("Segoe UI", 8),
            )
            self.shelf_canvas.create_rectangle(
                x + 28,
                y - 5,
                x + 28 + max_width,
                y + 5,
                outline="#d1d5db",
                fill="#f3f4f6",
            )
            if w > 0:
                self.shelf_canvas.create_rectangle(
                    x + 28,
                    y - 5,
                    x + 28 + w,
                    y + 5,
                    outline="",
                    fill=self.primary_soft,
                )
            y += 16

    def set_status(self, text):
        self.status_var.set(text)

    def clear_form(self):
        self.t.set("")
        self.a.set("")
        self.s.set("Shelf-A")
        self.edit_index = None
        self.set_status("Form cleared, no row selected.")
        self.route_path_var.set("Path: -")
        self.route_steps_var.set("Steps: -")
        self.path_info_var.set(
            "Double-click a book to see AI shortest route using A*."
        )
        self.draw_map()

    def expand_shelf_capacity(self):
        choice = self.capacity_choice.get()
        if choice == "All Shelves":
            for shelf in SHELF_CAPACITY:
                SHELF_CAPACITY[shelf] += 1
            self.set_status("Shelf capacity increased by 1 for all shelves.")
        else:
            SHELF_CAPACITY[choice] += 1
            self.set_status(f"{choice} capacity increased by 1.")
        self.update_stats()

    def refresh_books(self, book_list=None):
        if book_list is None:
            book_list = BOOKS
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, b in enumerate(book_list):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "", "end", values=(b["title"], b["author"], b["shelf"]), tags=(tag,)
            )
        self.update_stats()

    def find_path(self, shelf):
        return astar(GRAPH, "Entrance", shelf)

    def select_row(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        title, author, shelf = vals

        self.edit_index = None
        for i, b in enumerate(BOOKS):
            if b["title"] == title and b["author"] == author and b["shelf"] == shelf:
                self.edit_index = i
                break
        if self.edit_index is None:
            return

        b = BOOKS[self.edit_index]
        self.t.set(b["title"])
        self.a.set(b["author"])
        self.s.set(b["shelf"])

        path = self.find_path(b["shelf"])
        if path:
            steps = len(path) - 1
            self.route_path_var.set("Path: " + " → ".join(path))
            self.route_steps_var.set(f"Steps: {steps}")
            self.set_status(f"A* found path to {b['shelf']} ({steps} step/s).")
            self.path_info_var.set(
                f"A* selected the path with {steps} step(s) from Entrance to {b['shelf']}."
            )
            self.animate(path)
        else:
            self.route_path_var.set("Path: No route found.")
            self.route_steps_var.set("Steps: -")
            self.set_status("No route found in graph.")
            self.path_info_var.set("No route found in current map.")
            self.draw_map()

    def add_book(self):
        title, author, shelf = self.t.get().strip(), self.a.get().strip(), self.s.get()
        if not title or not author:
            return messagebox.showerror("Error", "Please fill all fields.")
        used = self.count_shelf_books(shelf)
        if used >= SHELF_CAPACITY[shelf]:
            return messagebox.showerror(
                "Shelf Full",
                f"{shelf} is full ({used}/{SHELF_CAPACITY[shelf]}). "
                f"Increase capacity or choose another shelf.",
            )
        BOOKS.append({"title": title, "author": author, "shelf": shelf})
        self.refresh_books()
        self.clear_form()
        self.set_status(f"Book '{title}' added to {shelf}.")

    def update_book(self):
        if self.edit_index is None:
            return messagebox.showwarning(
                "No Selection", "Select a book from the table first."
            )
        new_title = self.t.get().strip()
        new_author = self.a.get().strip()
        new_shelf = self.s.get()
        if not new_title or not new_author:
            return messagebox.showerror("Error", "Please fill all fields.")

        old_shelf = BOOKS[self.edit_index]["shelf"]
        if new_shelf != old_shelf:
            used = self.count_shelf_books(new_shelf)
            if used >= SHELF_CAPACITY[new_shelf]:
                return messagebox.showerror(
                    "Shelf Full",
                    f"{new_shelf} is full ({used}/{SHELF_CAPACITY[new_shelf]}).",
                )

        BOOKS[self.edit_index] = {
            "title": new_title,
            "author": new_author,
            "shelf": new_shelf,
        }
        self.refresh_books()
        self.set_status(f"Book updated: '{new_title}'.")
        self.route_path_var.set("Path: -")
        self.route_steps_var.set("Steps: -")
        self.path_info_var.set(
            "Double-click a book to see AI shortest route using A*."
        )
        self.draw_map()

    def delete_book(self):
        if self.edit_index is None:
            return messagebox.showwarning(
                "No Selection", "Select a book from the table first."
            )
        b = BOOKS[self.edit_index]
        if messagebox.askyesno(
            "Confirm Delete", f"Delete '{b['title']}' from {b['shelf']}?"
        ):
            BOOKS.pop(self.edit_index)
            self.refresh_books()
            self.clear_form()
            self.set_status("Book deleted.")

    def search(self):
        q = self.q.get().strip().lower()
        if not q:
            self.refresh_books()
            self.set_status("Search box empty – showing all books.")
            return
        result = [
            b
            for b in BOOKS
            if q in b["title"].lower()
            or q in b["author"].lower()
            or q in b["shelf"].lower()
        ]
        self.refresh_books(result)
        self.set_status(f"Search result: {len(result)} book(s) found.")

    def reset_search(self):
        self.q.set("")
        self.refresh_books()
        self.set_status("Search reset – showing all books.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartUI(root)
    root.mainloop()
