import tkinter as tk
from screeninfo import get_monitors

class MonitorManagement:
    def __init__(self, open_windows):
        self.open_windows = open_windows
        self.monitors = self.get_monitors()
        self.move_windows_to_monitors()
    
    def get_monitors(self):
        try:
            return get_monitors()
        except Exception as e:
            print(f"Error retrieving monitors: {e}")
            return []
    
    def move_windows_to_monitors(self):
        if not self.open_windows:
            print("No windows to move.")
            return
        
        num_monitors = len(self.monitors)
        num_windows = len(self.open_windows)
        
        if num_windows < num_monitors:
            print("Not enough windows to match the number of monitors.")
            return
        
        for i, window in enumerate(self.open_windows):
            if i >= num_monitors:
                break
            
            monitor = self.monitors[i]
            self.move_window_to_monitor(window, monitor)
    
    def move_window_to_monitor(self, window, monitor):
        try:
            if window.window is None:
                print("Window is None, cannot move.")
                return
            
            monitor_x = monitor.x
            monitor_y = monitor.y
            monitor_width = monitor.width
            monitor_height = monitor.height
            
            # Set window size to monitor's size
            window.window.geometry(f"{monitor_width}x{monitor_height}+{monitor_x}+{monitor_y}")
            
            # Maximize the window
            window.window.state('zoomed')
            
            print(f"Moved and maximized window to monitor at ({monitor_x}, {monitor_y}) with size {monitor_width}x{monitor_height}")
        except Exception as e:
            print(f"Error moving window: {e}")
