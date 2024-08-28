import platform
from tkinter import messagebox
from screeninfo import get_monitors

# Initialize lists to store monitor dimensions
monitor_widths = []
monitor_heights = []

def get_monitor_dimensions():
    """Gets the width and height of each monitor on the system."""
    global monitor_widths, monitor_heights
    
    if platform.system() == 'Windows':
        import win32api
        # Enumerate all monitors
        monitors = win32api.EnumDisplayMonitors()

        # Loop through each monitor and get its dimensions
        for i, monitor in enumerate(monitors):
            monitor_info = win32api.GetMonitorInfo(monitor[0])  # Correct index usage
            monitor_area = monitor_info['Monitor']
            
            # Calculate width and height
            width = monitor_area[2] - monitor_area[0]
            height = monitor_area[3] - monitor_area[1]
            
            print(f"Monitor {i + 1}: Width = {width} px, Height = {height} px")
            monitor_widths.append(width)
            monitor_heights.append(height)
            
    elif platform.system() == 'Darwin':
        monitors = get_monitors()
        
        for monitor in monitors:
            width = monitor.width
            height = monitor.height
            monitor_widths.append(width)
            monitor_heights.append(height)

    print(f"Monitor_widths : {monitor_widths}")
    print(f"Number of monitors detected: {len(monitor_widths)}")

def move_to_monitors(open_windows):

    # Call function to populate the information lists
    get_monitor_dimensions()

    """Moves each window to a specific monitor based on available monitors."""
    if len(open_windows) < len(monitor_widths):
        messagebox.showerror(
            'Not enough windows',
            'The number of Important Job Windows is smaller than the number of monitors available. Please open more windows to match the number of monitors.'
        )
        return
    
    # Function to calculate the x-coordinate based on monitor widths
    def get_x_coordinate(monitor_index):
        return sum(monitor_widths[:monitor_index])  # Sum all previous monitor widths

    # Move each window to the respective monitor
    for i, job_window in enumerate(open_windows):
        if i >= len(monitor_widths):  # Ensure we don't exceed available monitors
            return
        
        # Get current window size from the `window` attribute of `ImportantJobsWindow`
        current_width = job_window.window.winfo_width()  # Access through `self.window`
        current_height = job_window.window.winfo_height()
        
        # Calculate new position
        x = get_x_coordinate(i)
        y = 0  # Start at the top of the screen; adjust if needed
        
        # Update window geometry without changing its size
        job_window.window.geometry(f"{current_width}x{current_height}+{x}+{y}")