import os
import glob
import tkinter as tk
from tkinter import messagebox

def get_backlight_path():
    backlight_dirs = glob.glob("/sys/class/backlight/*")
    if backlight_dirs:
        return os.path.join(backlight_dirs[0], "brightness")
    raise FileNotFoundError("No backlight interface found.")

BRIGHTNESS_PATH = get_backlight_path()

def get_brightness():
    try:
        with open(BRIGHTNESS_PATH, "r") as f:
            return int(f.read().strip())
    except Exception as e:
        messagebox.showerror("Error", f"Could not read brightness: {e}")
        return 0

def set_brightness(value):
    try:
        brightness = max(0, min(int(float(value)), 50))
        os.system(f"echo {brightness} | sudo tee {BRIGHTNESS_PATH} > /dev/null")
    except Exception as e:
        messagebox.showerror("Error", f"Could not set brightness: {e}")

def show_slider():
    slider_window = tk.Tk()
    slider_window.overrideredirect(True)
    screen_width = slider_window.winfo_screenwidth()
    screen_height = slider_window.winfo_screenheight()
    window_width = 270
    window_height = 50
    x_position = screen_width - window_width
    y_position = screen_height - window_height - 41
    slider_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    canvas = tk.Canvas(slider_window, width=window_width, height=window_height, bg="#f0f0f0", highlightthickness=0)
    canvas.pack()
    track_length = 250
    track_start = (15, window_height // 2)
    track_end = (track_start[0] + track_length, track_start[1])
    canvas.create_line(track_start, track_end, fill="#cccccc", width=4, capstyle=tk.ROUND)
    knob_radius = 10
    current_brightness = get_brightness()
    knob_x = track_start[0] + (current_brightness / 50) * track_length
    knob = canvas.create_oval(knob_x - knob_radius, track_start[1] - knob_radius, knob_x + knob_radius, track_start[1] + knob_radius, fill="#4a90e2", outline="")
    close_timer = None
    interaction_occurred = False

    def reset_timer():
        nonlocal close_timer
        if close_timer:
            slider_window.after_cancel(close_timer)
        close_timer = slider_window.after(3600, check_and_close)

    def check_and_close():
        nonlocal interaction_occurred
        if interaction_occurred:
            slider_window.destroy()

    def move_knob(event):
        nonlocal interaction_occurred
        x = min(max(event.x, track_start[0]), track_end[0])
        canvas.coords(knob, x - knob_radius, track_start[1] - knob_radius, x + knob_radius, track_start[1] + knob_radius)
        brightness = int(((x - track_start[0]) / track_length) * 50)
        set_brightness(brightness)
        interaction_occurred = True
        reset_timer()

    canvas.bind("<Button-1>", move_knob)

    def drag_knob(event):
        if track_start[0] <= event.x <= track_end[0]:
            move_knob(event)

    canvas.bind("<B1-Motion>", drag_knob)
    slider_window.mainloop()

if __name__ == "__main__":
    show_slider()

