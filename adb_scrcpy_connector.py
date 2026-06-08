import os
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
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="ADB Pairing & Scrcpy Setup", 
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Port 1 (Pairing Port)
        ttk.Label(main_frame, text="Port Number 1:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.port1_var = tk.StringVar()
        port1_entry = ttk.Entry(main_frame, textvariable=self.port1_var, width=20, font=("Arial", 11))
        port1_entry.grid(row=1, column=1, sticky=tk.W, padx=10)
        port1_entry.focus()
        
        # Pairing Code
        ttk.Label(main_frame, text="WiFi Pairing Code:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=10)
        self.pairing_code_var = tk.StringVar()
        code_entry = ttk.Entry(main_frame, textvariable=self.pairing_code_var, width=20, font=("Arial", 11))
        code_entry.grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Port 2 (Connect Port)
        ttk.Label(main_frame, text="Port Number 2:", font=("Arial", 11)).grid(row=3, column=0, sticky=tk.W, pady=10)
        self.port2_var = tk.StringVar()
        port2_entry = ttk.Entry(main_frame, textvariable=self.port2_var, width=20, font=("Arial", 11))
        port2_entry.grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Connection Mode (Wireless or USB)
        ttk.Label(main_frame, text="Connection Mode:", font=("Arial", 11)).grid(row=4, column=0, sticky=tk.W, pady=10)
        self.mode_var = tk.StringVar(value="wireless")
        wireless_radio = ttk.Radiobutton(main_frame, text="Wireless", variable=self.mode_var, value="wireless")
        wireless_radio.grid(row=4, column=1, sticky=tk.W, padx=10)
        usb_radio = ttk.Radiobutton(main_frame, text="USB", variable=self.mode_var, value="usb")
        usb_radio.grid(row=5, column=1, sticky=tk.W, padx=10)
        
        # Start Button
        self.start_button = ttk.Button(main_frame, text="Start Connection", command=self.start_process)
        self.start_button.grid(row=6, column=0, columnspan=2, pady=30)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def run_command(self, command, input_text=None, wait=True):
        """Run a command with optional input"""
        try:
            print(f"\n>>> Running: {command}")
            if wait:
                if input_text:
                    result = subprocess.run(command, shell=True, input=input_text, text=True, timeout=30)
                else:
                    result = subprocess.run(command, shell=True, text=True, timeout=30)
                print(f">>> Command completed with code: {result.returncode}")
                return result.returncode == 0
            else:
                subprocess.Popen(command, shell=True)
                print(">>> Command started in background")
                return True
        except Exception as e:
            print(f">>> Error: {e}")
            return False
    
    def start_process(self):
        """Main process thread"""
        # Validate inputs
        port1 = self.port1_var.get()
        pairing_code = self.pairing_code_var.get()
        port2 = self.port2_var.get()
        mode = self.mode_var.get()
        
        if not port1 or not pairing_code or not port2:
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        
        # Disable button during process
        self.start_button.config(state="disabled")
        self.start_button.config(text="Connecting...")
        
        # Run process in separate thread
        thread = threading.Thread(target=self.execute_process, args=(port1, pairing_code, port2, mode))
        thread.daemon = True
        thread.start()
    
    def execute_process(self, port1, pairing_code, port2, mode):
        """Execute the full process"""
        try:
            ip_addr = "192.168.1.25"
            
            print(f"\n{'='*50}")
            print("ADB Pairing & Scrcpy Connection Started")
            print(f"{'='*50}")
            print(f"Mode: {mode.upper()}")
            print(f"IP Address: {ip_addr}")
            print(f"Port 1 (Pairing): {port1}")
            print(f"Port 2 (Connect): {port2}")
            
            # Step 1: ADB Pair (with pairing code input)
            print(f"\n[STEP 1] ADB Pairing...")
            cmd_pair = f"adb pair {ip_addr}:{port1}"
            self.run_command(cmd_pair, input_text=pairing_code + "\n")
            
            # Step 2: ADB Connect
            print(f"\n[STEP 2] ADB Connect...")
            cmd_connect = f"adb connect {ip_addr}:{port2}"
            self.run_command(cmd_connect)
            
            # Step 3: Run Scrcpy (different command based on mode)
            print(f"\n[STEP 3] Starting Scrcpy ({mode.upper()})...")
            scrcpy_path = r"C:\Users\pc\Downloads\scrcpy-win64-v3.3.1"
            
            if mode == "wireless":
                cmd_scrcpy = f'cd /d "{scrcpy_path}" && scrcpy -s {ip_addr}:{port2}'
            else:  # USB mode
                cmd_scrcpy = f'cd /d "{scrcpy_path}" && scrcpy -d'
            
            self.run_command(cmd_scrcpy, wait=False)

            # Step 4: Launch OBS
            print(f"\n[STEP 4] Launching OBS...")
            obs_path = r"C:\Program Files\obs-studio\bin\64bit"
            cmd_obs = f'cd /d "{obs_path}" && obs64.exe'
            self.run_command(cmd_obs, wait=False)
            
            print(f"\n{'='*50}")
            print("Process Complete! Scrcpy and OBS are starting.")
            print(f"{'='*50}\n")
            messagebox.showinfo("Success", "Connection started successfully and OBS was launched!")
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}\n")
            messagebox.showerror("Error", f"Error: {str(e)}")
        finally:
            self.start_button.config(state="normal")
            self.start_button.config(text="Start Connection")

if __name__ == "__main__":
    root = tk.Tk()
    app = ADBScrcpyConnector(root)
    root.mainloop()