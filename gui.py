import os
import random
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from user_system import load_users, save_users
from models.task import Task
from models.user import User
from utils.quotes import QUOTES
from utils.paths import DATA_DIR

# Enhanced appearance with custom colors
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Custom color palette
COLORS = {
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "bg_dark": "#1e293b",
    "bg_card": "#2d3748",
    "text_light": "#e2e8f0",
    "text_muted": "#94a3b8",
}

APP_TITLE = "FocusFlow "

def today_iso():
    return date.today().isoformat()

def safe_user(username):
    try:
        return User(username)
    except Exception as e:
        messagebox.showerror("Backend error", f"Cannot instantiate user: {e}")
        return None

class FocusFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1400x820")
        self.minsize(1200, 700)
        
        self.current_user = None
        
        # Enhanced topbar with gradient effect
        topbar = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=COLORS["bg_dark"])
        topbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        topbar.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        title_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        ctk.CTkLabel(
            title_frame, 
            text="FocusFlow", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Productivity Analyzer",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(10, 0))
        
        # Theme controls
        control_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        control_frame.grid(row=0, column=2, padx=20, sticky="e")
        
        self.theme_switch = ctk.CTkSegmentedButton(
            control_frame,
            values=["Light", "Dark", "System"],
            command=self._on_theme,
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"]
        )
        self.theme_switch.set("Dark")
        self.theme_switch.pack(side="right")
        
        # Main layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Enhanced sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLORS["bg_dark"])
        self.sidebar.grid(row=1, column=0, sticky="ns", padx=(0, 2))
        self.sidebar.grid_propagate(False)
        
        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        self._build_sidebar()
        self._build_pages()
        self.show_page("LoginPage")
    
    def _on_theme(self, val):
        ctk.set_appearance_mode(val.lower())
    
    def _build_sidebar(self):
        # User profile section
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.pack(pady=20, padx=15, fill="x")
        
        ctk.CTkLabel(
            profile_frame,
            text="👤",
            font=ctk.CTkFont(size=32)
        ).pack()
        
        self.sidebar_user_label = ctk.CTkLabel(
            profile_frame,
            text="Not logged in",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        self.sidebar_user_label.pack(pady=(5, 0))
        
        # Separator
        ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS["bg_card"]).pack(fill="x", padx=15, pady=10)
        
        # Navigation label
        ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        # Navigation button
        self.btn_home = self._create_nav_button(self.sidebar, "🏠 Home", self._show_home_from_sidebar)
        self.btn_home.pack(fill="x", padx=15, pady=4)
    
    def _create_nav_button(self, parent, text, command):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color=COLORS["primary"],
            anchor="w",
            height=40,
            font=ctk.CTkFont(size=14)
        )
    
    def _build_pages(self):
        self.pages = {}
        for Page in (LoginPage, RegisterPage, DashboardPage):
            page = Page(self.content, self)
            self.pages[Page.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")
    
    def show_page(self, name: str):
        p = self.pages.get(name)
        if p:
            p.tkraise()
    
    def login_success(self, username: str):
        user_obj = safe_user(username)
        if not user_obj:
            return
        self.current_user = user_obj
        self.sidebar_user_label.configure(
            text=f"{username}",
            text_color=COLORS["primary"]
        )
        dash: DashboardPage = self.pages["DashboardPage"]
        dash.set_user(self.current_user)
        self.show_page("DashboardPage")
        dash.show_home()
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.sidebar_user_label.configure(
                text="Not logged in",
                text_color=COLORS["text_muted"]
            )
            self.show_page("LoginPage")
    
    def _show_home_from_sidebar(self):
        if "DashboardPage" in self.pages:
            self.show_page("DashboardPage")
            self.pages["DashboardPage"].show_home()

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, app: FocusFlowApp):
        super().__init__(parent)
        self.app = app
        
        # Make the frame expand properly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)
        
        # Enhanced card with shadow effect
        self.card = ctk.CTkFrame(
            wrapper,
            width=520,
            height=480,
            corner_radius=20,
            border_width=1,
            border_color=COLORS["primary"]
        )
        self.card.pack(expand=True)
        self.card.grid_propagate(False)
        
        # Icon
        ctk.CTkLabel(
            self.card,
            text="🎯",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            self.card,
            text="Welcome to FocusFlow",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            self.card,
            text="Track your productivity journey",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 25))
        
        # Form
        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(
            form,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_user = ctk.CTkEntry(
            form,
            height=45,
            placeholder_text="Enter your username",
            border_width=2,
            corner_radius=10
        )
        self.entry_user.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            form,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_pass = ctk.CTkEntry(
            form,
            height=45,
            show="●",
            placeholder_text="Enter your password",
            border_width=2,
            corner_radius=10
        )
        self.entry_pass.pack(fill="x", pady=(0, 20))
        
        # Buttons
        ctk.CTkButton(
            form,
            text="Login",
            height=45,
            command=self.attempt_login,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=10
        ).pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            form,
            text="Create Account",
            height=45,
            command=lambda: self.app.show_page("RegisterPage"),
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["primary"],
            hover_color=COLORS["bg_card"],
            corner_radius=10
        ).pack(fill="x")
    
    def attempt_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Input", "Please enter username and password")
            return
        users = load_users()
        if username in users and users[username]["password"] == password:
            self.app.login_success(username)
        else:
            messagebox.showerror("Login failed", "Invalid username or password")

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, app: FocusFlowApp):
        super().__init__(parent)
        self.app = app
        
        # Make the frame expand properly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)
        
        self.card = ctk.CTkFrame(
            wrapper,
            width=520,
            height=540,
            corner_radius=20,
            border_width=1,
            border_color=COLORS["success"]
        )
        self.card.pack(expand=True)
        self.card.grid_propagate(False)
        
        ctk.CTkLabel(
            self.card,
            text="✨",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            self.card,
            text="Create Your Account",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            self.card,
            text="Start your productivity journey today",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 25))
        
        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(padx=40, fill="x")
        
        ctk.CTkLabel(
            form,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.e_user = ctk.CTkEntry(
            form,
            height=45,
            placeholder_text="Choose a username",
            border_width=2,
            corner_radius=10
        )
        self.e_user.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            form,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.e_pass = ctk.CTkEntry(
            form,
            height=45,
            show="●",
            placeholder_text="Create a password",
            border_width=2,
            corner_radius=10
        )
        self.e_pass.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            form,
            text="Confirm Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.e_confirm = ctk.CTkEntry(
            form,
            height=45,
            show="●",
            placeholder_text="Confirm your password",
            border_width=2,
            corner_radius=10
        )
        self.e_confirm.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(
            form,
            text="Create Account",
            height=45,
            command=self.create_account,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#059669",
            corner_radius=10
        ).pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            form,
            text="Back to Login",
            height=45,
            command=lambda: self.app.show_page("LoginPage"),
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["text_muted"],
            hover_color=COLORS["bg_card"],
            corner_radius=10
        ).pack(fill="x")
    
    def create_account(self):
        u = self.e_user.get().strip()
        p = self.e_pass.get().strip()
        c = self.e_confirm.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Please provide username and password")
            return
        if p != c:
            messagebox.showerror("Error", "Passwords do not match")
            return
        users = load_users()
        if u in users:
            messagebox.showerror("Error", "Username already exists")
            return
        users[u] = {"password": p}
        save_users(users)
        messagebox.showinfo("Success", "Account created! You can now login.")
        self.app.show_page("LoginPage")

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app: FocusFlowApp):
        super().__init__(parent)
        self.app = app
        self.user = None
        self.current_nav_button = None
        
        self.columnconfigure(1, weight=1)
        
        # Enhanced left menu
        left = ctk.CTkFrame(self, width=240, corner_radius=12, fg_color=COLORS["bg_card"])
        left.grid(row=0, column=0, sticky="nsw", padx=15, pady=15)
        left.grid_propagate(False)
        
        # Content area
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        # Menu sections
        ctk.CTkLabel(
            left,
            text="MENU",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Store navigation buttons
        self.nav_buttons = {}
        
        menu_items = [
            ("home", "🏠", "Home", self.show_home),
            ("add", "➕", "Add Task", self.show_add),
            ("tasks", "📋", "Tasks", self.show_tasks),
            ("analytics", "📊", "Analytics", self.show_analytics),
            ("visualize", "📈", "Visualize", self.show_visualize),
            ("backup", "💾", "Backup", self.show_backup),
        ]
        
        for key, icon, text, cmd in menu_items:
            btn = self._create_menu_button(left, f"{icon} {text}", cmd)
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = btn
        
        # Separator
        ctk.CTkFrame(left, height=2, fg_color=COLORS["bg_dark"]).pack(fill="x", padx=15, pady=15)
        
        # Logout button
        ctk.CTkButton(
            left,
            text="🚪 Logout",
            command=self.app.logout,
            fg_color=COLORS["danger"],
            hover_color="#dc2626",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=12, pady=(5, 15))
        
        self.lbl_user = ctk.CTkLabel(
            left,
            text="Not logged in",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.lbl_user.pack(side="bottom", pady=15)
        
        # Pages
        self.pages = {}
        for Page in (HomeCard, AddTaskCard, TasksCard, AnalyticsCard, VisualizeCard, BackupCard):
            pg = Page(self.content_area, self)
            self.pages[Page.__name__] = pg
            pg.grid(row=0, column=0, sticky="nsew")
        
        self.show_home()
    
    def _create_menu_button(self, parent, text, command):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color=COLORS["primary"],
            anchor="w",
            height=38,
            font=ctk.CTkFont(size=13)
        )
    
    def set_user(self, user: User):
        self.user = user
        self.lbl_user.configure(text=f"👤 {user.username}")
        for p in self.pages.values():
            if hasattr(p, "refresh"):
                try:
                    p.refresh()
                except Exception:
                    pass
        self._remind_unfinished()
    
    def _remind_unfinished(self):
        if not self.user:
            return
        today = date.today()
        try:
            pending = [t for t in self.user.tasks_on_date(today) if not t.completed]
        except Exception:
            pending = []
        if pending:
            msg = f"You have {len(pending)} unfinished tasks today:\n" + "\n".join([f"- {t.name} ({t.hours}h)" for t in pending[:8]])
            messagebox.showinfo("Reminder", msg + "\n\n" + random.choice(QUOTES))
    
    def _highlight_nav(self, key):
        """Highlight the active navigation button"""
        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.configure(fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"])
            else:
                btn.configure(fg_color="transparent", hover_color=COLORS["primary"])
    
    def show_home(self): 
        self._highlight_nav("home")
        self.pages["HomeCard"].refresh()
        self.pages["HomeCard"].tkraise()
    
    def show_add(self): 
        self._highlight_nav("add")
        self.pages["AddTaskCard"].tkraise()
    
    def show_tasks(self): 
        self._highlight_nav("tasks")
        self.pages["TasksCard"].refresh()
        self.pages["TasksCard"].tkraise()
    
    def show_analytics(self): 
        self._highlight_nav("analytics")
        self.pages["AnalyticsCard"].refresh()
        self.pages["AnalyticsCard"].tkraise()
    
    def show_visualize(self): 
        self._highlight_nav("visualize")
        self.pages["VisualizeCard"].refresh()
        self.pages["VisualizeCard"].tkraise()
    
    def show_backup(self): 
        self._highlight_nav("backup")
        self.pages["BackupCard"].refresh()
        self.pages["BackupCard"].tkraise()

class HomeCard(ctk.CTkFrame):
    def __init__(self, parent, dashboard: DashboardPage):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        
        # Main scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # Welcome section
        welcome_card = ctk.CTkFrame(scroll, corner_radius=15, fg_color=COLORS["bg_card"])
        welcome_card.pack(fill="x", padx=10, pady=10)
        
        self.lbl_welcome = ctk.CTkLabel(
            welcome_card,
            text="Welcome!",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.lbl_welcome.pack(pady=(20, 5), padx=20)
        
        self.lbl_quote = ctk.CTkLabel(
            welcome_card,
            text=random.choice(QUOTES),
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
            wraplength=500
        )
        self.lbl_quote.pack(pady=(0, 20), padx=20)
        
        # Stats grid
        stats_container = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_container.pack(fill="x", padx=10, pady=10)
        
        stats_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.stat_cards = {}
        stats = [
            ("tasks", "Today's Tasks", "📋", COLORS["primary"]),
            ("hours", "Hours Today", "⏱️", COLORS["success"]),
            ("score", "Productivity", "🎯", COLORS["warning"])
        ]
        
        for i, (key, title, icon, color) in enumerate(stats):
            card = self._create_stat_card(stats_container, title, "—", icon, color)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            self.stat_cards[key] = card
        
        # Quick actions
        actions_card = ctk.CTkFrame(scroll, corner_radius=15, fg_color=COLORS["bg_card"])
        actions_card.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            actions_card,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        btn_frame = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            btn_frame,
            text="➕ Add Task",
            command=lambda: self.dashboard.show_add(),
            height=45,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="📋 View All Tasks",
            command=lambda: self.dashboard.show_tasks(),
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["primary"],
            hover_color=COLORS["bg_dark"],
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", expand=True, padx=(5, 0))
        
        # Recent tasks
        recent_card = ctk.CTkFrame(scroll, corner_radius=15, fg_color=COLORS["bg_card"])
        recent_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            recent_card,
            text="Recent Tasks",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        self.recent_frame = ctk.CTkFrame(recent_card, fg_color="transparent")
        self.recent_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        self.refresh()
    
    def _create_stat_card(self, parent, title, value, icon, color):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=COLORS["bg_card"], border_width=2, border_color=color)
        
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=32)
        ).pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        )
        value_label.pack()
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 15))
        
        card.value_label = value_label
        return card
    
    def refresh(self):
        user = self.dashboard.user
        if not user:
            self.lbl_welcome.configure(text="Welcome! Please login.")
            for card in self.stat_cards.values():
                card.value_label.configure(text="—")
            for w in self.recent_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.recent_frame,
                text="Not logged in",
                text_color=COLORS["text_muted"]
            ).pack(pady=20)
            return
        
        self.lbl_welcome.configure(text=f"Welcome back, {user.username}! 👋")
        
        today = date.today()
        try:
            todays = user.tasks_on_date(today)
        except Exception:
            todays = []
        
        total_today_hours = sum(t.hours for t in todays)
        self.stat_cards["tasks"].value_label.configure(text=str(len(todays)))
        self.stat_cards["hours"].value_label.configure(text=f"{total_today_hours:.1f}h")
        
        try:
            score = user.productivity_score()
            self.stat_cards["score"].value_label.configure(text=f"{score:.0f}%")
        except Exception:
            self.stat_cards["score"].value_label.configure(text="—")
        
        for w in self.recent_frame.winfo_children():
            w.destroy()
        
        recent = list(user.tasks)[-6:] if getattr(user, "tasks", None) else []
        if not recent:
            ctk.CTkLabel(
                self.recent_frame,
                text="No tasks yet. Start by adding one!",
                text_color=COLORS["text_muted"]
            ).pack(pady=20)
        else:
            for t in reversed(recent):
                task_frame = ctk.CTkFrame(self.recent_frame, fg_color=COLORS["bg_dark"], corner_radius=8)
                task_frame.pack(fill="x", pady=3)
                
                status = "✅" if t.completed else "⏳"
                status_color = COLORS["success"] if t.completed else COLORS["warning"]
                
                left_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
                left_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
                
                ctk.CTkLabel(
                    left_frame,
                    text=f"{status} {t.name}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w"
                ).pack(side="left")
                
                right_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
                right_frame.pack(side="right", padx=15, pady=10)
                
                ctk.CTkLabel(
                    right_frame,
                    text=f"{t.category}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_muted"]
                ).pack(side="left", padx=5)
                
                ctk.CTkLabel(
                    right_frame,
                    text=f"{t.hours:.1f}h",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=status_color
                ).pack(side="left", padx=5)
        
        self.lbl_quote.configure(text=random.choice(QUOTES))

class AddTaskCard(ctk.CTkFrame):
    def __init__(self, parent, dashboard: DashboardPage):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(expand=True)
        
        self.card = ctk.CTkFrame(wrapper, width=700, corner_radius=20, fg_color=COLORS["bg_card"])
        self.card.pack(padx=20, pady=20)
        self.card.grid_propagate(False)
        
        ctk.CTkLabel(
            self.card,
            text="➕ Add New Task",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(25, 5))
        
        ctk.CTkLabel(
            self.card,
            text="Create a new task to track your productivity",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 20))
        
        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        # Task Name
        ctk.CTkLabel(
            form,
            text="Task Name",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.e_name = ctk.CTkEntry(
            form,
            height=45,
            placeholder_text="e.g., Complete project report",
            border_width=2,
            corner_radius=10
        )
        self.e_name.pack(fill="x")
        
        # Category
        ctk.CTkLabel(
            form,
            text="Category",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(15, 5))
        
        self.e_cat = ctk.CTkEntry(
            form,
            height=45,
            placeholder_text="e.g., Work, Study, Personal",
            border_width=2,
            corner_radius=10
        )
        self.e_cat.pack(fill="x")
        
        # Hours and Date row
        row_frame = ctk.CTkFrame(form, fg_color="transparent")
        row_frame.pack(fill="x", pady=(15, 0))
        row_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Hours
        hours_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        hours_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkLabel(
            hours_frame,
            text="Hours",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.e_hours = ctk.CTkEntry(
            hours_frame,
            height=45,
            placeholder_text="e.g., 2.5",
            border_width=2,
            corner_radius=10
        )
        self.e_hours.pack(fill="x")
        
        # Date
        date_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        date_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        ctk.CTkLabel(
            date_frame,
            text="Date",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.e_date = ctk.CTkEntry(
            date_frame,
            height=45,
            placeholder_text="YYYY-MM-DD",
            border_width=2,
            corner_radius=10
        )
        self.e_date.pack(fill="x")
        self.e_date.insert(0, today_iso())
        
        # Completed checkbox
        self.chk_completed = ctk.CTkCheckBox(
            form,
            text="Mark as completed",
            font=ctk.CTkFont(size=13),
            checkbox_height=24,
            checkbox_width=24
        )
        self.chk_completed.pack(anchor="w", pady=(15, 0))
        
        # Add button
        ctk.CTkButton(
            form,
            text="✅ Add Task",
            height=50,
            command=self.add_task,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#059669",
            corner_radius=12
        ).pack(fill="x", pady=(25, 0))
    
    def add_task(self):
        if not self.dashboard.user:
            messagebox.showwarning("No user", "Please login first.")
            return
        
        name = self.e_name.get().strip() or "Untitled"
        cat = self.e_cat.get().strip() or "General"
        
        try:
            hours = float(self.e_hours.get().strip())
        except:
            hours = 0.0
        
        completed = bool(self.chk_completed.get())
        date_s = self.e_date.get().strip()
        
        try:
            datetime.strptime(date_s, "%Y-%m-%d")
        except:
            date_s = today_iso()
        
        t = Task(name, cat, hours, completed, date_s)
        
        try:
            self.dashboard.user.add_task(t)
            messagebox.showinfo("Success", "Task added successfully! ✅")
        except Exception as e:
            messagebox.showerror("Error", f"Could not add task: {e}")
            return
        
        # Clear form
        self.e_name.delete(0, "end")
        self.e_cat.delete(0, "end")
        self.e_hours.delete(0, "end")
        self.e_date.delete(0, "end")
        self.e_date.insert(0, today_iso())
        self.chk_completed.deselect()
        
        # Refresh other pages
        for page_name in ["TasksCard", "AnalyticsCard", "VisualizeCard", "HomeCard"]:
            self.dashboard.pages[page_name].refresh()

class TasksCard(ctk.CTkFrame):
    def __init__(self, parent, dashboard: DashboardPage):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        
        # Main card
        main_card = ctk.CTkFrame(self, corner_radius=20, fg_color=COLORS["bg_card"])
        main_card.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 15))
        
        ctk.CTkLabel(
            header,
            text="📋 Your Tasks",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            command=self.refresh,
            width=100,
            height=35,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["primary"],
            corner_radius=8
        ).pack(side="right")
        
        # Tree container
        tree_container = ctk.CTkFrame(main_card, fg_color=COLORS["bg_dark"], corner_radius=12)
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Treeview with custom styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_light"],
            fieldbackground=COLORS["bg_dark"],
            borderwidth=0,
            rowheight=35
        )
        style.configure("Custom.Treeview.Heading", background=COLORS["primary"], foreground="white", font=("Arial", 11, "bold"))
        style.map("Custom.Treeview", background=[("selected", COLORS["primary"])])
        
        self.tree = ttk.Treeview(
            tree_container,
            columns=("date", "name", "category", "hours", "status"),
            show="headings",
            height=12,
            style="Custom.Treeview"
        )
        
        self.tree.heading("date", text="Date")
        self.tree.heading("name", text="Task")
        self.tree.heading("category", text="Category")
        self.tree.heading("hours", text="Hours")
        self.tree.heading("status", text="Status")
        
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("name", width=350, anchor="w")
        self.tree.column("category", width=150, anchor="center")
        self.tree.column("hours", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        vsb.pack(side="right", fill="y", pady=10)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Mark Completed",
            command=self.mark_completed,
            height=40,
            fg_color=COLORS["success"],
            hover_color="#059669",
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", expand=True, padx=3)
        
        ctk.CTkButton(
            btn_frame,
            text="✏️ Edit",
            command=self.edit_selected,
            height=40,
            fg_color=COLORS["warning"],
            hover_color="#d97706",
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", expand=True, padx=3)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            command=self.delete_selected,
            height=40,
            fg_color=COLORS["danger"],
            hover_color="#dc2626",
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", expand=True, padx=3)
        
        self.refresh()
    
    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        if not self.dashboard.user:
            return
        
        for i, t in enumerate(self.dashboard.user.tasks):
            status = "✅ Done" if t.completed else "⏳ Pending"
            self.tree.insert(
                "",
                "end",
                iid=str(i),
                values=(t.date.isoformat(), t.name, t.category, f"{t.hours:.2f}", status)
            )
    
    def _selected_index(self):
        sel = self.tree.selection()
        if not sel:
            return None
        try:
            return int(sel[0])
        except:
            return None
    
    def mark_completed(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showwarning("Select", "Please select a task")
            return
        
        try:
            self.dashboard.user.update_task(idx, completed=True)
            self.refresh()
            self.dashboard.pages["AnalyticsCard"].refresh()
            self.dashboard.pages["VisualizeCard"].refresh()
            self.dashboard.pages["HomeCard"].refresh()
            messagebox.showinfo("Success", "Task marked as completed! ✅")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def edit_selected(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showwarning("Select", "Please select a task")
            return
        
        try:
            task = self.dashboard.user.tasks[idx]
            EditTaskDialog(self, self.dashboard.user, idx, task, on_save=self.refresh)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open editor: {e}")
    
    def delete_selected(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showwarning("Select", "Please select a task")
            return
        
        if messagebox.askyesno("Delete", "Are you sure you want to delete this task?"):
            try:
                self.dashboard.user.delete_task(idx)
                self.refresh()
                self.dashboard.pages["AnalyticsCard"].refresh()
                self.dashboard.pages["VisualizeCard"].refresh()
                self.dashboard.pages["HomeCard"].refresh()
                messagebox.showinfo("Success", "Task deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {e}")

class EditTaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, user: User, idx: int, task: Task, on_save=None):
        super().__init__(parent)
        self.title("Edit Task")
        self.geometry("550x450")
        self.resizable(False, False)
        
        self.user = user
        self.idx = idx
        self.on_save = on_save
        
        # Main frame
        main = ctk.CTkFrame(self, corner_radius=15, fg_color=COLORS["bg_card"])
        main.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            main,
            text="✏️ Edit Task",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(20, 20))
        
        form = ctk.CTkFrame(main, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Name
        ctk.CTkLabel(form, text="Task Name", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 5))
        self.e_name = ctk.CTkEntry(form, height=40, border_width=2, corner_radius=8)
        self.e_name.pack(fill="x", pady=(0, 15))
        self.e_name.insert(0, task.name)
        
        # Category
        ctk.CTkLabel(form, text="Category", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 5))
        self.e_cat = ctk.CTkEntry(form, height=40, border_width=2, corner_radius=8)
        self.e_cat.pack(fill="x", pady=(0, 15))
        self.e_cat.insert(0, task.category)
        
        # Hours and Date
        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", pady=(0, 15))
        row.grid_columnconfigure((0, 1), weight=1)
        
        hours_f = ctk.CTkFrame(row, fg_color="transparent")
        hours_f.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(hours_f, text="Hours", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 5))
        self.e_hours = ctk.CTkEntry(hours_f, height=40, border_width=2, corner_radius=8)
        self.e_hours.pack(fill="x")
        self.e_hours.insert(0, str(task.hours))
        
        date_f = ctk.CTkFrame(row, fg_color="transparent")
        date_f.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(date_f, text="Date", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 5))
        self.e_date = ctk.CTkEntry(date_f, height=40, border_width=2, corner_radius=8)
        self.e_date.pack(fill="x")
        self.e_date.insert(0, task.date.isoformat())
        
        # Completed
        self.chk_completed = ctk.CTkCheckBox(form, text="Mark as completed", font=ctk.CTkFont(size=13), checkbox_height=22, checkbox_width=22)
        self.chk_completed.pack(anchor="w", pady=(5, 20))
        if task.completed:
            self.chk_completed.select()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save Changes",
            command=self.save,
            height=45,
            fg_color=COLORS["success"],
            hover_color="#059669",
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["text_muted"],
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", expand=True, padx=(5, 0))
    
    def save(self):
        name = self.e_name.get().strip()
        cat = self.e_cat.get().strip()
        
        try:
            hours = float(self.e_hours.get().strip())
        except:
            hours = 0.0
        
        completed = bool(self.chk_completed.get())
        date_s = self.e_date.get().strip()
        
        try:
            datetime.strptime(date_s, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        try:
            self.user.update_task(self.idx, name=name, category=cat, hours=hours, completed=completed, date=date_s)
            if self.on_save:
                self.on_save()
            messagebox.showinfo("Success", "Task updated successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

class AnalyticsCard(ctk.CTkFrame):
    def __init__(self, parent, dashboard: DashboardPage):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # Header card
        header_card = ctk.CTkFrame(scroll, corner_radius=15, fg_color=COLORS["bg_card"])
        header_card.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            header_card,
            text="📊 Analytics Dashboard",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=20)
        
        # Stats grid
        stats_container = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_container.pack(fill="x", padx=15, pady=10)
        stats_container.grid_columnconfigure((0, 1), weight=1)
        
        self.stat_cards = []
        
        # Main stats card
        main_stats = ctk.CTkFrame(stats_container, corner_radius=15, fg_color=COLORS["bg_card"])
        main_stats.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        ctk.CTkLabel(
            main_stats,
            text="Overall Statistics",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        self.summary = ctk.CTkLabel(
            main_stats,
            text="",
            anchor="w",
            justify="left",
            font=ctk.CTkFont(size=13)
        )
        self.summary.pack(fill="x", padx=20, pady=(0, 15), anchor="w")
        
        # Category breakdown
        cat_card = ctk.CTkFrame(stats_container, corner_radius=15, fg_color=COLORS["bg_card"])
        cat_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        ctk.CTkLabel(
            cat_card,
            text="Category Breakdown",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        self.cat_frame = ctk.CTkScrollableFrame(cat_card, height=200, fg_color="transparent")
        self.cat_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Refresh button
        ctk.CTkButton(
            scroll,
            text="🔄 Refresh Analytics",
            command=self.refresh,
            height=45,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        self.refresh()
    
    def refresh(self):
        if not self.dashboard.user:
            self.summary.configure(text="Not logged in")
            return
        
        u = self.dashboard.user
        
        try:
            total = u.total_hours()
            completed = u.total_productive_hours()
            rate = u.completion_rate()
            score = u.productivity_score()
            avg = u.average_time_per_category()
        except Exception as e:
            self.summary.configure(text=f"Analytics error: {e}")
            return
        
        txt = (
            f"📊 Total Hours Logged: {total:.2f}h\n"
            f"✅ Completed Hours: {completed:.2f}h\n"
            f"📈 Completion Rate: {rate:.2f}%\n"
            f"🎯 Productivity Score: {score:.2f}%\n\n"
        )
        
        if score > 80:
            txt += "🔥 Excellent focus! Keep it up!"
        elif score > 50:
            txt += "👍 Good progress — you're on track!"
        else:
            txt += "💪 Keep improving with small steps!"
        
        self.summary.configure(text=txt)
        
        # Category breakdown
        for w in self.cat_frame.winfo_children():
            w.destroy()
        
        if not avg:
            ctk.CTkLabel(
                self.cat_frame,
                text="No category data available",
                text_color=COLORS["text_muted"]
            ).pack(padx=10, pady=20)
        else:
            for k, v in avg.items():
                cat_item = ctk.CTkFrame(self.cat_frame, fg_color=COLORS["bg_dark"], corner_radius=8)
                cat_item.pack(fill="x", pady=4)
                
                ctk.CTkLabel(
                    cat_item,
                    text=k,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                ).pack(side="left", padx=15, pady=10)
                
                ctk.CTkLabel(
                    cat_item,
                    text=f"{v:.2f}h avg",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["primary"]
                ).pack(side="right", padx=15, pady=10)

class VisualizeCard(ctk.CTkFrame):
    def __init__(self, parent, dashboard: DashboardPage):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        
        main_card = ctk.CTkFrame(self, corner_radius=20, fg_color=COLORS["bg_card"])
        main_card.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 15))
        
        ctk.CTkLabel(
            header,
            text="📈 Data Visualization",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Chart type buttons
        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            btn_frame,
            text="📊 Hours by Category",
            command=self.plot_bar,
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=10
        ).pack(side="left", expand=True, padx=3)
        
        ctk.CTkButton(
            btn_frame,
            text="📈 Completed Hours",
            command=self.plot_line,
            height=40,
            fg_color=COLORS["success"],
            hover_color="#059669",
            corner_radius=10
        ).pack(side="left", expand=True, padx=3)
        
        ctk.CTkButton(
            btn_frame,
            text="🥧 Completion Ratio",
            command=self.plot_pie,
            height=40,
            fg_color=COLORS["warning"],
            hover_color="#d97706",
            corner_radius=10
        ).pack(side="left", expand=True, padx=3)
        
        # Canvas holder
        self.canvas_holder = ctk.CTkFrame(main_card, fg_color=COLORS["bg_dark"], corner_radius=12)
        self.canvas_holder.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.refresh()
    
    def refresh(self):
        for w in self.canvas_holder.winfo_children():
            w.destroy()
        
        if not self.dashboard.user or not getattr(self.dashboard.user, "tasks", None):
            ctk.CTkLabel(
                self.canvas_holder,
                text="📊 No data to visualize\nAdd some tasks to see charts here!",
                font=ctk.CTkFont(size=16),
                text_color=COLORS["text_muted"]
            ).pack(expand=True, pady=50)
            return
        
        self.plot_bar()
    
    def _draw_fig(self, fig):
        for w in self.canvas_holder.winfo_children():
            w.destroy()
        
        # Set dark theme for matplotlib
        fig.patch.set_facecolor(COLORS["bg_dark"])
        for ax in fig.get_axes():
            ax.set_facecolor(COLORS["bg_dark"])
            ax.spines['bottom'].set_color(COLORS["text_muted"])
            ax.spines['top'].set_color(COLORS["text_muted"])
            ax.spines['right'].set_color(COLORS["text_muted"])
            ax.spines['left'].set_color(COLORS["text_muted"])
            ax.tick_params(colors=COLORS["text_light"])
            ax.xaxis.label.set_color(COLORS["text_light"])
            ax.yaxis.label.set_color(COLORS["text_light"])
            ax.title.set_color(COLORS["text_light"])
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def plot_bar(self):
        u = self.dashboard.user
        if not u or not u.tasks:
            return
        
        categories = {}
        for t in u.tasks:
            categories[t.category] = categories.get(t.category, 0) + t.hours
        
        keys = list(categories.keys())
        vals = [categories[k] for k in keys]
        
        fig = plt.Figure(figsize=(9, 5))
        ax = fig.add_subplot(111)
        bars = ax.bar(keys, vals, color=COLORS["primary"], alpha=0.8, edgecolor='white', linewidth=1.5)
        ax.set_ylabel("Hours", fontsize=12, fontweight='bold')
        ax.set_title("Hours by Category", fontsize=14, fontweight='bold', pad=20)
        ax.set_xticklabels(keys, rotation=45, ha="right")
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        self._draw_fig(fig)
    
    def plot_line(self):
        u = self.dashboard.user
        if not u or not u.tasks:
            return
        
        daily = {}
        for t in u.tasks:
            if t.completed:
                key = t.date.isoformat() if hasattr(t.date, "isoformat") else str(t.date)
                daily[key] = daily.get(key, 0) + t.hours
        
        if not daily:
            messagebox.showinfo("No Data", "No completed tasks to visualize")
            return
        
        items = sorted(daily.items(), key=lambda x: x[0])
        xs = [i[0] for i in items]
        ys = [i[1] for i in items]
        
        fig = plt.Figure(figsize=(9, 5))
        ax = fig.add_subplot(111)
        ax.plot(xs, ys, marker="o", linewidth=2.5, markersize=8, color=COLORS["success"], markerfacecolor='white', markeredgewidth=2)
        ax.fill_between(range(len(xs)), ys, alpha=0.3, color=COLORS["success"])
        ax.set_ylabel("Completed Hours", fontsize=12, fontweight='bold')
        ax.set_title("Completed Hours Over Time", fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(range(len(xs)))
        ax.set_xticklabels(xs, rotation=45, ha="right")
        ax.grid(True, alpha=0.3, linestyle='--')
        fig.tight_layout()
        self._draw_fig(fig)
    
    def plot_pie(self):
        u = self.dashboard.user
        if not u:
            return
        
        comp = sum(1 for t in u.tasks if t.completed)
        pend = sum(1 for t in u.tasks if not t.completed)
        
        if comp + pend == 0:
            messagebox.showinfo("No Data", "No tasks to visualize")
            return
        
        fig = plt.Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)
        colors = [COLORS["success"], COLORS["warning"]]
        wedges, texts, autotexts = ax.pie(
            [comp, pend],
            labels=["Completed", "Pending"],
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'},
            explode=(0.05, 0)
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
        
        ax.set_title("Task Completion Status", fontsize=14, fontweight='bold', pad=20)
        fig.tight_layout()
        self._draw_fig(fig)

class BackupCard(ctk.CTkFrame):
    def __init__(self, parent, dashboard: DashboardPage):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        
        main_card = ctk.CTkFrame(self, corner_radius=20, fg_color=COLORS["bg_card"])
        main_card.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            main_card,
            text="💾 Backup & Restore",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(25, 10))
        
        ctk.CTkLabel(
            main_card,
            text="Protect your data by creating backups",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 20))
        
        # Action buttons
        btn_container = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_container.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkButton(
            btn_container,
            text="💾 Create Backup",
            command=self.create_backup,
            height=50,
            fg_color=COLORS["success"],
            hover_color="#059669",
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            btn_container,
            text="📁 Restore from File",
            command=self.restore_file,
            height=50,
            fg_color=COLORS["warning"],
            hover_color="#d97706",
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            btn_container,
            text="🔄 Refresh List",
            command=self.refresh,
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["primary"],
            hover_color=COLORS["bg_dark"],
            corner_radius=12,
            font=ctk.CTkFont(size=14)
        ).pack(fill="x", pady=5)
        
        # Backup list
        ctk.CTkLabel(
            main_card,
            text="Available Backups",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 10), padx=30, anchor="w")
        
        list_container = ctk.CTkFrame(main_card, fg_color=COLORS["bg_dark"], corner_radius=12)
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        self.listbox = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh()
    
    def refresh(self):
        for w in self.listbox.winfo_children():
            w.destroy()
        
        try:
            files = os.listdir(DATA_DIR)
        except Exception:
            files = []
        
        backups = [f for f in files if f.startswith("backup_")]
        
        if not backups:
            ctk.CTkLabel(
                self.listbox,
                text="📂 No backups found\nCreate your first backup!",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_muted"]
            ).pack(pady=40)
            return
        
        for b in sorted(backups, reverse=True):
            backup_frame = ctk.CTkFrame(self.listbox, fg_color=COLORS["bg_card"], corner_radius=10)
            backup_frame.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)
            
            ctk.CTkLabel(
                info_frame,
                text="💾 " + b,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            ).pack(anchor="w")
            
            try:
                file_path = os.path.join(DATA_DIR, b)
                size = os.path.getsize(file_path)
                size_text = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} bytes"
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"Size: {size_text}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_muted"],
                    anchor="w"
                ).pack(anchor="w")
            except:
                pass
            
            ctk.CTkButton(
                backup_frame,
                text="Restore",
                width=100,
                height=35,
                command=lambda p=os.path.join(DATA_DIR, b): self._restore(p),
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right", padx=15, pady=12)
    
    def create_backup(self):
        if not self.dashboard.user:
            messagebox.showwarning("No User", "Please login first")
            return
        
        try:
            path = self.dashboard.user.backup()
            if path:
                messagebox.showinfo("Success", f"✅ Backup created successfully!\n\n{os.path.basename(path)}")
                self.refresh()
            else:
                messagebox.showinfo("No Data", "No tasks file to backup")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {e}")
    
    def restore_file(self):
        p = filedialog.askopenfilename(
            initialdir=DATA_DIR,
            title="Select backup file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not p:
            return
        self._restore(p)
    
    def _restore(self, path):
        if not messagebox.askyesno("Confirm Restore", "⚠️ This will replace your current tasks.\nAre you sure?"):
            return
        
        try:
            self.dashboard.user.restore(path)
            messagebox.showinfo("Success", "✅ Data restored successfully!")
            
            # Refresh all pages
            for page_name in ["TasksCard", "AnalyticsCard", "VisualizeCard", "HomeCard"]:
                self.dashboard.pages[page_name].refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {e}")

def run_gui():
    app = FocusFlowApp()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
