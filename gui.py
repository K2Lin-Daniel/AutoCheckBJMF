import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import time
import logging
import traceback
import sys
import os
import schedule
from datetime import datetime, timedelta
from core import ConfigManager, CheckInManager

"""
Tkinter GUI module for AutoCheckBJMF.

This module provides a graphical user interface using the Tkinter framework,
serving as a lightweight and stable alternative to the Flet-based GUI.
"""

# Determine log path based on execution environment
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

log_path = os.path.join(base_dir, 'gui_tk_debug.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger("GUI_TK")

class AutoCheckApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoCheckBJMF - Class Cube (Tkinter)")
        self.root.geometry("900x650")

        # Apply a theme if possible
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')

        self.config_manager = ConfigManager()
        self.checkin_manager = CheckInManager(self.config_manager, log_callback=self.log_callback)

        self.create_widgets()
        self.start_scheduler()

    def create_widgets(self):
        # Navigation (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_tasks = ttk.Frame(self.notebook)
        self.tab_accounts = ttk.Frame(self.notebook)
        self.tab_locations = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text='Dashboard')
        self.notebook.add(self.tab_tasks, text='Tasks')
        self.notebook.add(self.tab_accounts, text='Accounts')
        self.notebook.add(self.tab_locations, text='Locations')
        self.notebook.add(self.tab_settings, text='Settings')

        # Bind events to refresh data when tabs are clicked
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.build_dashboard()
        self.build_tasks()
        self.build_accounts()
        self.build_locations()
        self.build_settings()

    def on_tab_change(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        if tab_name == "Tasks":
            self.refresh_tasks()
        elif tab_name == "Accounts":
            self.refresh_accounts()
        elif tab_name == "Locations":
            self.refresh_locations()

    # --- Dashboard ---
    def build_dashboard(self):
        frame = self.tab_dashboard

        # Header Info
        top_frame = ttk.LabelFrame(frame, text="Status", padding=10)
        top_frame.pack(fill='x', padx=10, pady=5)

        self.lbl_status = ttk.Label(top_frame, text="Next Run In:", font=('Helvetica', 12))
        self.lbl_status.pack(anchor='w')

        self.lbl_countdown = ttk.Label(top_frame, text="-", font=('Helvetica', 24, 'bold'), foreground='blue')
        self.lbl_countdown.pack(anchor='center', pady=10)

        self.lbl_schedule_info = ttk.Label(top_frame, text="Ready")
        self.lbl_schedule_info.pack(anchor='w')

        # Buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill='x', pady=5)

        self.btn_run = ttk.Button(btn_frame, text="Run Check-in Now", command=self.run_manual_checkin)
        self.btn_run.pack(side='left', padx=5)

        self.btn_clear = ttk.Button(btn_frame, text="Clear Logs", command=self.clear_logs)
        self.btn_clear.pack(side='left', padx=5)

        # Logs
        log_frame = ttk.LabelFrame(frame, text="Activity Logs", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.txt_log = scrolledtext.ScrolledText(log_frame, state='disabled', font=('Consolas', 10))
        self.txt_log.pack(fill='both', expand=True)

        # Log Text Tags for colors
        self.txt_log.tag_config('error', foreground='red')
        self.txt_log.tag_config('success', foreground='green')
        self.txt_log.tag_config('normal', foreground='black')

    def log_callback(self, message):
        def _update():
            self.txt_log.config(state='normal')

            tag = 'normal'
            if any(x in message for x in ["❌", "失败", "Error", "无效", "Exception"]):
                tag = 'error'
            elif any(x in message for x in ["✅", "成功", "Finished"]):
                tag = 'success'

            self.txt_log.insert(tk.END, message + "\n", tag)
            self.txt_log.see(tk.END)
            self.txt_log.config(state='disabled')

        self.root.after(0, _update)

    def clear_logs(self):
        self.txt_log.config(state='normal')
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state='disabled')

    def run_manual_checkin(self):
        self.btn_run.config(state='disabled')
        threading.Thread(target=self._run_checkin_thread, daemon=True).start()

    def _run_checkin_thread(self):
        self.log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] Manual run started...")
        try:
            self.checkin_manager.run_job()
            self.log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] Manual run completed.")
        except Exception as e:
            self.log_callback(f"Error: {e}")
            logger.error(traceback.format_exc())

        self.root.after(0, lambda: self.btn_run.config(state='normal'))

    # --- Tasks ---
    def build_tasks(self):
        frame = self.tab_tasks

        btn_frame = ttk.Frame(frame, padding=5)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="Add Task", command=self.add_task).pack(side='left')
        ttk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Toggle Enable", command=self.toggle_task).pack(side='left', padx=5)

        cols = ('Account', 'Location', 'Status')
        self.tree_tasks = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree_tasks.heading(col, text=col)
            self.tree_tasks.column(col, width=150)

        self.tree_tasks.pack(fill='both', expand=True, padx=10, pady=5)

    def refresh_tasks(self):
        for i in self.tree_tasks.get_children():
            self.tree_tasks.delete(i)

        tasks = self.config_manager.get("tasks", [])
        for idx, task in enumerate(tasks):
            status = "Active" if task.get("enable", True) else "Disabled"
            self.tree_tasks.insert('', 'end', iid=idx, values=(
                task.get('account_name', '?'),
                task.get('location_name', '?'),
                status
            ))

    def add_task(self):
        accs = self.config_manager.get("accounts", [])
        locs = self.config_manager.get("locations", [])

        if not accs or not locs:
            messagebox.showwarning("Warning", "Please add Accounts and Locations first.")
            return

        acc_names = [a.get("name") for a in accs]
        loc_names = [l.get("name") for l in locs]

        # Simple Dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Account:").pack(pady=5)
        cb_acc = ttk.Combobox(dialog, values=acc_names, state="readonly")
        cb_acc.pack()

        ttk.Label(dialog, text="Location:").pack(pady=5)
        cb_loc = ttk.Combobox(dialog, values=loc_names, state="readonly")
        cb_loc.pack()

        def save():
            if not cb_acc.get() or not cb_loc.get():
                return
            tasks = self.config_manager.get("tasks", [])
            tasks.append({
                "account_name": cb_acc.get(),
                "location_name": cb_loc.get(),
                "enable": True
            })
            self.config_manager.save_config({"tasks": tasks})
            self.refresh_tasks()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

    def delete_task(self):
        selected = self.tree_tasks.selection()
        if not selected:
            return

        idx = int(selected[0])
        tasks = self.config_manager.get("tasks", [])
        if 0 <= idx < len(tasks):
            del tasks[idx]
            self.config_manager.save_config({"tasks": tasks})
            self.refresh_tasks()

    def toggle_task(self):
        selected = self.tree_tasks.selection()
        if not selected:
            return

        idx = int(selected[0])
        tasks = self.config_manager.get("tasks", [])
        if 0 <= idx < len(tasks):
            tasks[idx]["enable"] = not tasks[idx].get("enable", True)
            self.config_manager.save_config({"tasks": tasks})
            self.refresh_tasks()

    # --- Accounts ---
    def build_accounts(self):
        frame = self.tab_accounts

        btn_frame = ttk.Frame(frame, padding=5)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="Add Account", command=lambda: self.open_account_dialog(-1)).pack(side='left')
        ttk.Button(btn_frame, text="Edit Account", command=self.edit_account).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Account", command=self.delete_account).pack(side='left', padx=5)

        cols = ('Name', 'Class ID', 'Cookie Preview')
        self.tree_accounts = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree_accounts.heading(col, text=col)
        self.tree_accounts.column('Cookie Preview', width=300)

        self.tree_accounts.pack(fill='both', expand=True, padx=10, pady=5)

    def refresh_accounts(self):
        for i in self.tree_accounts.get_children():
            self.tree_accounts.delete(i)

        accounts = self.config_manager.get("accounts", [])
        for idx, acc in enumerate(accounts):
            cookie_short = (acc.get('cookie', '')[:20] + '...') if len(acc.get('cookie', '')) > 20 else acc.get('cookie', '')
            self.tree_accounts.insert('', 'end', iid=idx, values=(
                acc.get('name', ''),
                acc.get('class_id', ''),
                cookie_short
            ))

    def edit_account(self):
        selected = self.tree_accounts.selection()
        if selected:
            self.open_account_dialog(int(selected[0]))

    def open_account_dialog(self, idx):
        accounts = self.config_manager.get("accounts", [])
        is_edit = idx >= 0
        data = accounts[idx] if is_edit else {}

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Account" if is_edit else "Add Account")
        dialog.geometry("400x350")

        ttk.Label(dialog, text="Name:").pack()
        entry_name = ttk.Entry(dialog)
        entry_name.insert(0, data.get("name", ""))
        entry_name.pack(fill='x', padx=10)

        ttk.Label(dialog, text="Class ID:").pack()
        entry_class = ttk.Entry(dialog)
        entry_class.insert(0, data.get("class_id", ""))
        entry_class.pack(fill='x', padx=10)

        ttk.Label(dialog, text="Cookie:").pack()
        txt_cookie = scrolledtext.ScrolledText(dialog, height=5)
        txt_cookie.insert(1.0, data.get("cookie", ""))
        txt_cookie.pack(fill='x', padx=10)

        ttk.Label(dialog, text="Password (Optional):").pack()
        entry_pwd = ttk.Entry(dialog, show="*")
        entry_pwd.insert(0, data.get("pwd", ""))
        entry_pwd.pack(fill='x', padx=10)

        def save():
            new_acc = {
                "name": entry_name.get(),
                "class_id": entry_class.get(),
                "cookie": txt_cookie.get(1.0, tk.END).strip(),
                "pwd": entry_pwd.get()
            }
            if is_edit:
                accounts[idx] = new_acc
            else:
                accounts.append(new_acc)
            self.config_manager.save_config({"accounts": accounts})
            self.refresh_accounts()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

    def delete_account(self):
        selected = self.tree_accounts.selection()
        if not selected:
            return

        idx = int(selected[0])
        accounts = self.config_manager.get("accounts", [])
        if 0 <= idx < len(accounts):
            del accounts[idx]
            self.config_manager.save_config({"accounts": accounts})
            self.refresh_accounts()

    # --- Locations ---
    def build_locations(self):
        frame = self.tab_locations

        btn_frame = ttk.Frame(frame, padding=5)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="Add Location", command=lambda: self.open_location_dialog(-1)).pack(side='left')
        ttk.Button(btn_frame, text="Edit Location", command=self.edit_location).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Location", command=self.delete_location).pack(side='left', padx=5)

        cols = ('Name', 'Lat', 'Lng', 'Acc')
        self.tree_locations = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.tree_locations.heading(col, text=col)

        self.tree_locations.pack(fill='both', expand=True, padx=10, pady=5)

    def refresh_locations(self):
        for i in self.tree_locations.get_children():
            self.tree_locations.delete(i)

        locations = self.config_manager.get("locations", [])
        for idx, loc in enumerate(locations):
            self.tree_locations.insert('', 'end', iid=idx, values=(
                loc.get('name', ''),
                loc.get('lat', ''),
                loc.get('lng', ''),
                loc.get('acc', '')
            ))

    def edit_location(self):
        selected = self.tree_locations.selection()
        if selected:
            self.open_location_dialog(int(selected[0]))

    def open_location_dialog(self, idx):
        locations = self.config_manager.get("locations", [])
        is_edit = idx >= 0
        data = locations[idx] if is_edit else {}

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Location" if is_edit else "Add Location")
        dialog.geometry("300x250")

        ttk.Label(dialog, text="Name:").pack()
        entry_name = ttk.Entry(dialog)
        entry_name.insert(0, data.get("name", ""))
        entry_name.pack(fill='x', padx=10)

        ttk.Label(dialog, text="Latitude:").pack()
        entry_lat = ttk.Entry(dialog)
        entry_lat.insert(0, data.get("lat", ""))
        entry_lat.pack(fill='x', padx=10)

        ttk.Label(dialog, text="Longitude:").pack()
        entry_lng = ttk.Entry(dialog)
        entry_lng.insert(0, data.get("lng", ""))
        entry_lng.pack(fill='x', padx=10)

        ttk.Label(dialog, text="Accuracy:").pack()
        entry_acc = ttk.Entry(dialog)
        entry_acc.insert(0, data.get("acc", "0.0"))
        entry_acc.pack(fill='x', padx=10)

        def save():
            new_loc = {
                "name": entry_name.get(),
                "lat": entry_lat.get(),
                "lng": entry_lng.get(),
                "acc": entry_acc.get()
            }
            if is_edit:
                locations[idx] = new_loc
            else:
                locations.append(new_loc)
            self.config_manager.save_config({"locations": locations})
            self.refresh_locations()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).pack(pady=10)

    def delete_location(self):
        selected = self.tree_locations.selection()
        if not selected:
            return

        idx = int(selected[0])
        locations = self.config_manager.get("locations", [])
        if 0 <= idx < len(locations):
            del locations[idx]
            self.config_manager.save_config({"locations": locations})
            self.refresh_locations()

    # --- Settings ---
    def build_settings(self):
        frame = self.tab_settings
        wecom = self.config_manager.get("wecom", {})

        ttk.Label(frame, text="Global Settings", font=('Helvetica', 14)).pack(pady=10)

        grid_frame = ttk.Frame(frame)
        grid_frame.pack(padx=20, pady=10)

        ttk.Label(grid_frame, text="Schedule Time (HH:MM):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.entry_sched = ttk.Entry(grid_frame)
        self.entry_sched.insert(0, self.config_manager.get("scheduletime", "08:00"))
        self.entry_sched.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(grid_frame, text="WeCom CorpID:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.entry_corpid = ttk.Entry(grid_frame)
        self.entry_corpid.insert(0, wecom.get("corpid", ""))
        self.entry_corpid.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(grid_frame, text="WeCom Secret:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.entry_secret = ttk.Entry(grid_frame, show="*")
        self.entry_secret.insert(0, wecom.get("secret", ""))
        self.entry_secret.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(grid_frame, text="WeCom AgentID:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.entry_agentid = ttk.Entry(grid_frame)
        self.entry_agentid.insert(0, wecom.get("agentid", ""))
        self.entry_agentid.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(grid_frame, text="WeCom ToUser:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.entry_touser = ttk.Entry(grid_frame)
        self.entry_touser.insert(0, wecom.get("touser", "@all"))
        self.entry_touser.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        self.var_debug = tk.BooleanVar(value=self.config_manager.get("debug", False))
        ttk.Checkbutton(grid_frame, text="Enable Debug Logging", variable=self.var_debug).grid(row=5, column=1, sticky='w', pady=10)

        ttk.Button(frame, text="Save Settings", command=self.save_settings).pack(pady=10)

    def save_settings(self):
        new_conf = {
            "scheduletime": self.entry_sched.get(),
            "wecom": {
                "corpid": self.entry_corpid.get(),
                "secret": self.entry_secret.get(),
                "agentid": self.entry_agentid.get(),
                "touser": self.entry_touser.get()
            },
            "debug": self.var_debug.get()
        }
        self.config_manager.save_config(new_conf)
        self.update_scheduler_job()
        messagebox.showinfo("Success", "Settings saved successfully.")

    # --- Scheduler ---
    def start_scheduler(self):
        self.update_scheduler_job()
        threading.Thread(target=self._scheduler_loop, daemon=True).start()

    def update_scheduler_job(self):
        schedule.clear()
        time_str = self.config_manager.get("scheduletime", "08:00")
        try:
            datetime.strptime(time_str, "%H:%M")
            schedule.every().day.at(time_str).do(self._scheduled_job)
            self.lbl_schedule_info.config(text=f"Scheduled daily at {time_str}")
        except ValueError:
            self.lbl_schedule_info.config(text="Invalid time format (HH:MM)")

    def _scheduled_job(self):
        threading.Thread(target=self._run_job_thread, daemon=True).start()

    def _run_job_thread(self):
        self.log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] Starting scheduled check-in...")
        try:
            self.checkin_manager.run_job()
            self.log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduled check-in finished.")
        except Exception as e:
            self.log_callback(f"Error during scheduled job: {e}")
            logger.error(traceback.format_exc())

    def _scheduler_loop(self):
        while True:
            schedule.run_pending()
            # Update countdown
            self.root.after(0, self._update_countdown)
            time.sleep(1)

    def _update_countdown(self):
        time_str = self.config_manager.get("scheduletime")
        if not time_str:
            return
        try:
            target_time = datetime.strptime(time_str, "%H:%M").time()
            now = datetime.now()
            target_dt = datetime.combine(now.date(), target_time)
            if target_dt < now:
                target_dt += timedelta(days=1)
            diff = target_dt - now
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.lbl_countdown.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        except:
            pass

if __name__ == "__main__":
    # Standard Tkinter boilerplate
    root = tk.Tk()
    app = AutoCheckApp(root)
    root.mainloop()
