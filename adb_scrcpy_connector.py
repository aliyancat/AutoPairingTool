import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class ADBScrcpyConnector:
    def __init__(self, root):
        self.root = root
        self.root.title("ADB Scrcpy Connector")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="ADB Pairing & Scrcpy Setup",
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(main_frame, text="Port Number 1:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.port1_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.port1_var, width=20).grid(row=1, column=1)

        ttk.Label(main_frame, text="WiFi Pairing Code:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.pairing_code_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.pairing_code_var, width=20).grid(row=2, column=1)

        ttk.Label(main_frame, text="Port Number 2:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.port2_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.port2_var, width=20).grid(row=3, column=1)

        ttk.Label(main_frame, text="Connection Mode:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.mode_var = tk.StringVar(value="wireless")

        ttk.Radiobutton(main_frame, text="Wireless", variable=self.mode_var, value="wireless").grid(row=4, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="USB", variable=self.mode_var, value="usb").grid(row=5, column=1, sticky=tk.W)

        self.start_button = ttk.Button(main_frame, text="Start Connection", command=self.start_process)
        self.start_button.grid(row=6, column=0, columnspan=2, pady=30)

        root.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    # ---------------- FIXED COMMAND RUNNER ----------------
    def run_command(self, cmd, input_data=None):
        try:
            print(f"\n>>> Running: {cmd}")

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output, error = process.communicate(input=input_data, timeout=60)

            print(output)
            if error:
                print("ERROR:", error)

            return process.returncode == 0

        except Exception as e:
            print("Exception:", e)
            return False

    # ---------------- MAIN PROCESS ----------------
    def start_process(self):
        port1 = self.port1_var.get()
        pairing_code = self.pairing_code_var.get()
        port2 = self.port2_var.get()
        mode = self.mode_var.get()

        if not port1 or not pairing_code or not port2:
            messagebox.showerror("Error", "Fill all fields")
            return

        self.start_button.config(state="disabled", text="Connecting...")

        thread = threading.Thread(
            target=self.execute_process,
            args=(port1, pairing_code, port2, mode),
            daemon=True
        )
        thread.start()

    def execute_process(self, port1, pairing_code, port2, mode):

        ip_addr = "192.168.1.25"

        try:
            print("\n==============================")
            print("ADB SCRCPY STARTED")
            print("==============================")

            # STEP 1: Pair
            print("\n[STEP 1] Pairing...")
            self.run_command(
                ["adb", "pair", f"{ip_addr}:{port1}"],
                input_data=pairing_code + "\n"
            )

            # STEP 2: Connect
            print("\n[STEP 2] Connecting...")
            self.run_command(
                ["adb", "connect", f"{ip_addr}:{port2}"]
            )

            # STEP 3: Scrcpy
            print("\n[STEP 3] Starting Scrcpy...")

            scrcpy_path = r"C:\Users\pc\Downloads\scrcpy-win64-v3.3.1"

            if mode == "wireless":
                cmd = f'cd /d "{scrcpy_path}" && scrcpy -s {ip_addr}:{port2}'
            else:
                cmd = f'cd /d "{scrcpy_path}" && scrcpy -d'

            subprocess.Popen(cmd, shell=True)

            print("\nDONE!")

            messagebox.showinfo("Success", "Connected successfully!")

        except Exception as e:
            print("ERROR:", e)
            messagebox.showerror("Error", str(e))

        finally:
            self.start_button.config(state="normal", text="Start Connection")


if __name__ == "__main__":
    root = tk.Tk()
    app = ADBScrcpyConnector(root)
    root.mainloop()