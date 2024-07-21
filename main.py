import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import threading
import re

error_log = ""
selected_file = ""

def show_error_log():
    if not hasattr(show_error_log, 'log_window') or not show_error_log.log_window.winfo_exists():
        show_error_log.log_window = tk.Toplevel(root)
        show_error_log.log_window.title("Live Log")
        show_error_log.log_window.geometry("500x300")
        
        global log_text
        log_text = scrolledtext.ScrolledText(show_error_log.log_window, wrap=tk.WORD)
        log_text.pack(expand=True, fill='both')
        log_text.insert(tk.END, error_log)
        log_text.config(state='disabled')
    else:
        show_error_log.log_window.deiconify()

def run_auto_editor():
    global error_log
    if selected_file:
        result_label.config(text="Processing...")
        
        def process():
            global error_log
            custom_params = custom_params_entry.get().strip()
            command = f"auto-editor \"{selected_file.strip('{}')}\""
            if custom_params:
                command += f" {custom_params}"
            try:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                for line in process.stdout:
                    root.after(0, lambda l=line: update_log(l))
                process.wait()
                if process.returncode == 0:
                    root.after(0, lambda: complete_process("Auto-editing complete!"))
                else:
                    error_output = process.stderr.read()
                    clean_error = re.sub(r'\x1b\[[0-9;]*[mK]', '', error_output)
                    error_log = clean_error.strip()
                    root.after(0, lambda: complete_process("Error occurred. Check log for details."))
            except Exception as e:
                error_log = str(e)
                root.after(0, lambda: complete_process("Error occurred. Check log for details."))

        threading.Thread(target=process, daemon=True).start()
    else:
        result_label.config(text="No file selected.")

def update_log(line):
    if any(phrase in line for phrase in [
        "Extracting audio", 
        "Analyzing audio volume", 
        "Creating new audio", 
        "Creating new video"
    ]):
        return

    log_text.config(state='normal')
    log_text.insert(tk.END, line)
    log_text.see(tk.END)
    log_text.config(state='disabled')

def complete_process(message):
    result_label.config(text=message)

def on_drop(event):
    global selected_file
    selected_file = event.data
    file_label.config(text=f"Selected file: {selected_file}")

def on_select_file():
    global selected_file
    selected_file = filedialog.askopenfilename(title="Select input video file")
    if selected_file:
        file_label.config(text=f"Selected file: {selected_file}")

root = TkinterDnD.Tk()
root.title("Auto-Editor GUI (Made by Yazan)")
root.geometry("400x300")
root.configure(bg="#f0f0f0")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

title_label = tk.Label(root, text="Auto-Editor", font=("Arial", 24, "bold"), bg="#f0f0f0")
title_label.pack(pady=5)

select_button = ttk.Button(root, text="Select Video File", command=on_select_file, style="TButton")
select_button.pack(pady=2)

drop_label = tk.Label(root, text="Or drag and drop video here", bg="#e0e0e0", width=30, height=2)
drop_label.pack(pady=2)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', on_drop)

file_label = tk.Label(root, text="No file selected", bg="#f0f0f0")
file_label.pack(pady=2)

custom_params_label = tk.Label(root, text="Custom Parameters:", bg="#f0f0f0")
custom_params_label.pack(pady=2)
custom_params_entry = tk.Entry(root, width=40)
custom_params_entry.pack(pady=2)

result_label = tk.Label(root, text="", font=("Arial", 12), bg="#f0f0f0")
result_label.pack(pady=2)

button_frame = tk.Frame(root)
button_frame.pack(side='bottom', pady=2)

start_button = ttk.Button(button_frame, text="Start Auto-Editing", command=run_auto_editor, style="TButton")
start_button.pack(side='bottom', padx=5)

show_log_button = ttk.Button(button_frame, text="Show Live Log", command=show_error_log, style="TButton")
show_log_button.pack(side='top', padx=5)

root.mainloop()