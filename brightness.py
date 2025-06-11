import os
import glob
import tkinter as tk
from tkinter import messagebox

timeout = 400

def get_backlight_path():
    dirs = glob.glob("/sys/class/backlight/*")
    if not dirs:
        raise FileNotFoundError("No backlight interface found.")
    return os.path.join(dirs[0], "brightness")

brightness_path = get_backlight_path()

def get_brightness():
    try:
        with open(brightness_path, "r") as f:
            return int(f.read().strip())
    except Exception as e:
        messagebox.showerror("Error", f"Could not read brightness: {e}")
        return 0

def set_brightness(value):
    try:
        v = max(0, min(int(float(value)), 50))
        os.system(f"echo {v} | sudo tee {brightness_path} > /dev/null")
    except Exception as e:
        messagebox.showerror("Error", f"Could not set brightness: {e}")

def show_slider():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    ww, wh = 270, 50
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = sw - ww, sh - wh - 41
    root.geometry(f"{ww}x{wh}+{x}+{y}")
    root.update_idletasks()
    c = tk.Canvas(root, width=ww, height=wh, bg="#f0f0f0", highlightthickness=0)
    c.pack()
    track_len = 250
    start = (15, wh // 2)
    end = (start[0] + track_len, start[1])
    c.create_line(start, end, fill="#cccccc", width=4, capstyle=tk.ROUND)
    r = 10
    curr = get_brightness()
    knob_x = start[0] + (curr / 50) * track_len
    knob = c.create_oval(knob_x - r, start[1] - r, knob_x + r, start[1] + r,
                         fill="#4a90e2", outline="")
    close_after_id = None
    entered = False

    def cancel_close(event=None):
        nonlocal close_after_id, entered
        if close_after_id:
            root.after_cancel(close_after_id)
            close_after_id = None
        entered = True

    def schedule_close():
        nonlocal close_after_id
        if not entered:
            return
        if close_after_id:
            root.after_cancel(close_after_id)
        close_after_id = root.after(timeout, root.destroy)

    def move_knob(evt):
        x = min(max(evt.x, start[0]), end[0])
        c.coords(knob, x - r, start[1] - r, x + r, start[1] + r)
        b = int(((x - start[0]) / track_len) * 50)
        set_brightness(b)

    c.bind("<Button-1>", move_knob)
    c.bind("<B1-Motion>", move_knob)
    c.bind("<Enter>", cancel_close)
    c.bind("<Leave>", lambda e: schedule_close())
    root.bind("<Enter>", cancel_close)
    root.bind("<Leave>", lambda e: schedule_close())
    schedule_close()
    root.mainloop()

if __name__ == "__main__":
    show_slider()

