import tkinter as tk
from tkinter import messagebox

def get_monitor_geometry():
    """Retrieve the dimensions and positions of connected monitors."""
    monitors = []
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Try to get monitor dimensions
    try:
        screen_width = int(root.tk.call('winfo', 'screenwidth'))
        screen_height = int(root.tk.call('winfo', 'screenheight'))
        monitors.append((screen_width, screen_height))
    except tk.TclError:
        print("Error retrieving monitor dimensions.")
    
    root.destroy()
    return monitors

def arrange_windows(open_windows):
    """Arrange open important job windows across available monitors."""
    monitors = get_monitor_geometry()
    num_monitors = len(monitors)
    num_windows = len(open_windows)
    
    # Check if there are enough important job windows
    if num_windows < num_monitors:
        # Show warning message
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showwarning("Warning", "There are fewer important job windows than monitors available.")
        root.destroy()
        return

    # Arrange windows
    for index, window in enumerate(open_windows):
        if index >= num_monitors:
            break  # Avoid placing more windows than monitors
        
        monitor_width, monitor_height = monitors[index]

        # Position and size each window
        window.geometry(f"{monitor_width}x{monitor_height}+{monitor_width * index}+0")
        window.attributes('-zoomed', True)  # Fullscreen the window
