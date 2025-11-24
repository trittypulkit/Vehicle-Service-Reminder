import json
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = "vehicle_service.json"

# ---------------------------
# Helper Functions
# ---------------------------

def get_data_path():
    # Store data file next to script if packaged, else use working dir
    return os.path.join(os.path.dirname(__file__), DATA_FILE)

def load_data():
    path = get_data_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_data(data):
    path = get_data_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def next_service_date(last_service_date):
    last = datetime.strptime(last_service_date, "%Y-%m-%d")
    next_date = last + timedelta(days=365)   # 1 year
    return next_date.strftime("%Y-%m-%d")

def next_service_km(last_km):
    return int(last_km) + 10000

def days_remaining(target_date):
    today = datetime.today()
    t = datetime.strptime(target_date, "%Y-%m-%d")
    return (t - today).days

def status_message(date_due, km_due, current_km):
    days_left = days_remaining(date_due)
    km_left = km_due - current_km

    # Overdue (when either condition passes)
    if days_left < 0 or km_left < 0:
        return "⚠️ SERVICE OVERDUE"
    elif days_left == 0 or km_left == 0:
        return "⚠️ SERVICE DUE TODAY"
    elif days_left <= 7 or km_left <= 500:
        return f"⏳ DUE SOON (Time left: {days_left} days, KM left: {km_left})"
    else:
        return f"✓ OK (Time left: {days_left} days, KM left: {km_left})"


# ---------------------------
# GUI Application
# ---------------------------

class VehicleServiceApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Service Reminder")
        self.root.geometry("820x620")
        self.root.resizable(False, False)

        title = ttk.Label(root, text="Vehicle Service Reminder System", 
                          font=("Segoe UI", 18, "bold"))
        title.pack(pady=12)

        tabs = ttk.Notebook(root)
        self.tab_add = ttk.Frame(tabs)
        self.tab_view = ttk.Frame(tabs)
        self.tab_update = ttk.Frame(tabs)
        self.tab_tools = ttk.Frame(tabs)

        tabs.add(self.tab_add, text="Add Vehicle")
        tabs.add(self.tab_view, text="View Reminders")
        tabs.add(self.tab_update, text="Update Service")
        tabs.add(self.tab_tools, text="Tools")
        tabs.pack(fill="both", expand=1)

        self.build_add_tab()
        self.build_view_tab()
        self.build_update_tab()
        self.build_tools_tab()

    # ---------------------------
    # Add Vehicle Tab
    # ---------------------------

    def build_add_tab(self):
        frame = ttk.Frame(self.tab_add, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Vehicle Number:").grid(row=0, column=0, sticky="w")
        self.add_vehicle_no = ttk.Entry(frame, width=30)
        self.add_vehicle_no.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(frame, text="Last Service Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.add_last_date = ttk.Entry(frame, width=30)
        self.add_last_date.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(frame, text="Last Service KM:").grid(row=2, column=0, sticky="w")
        self.add_last_km = ttk.Entry(frame, width=30)
        self.add_last_km.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(frame, text="Current KM:").grid(row=3, column=0, sticky="w")
        self.add_current_km = ttk.Entry(frame, width=30)
        self.add_current_km.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        add_btn = ttk.Button(frame, text="Add Vehicle", command=self.add_vehicle)
        add_btn.grid(row=4, column=0, columnspan=2, pady=12)

        note = ttk.Label(frame, text="Note: Next service = last service + 10,000 km OR +1 year (whichever comes first).")
        note.grid(row=5, column=0, columnspan=2, pady=8)

    def add_vehicle(self):
        vehicle = self.add_vehicle_no.get().strip()
        last_date = self.add_last_date.get().strip()
        last_km = self.add_last_km.get().strip()
        current_km = self.add_current_km.get().strip()

        if not (vehicle and last_date and last_km and current_km):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            # Validate date format
            datetime.strptime(last_date, "%Y-%m-%d")
            last_km_i = int(last_km)
            current_km_i = int(current_km)
            if current_km_i < last_km_i:
                messagebox.showwarning("Warning", "Current KM is less than last service KM. Please check values.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        next_date = next_service_date(last_date)
        next_km = next_service_km(last_km_i)

        data = load_data()
        data[vehicle] = {
            "last_service_date": last_date,
            "last_service_km": last_km_i,
            "current_km": current_km_i,
            "next_service_date": next_date,
            "next_service_km": next_km
        }
        save_data(data)

        messagebox.showinfo("Success", f"Vehicle added!\nNext Service: {next_date} OR {next_km} km")
        self.clear_add_fields()

    def clear_add_fields(self):
        self.add_vehicle_no.delete(0, tk.END)
        self.add_last_date.delete(0, tk.END)
        self.add_last_km.delete(0, tk.END)
        self.add_current_km.delete(0, tk.END)

    # ---------------------------
    # View Reminders Tab
    # ---------------------------

    def build_view_tab(self):
        top = ttk.Frame(self.tab_view)
        top.pack(fill="x", pady=6)
        ttk.Button(top, text="Refresh", command=self.display_reminders).pack(side="left", padx=8)
        ttk.Button(top, text="Export as CSV", command=self.export_csv).pack(side="left", padx=8)
        ttk.Button(top, text="Load sample data", command=self.load_sample_data).pack(side="left", padx=8)

        self.reminder_box = tk.Text(self.tab_view, width=100, height=30, font=("Consolas", 10))
        self.reminder_box.pack(padx=8, pady=8)

        self.display_reminders()

    def display_reminders(self):
        self.reminder_box.delete(1.0, tk.END)
        data = load_data()

        if not data:
            self.reminder_box.insert(tk.END, "No vehicle data found. Use 'Load sample data' to create demo entries.")
            return

        for vehicle, info in sorted(data.items()):
            status = status_message(
                info["next_service_date"],
                info["next_service_km"],
                info["current_km"]
            )

            self.reminder_box.insert(tk.END,
                f"Vehicle: {vehicle}\n"
                f"  Last Service Date : {info['last_service_date']}\n"
                f"  Last Service KM   : {info['last_service_km']}\n"
                f"  Current KM        : {info['current_km']}\n"
                f"  Next Service Date : {info['next_service_date']}\n"
                f"  Next Service KM   : {info['next_service_km']}\n"
                f"  Status            : {status}\n"
                f"{'-'*90}\n"
            )

    def export_csv(self):
        data = load_data()
        if not data:
            messagebox.showinfo("Info", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not file_path:
            return
        with open(file_path, "w") as f:
            f.write("vehicle,last_service_date,last_service_km,current_km,next_service_date,next_service_km\n")
            for v,i in data.items():
                f.write(f'{v},{i["last_service_date"]},{i["last_service_km"]},{i["current_km"]},{i["next_service_date"]},{i["next_service_km"]}\n')
        messagebox.showinfo("Exported", f"CSV exported to: {file_path}")

    def load_sample_data(self):
        sample = {
            "MH01AB1234": {
                "last_service_date": "2024-11-01",
                "last_service_km": 12000,
                "current_km": 21000,
                "next_service_date": next_service_date("2024-11-01"),
                "next_service_km": next_service_km(12000)
            },
            "DL8CAF0001": {
                "last_service_date": "2024-06-15",
                "last_service_km": 45000,
                "current_km": 54050,
                "next_service_date": next_service_date("2024-06-15"),
                "next_service_km": next_service_km(45000)
            }
        }
        save_data(sample)
        messagebox.showinfo("Sample Data", "Sample data saved to vehicle_service.json")
        self.display_reminders()

    # ---------------------------
    # Update Service Tab
    # ---------------------------

    def build_update_tab(self):
        frame = ttk.Frame(self.tab_update, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Vehicle Number:").grid(row=0, column=0, sticky="w")
        self.update_vehicle_no = ttk.Entry(frame, width=30)
        self.update_vehicle_no.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(frame, text="New Last Service Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.update_last_date = ttk.Entry(frame, width=30)
        self.update_last_date.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(frame, text="New Last Service KM:").grid(row=2, column=0, sticky="w")
        self.update_last_km = ttk.Entry(frame, width=30)
        self.update_last_km.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(frame, text="Current KM:").grid(row=3, column=0, sticky="w")
        self.update_current_km = ttk.Entry(frame, width=30)
        self.update_current_km.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        ttk.Button(frame, text="Update Service", command=self.update_vehicle).grid(row=4, column=0, columnspan=2, pady=12)

    def update_vehicle(self):
        vehicle = self.update_vehicle_no.get().strip()
        new_date = self.update_last_date.get().strip()
        new_km = self.update_last_km.get().strip()
        current_km = self.update_current_km.get().strip()

        data = load_data()

        if vehicle not in data:
            messagebox.showerror("Error", "Vehicle not found!")
            return

        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            new_km_i = int(new_km)
            current_km_i = int(current_km)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        next_date = next_service_date(new_date)
        next_km = next_service_km(new_km_i)

        data[vehicle] = {
            "last_service_date": new_date,
            "last_service_km": new_km_i,
            "current_km": current_km_i,
            "next_service_date": next_date,
            "next_service_km": next_km
        }

        save_data(data)
        messagebox.showinfo("Success", "Vehicle record updated!")
        self.display_reminders()
        # clear fields
        self.update_vehicle_no.delete(0, tk.END)
        self.update_last_date.delete(0, tk.END)
        self.update_last_km.delete(0, tk.END)
        self.update_current_km.delete(0, tk.END)

    # ---------------------------
    # Tools Tab
    # ---------------------------

    def build_tools_tab(self):
        frame = ttk.Frame(self.tab_tools, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Backup / Restore").grid(row=0, column=0, sticky="w")
        ttk.Button(frame, text="Backup JSON", command=self.backup_json).grid(row=1, column=0, pady=6, sticky="w")
        ttk.Button(frame, text="Restore JSON", command=self.restore_json).grid(row=1, column=1, pady=6, sticky="w")

        ttk.Label(frame, text="Clear all data").grid(row=3, column=0, sticky="w", pady=(12,0))
        ttk.Button(frame, text="Clear Data", command=self.clear_data).grid(row=4, column=0, pady=6, sticky="w")

    def backup_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if not path:
            return
        data = load_data()
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Backup", f"Backup saved to {path}")

    def restore_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if not path:
            return
        with open(path, "r") as f:
            data = json.load(f)
        save_data(data)
        messagebox.showinfo("Restore", "Data restored from selected file")
        self.display_reminders()

    def clear_data(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to permanently delete all records?"):
            save_data({})
            messagebox.showinfo("Cleared", "All data cleared")
            self.display_reminders()


# ---------------------------
# Run App
# ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleServiceApp(root)
    root.mainloop()