import tkinter as tk
from tkinter import simpledialog, messagebox, simpledialog, messagebox
import pandas as pd
from textwrap import shorten
from tkinter import font

# Global variables to track the state
open_windows = []
original_text = ''
original_command = ''
num_windows = 0
jobs_df_update = pd.DataFrame()
added_jobs_df_update = pd.DataFrame()
last_displayed_sacos = []

class ImportantJobsWindow:
    def __init__(self, parent, jobs_df, num_jobs, on_close_callback=None):
        try:
            self.window = tk.Toplevel(parent)
            self.window.title("Important Jobs")
            self.window.update_idletasks()
            self.window.state('zoomed')

            self.canvas = tk.Canvas(self.window)
            self.canvas.pack(side='left', fill='both', expand=True)

            self.scrollbar = tk.Scrollbar(self.window, orient='vertical', command=self.canvas.yview)
            self.scrollbar.pack(side='right', fill='y')

            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.scrollable_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

            self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

            self.on_close_callback = on_close_callback
            self.num_jobs = num_jobs
            self.jobs_df = jobs_df
            self.job_frames = []

            self.max_width = 0
            self.max_height = 0

            self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
            self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)
            self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)

            self.update_display()

            self.window.after(100, self.scroll_to_center)
            self.window.after(200, self.focus_and_raise)

            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        except Exception as e:
            messagebox.showerror("Error", f"Error initializing Important Jobs window: {e}")

    def focus_and_raise(self):
        try:
            self.window.focus_set()  # Request focus
            self.window.lift()  # Bring to the front
            self.window.attributes('-topmost', True)  # Set as topmost window
            self.window.attributes('-topmost', False)  # Reset topmost attribute
            
            # Forcing the window to stay on top for a brief moment
            self.window.update_idletasks()
            self.window.after(100, lambda: self.window.attributes('-topmost', True))
            self.window.after(200, lambda: self.window.attributes('-topmost', False))

            # Ensure the window is not minimized
            self.window.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"Error focusing and raising window: {e}")

    def on_frame_configure(self, event=None):
        try:
            # Update the scroll region to match the frame's size
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            # Get the size of the canvas and the scrollable frame
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            frame_width = self.scrollable_frame.winfo_reqwidth()
            frame_height = self.scrollable_frame.winfo_reqheight()

            # Enable or disable scrolling based on content size
            if frame_height <= canvas_height:
                self.scrollbar.pack_forget()  # Remove the scrollbar
                self.canvas.unbind_all("<MouseWheel>")  # Disable mouse wheel scrolling
            else:
                self.scrollbar.pack(side='right', fill='y')  # Add the scrollbar
                self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Enable mouse wheel scrolling

            # Center the content
            self.center_content()
        except Exception as e:
            messagebox.showerror("Error", f"Error configuring frame: {e}")

    def center_content(self):
        try:
            # Get the canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Get the scrollable frame dimensions
            frame_width = self.scrollable_frame.winfo_reqwidth()
            frame_height = self.scrollable_frame.winfo_reqheight()

            # Calculate the offsets to center the frame within the canvas
            x_offset = (canvas_width - frame_width) // 2
            y_offset = (canvas_height - frame_height) // 2

            # Ensure the offsets are within valid bounds (non-negative)
            x_offset = max(x_offset, 0)
            y_offset = max(y_offset, 0)

            # Set the position of the scrollable frame
            self.canvas.coords(self.canvas.find_all()[0], x_offset, y_offset)
        except Exception as e:
            messagebox.showerror("Error", f"Error centering content: {e}")

    def scroll_to_center(self):
        try:
            self.scrollable_frame.update_idletasks()

            canvas_height = self.canvas.winfo_height()

            total_job_height = len(self.job_frames) * (self.max_height + 20)

            available_space = canvas_height - total_job_height

            perfect_padding = max(0, available_space // 2)

            reduction_factor = 0.3  # Reduced to make space smaller
            adjusted_height = int(perfect_padding * reduction_factor)

            # Create or update the dummy frame
            if hasattr(self, 'dummy_frame'):
                self.dummy_frame.config(height=adjusted_height)
            else:
                self.dummy_frame = tk.Frame(self.scrollable_frame, height=adjusted_height)
                self.dummy_frame.pack(fill='x', padx=0, pady=0)  # Adjust padding here

            # Create the format label in the dummy frame
            format_label = tk.Label(self.dummy_frame, text="FORMAT :", font=("Arial", 14, 'bold'), anchor='center')
            format_label.pack(pady=0)  # Adjust vertical padding here

            format_details_label = tk.Label(self.dummy_frame, text="SACO | CLIENTE | DESCRIÇÃO | QUANTIDADE | SECTOR", font=("Arial", 16), anchor='center', fg='#2f73b4')
            format_details_label.pack(pady=0)  # Adjust vertical padding here

            entrega_label = tk.Label(self.dummy_frame, text="ENTREGA", font=("Arial", 16), anchor='center', fg='#2f73b4')
            entrega_label.pack(pady=0)  # Adjust vertical padding here

            self.update_display()

            if self.job_frames:
                first_job_frame_y = self.canvas.bbox("all")[1]
                first_job_frame_height = self.job_frames[0].winfo_height()
                center_y = (canvas_height - first_job_frame_height) // 2
                self.canvas.yview_moveto((first_job_frame_y - center_y) / (self.canvas.bbox("all")[3] - canvas_height))
        except Exception as e:
            messagebox.showerror("Error", f"Error scrolling to center: {e}")

    def update_display(self):
        try:
            # Clear old job frames
            for frame in self.job_frames:
                frame.destroy()
            self.job_frames = []

            # Get the top num_jobs rows
            important_jobs = self.jobs_df.head(self.num_jobs)

            # Initialize fixed frame width
            self.fixed_width = 1400  # Set a fixed width for the frame
            self.max_frame_width = 1300  # Maximum width to prevent frames from expanding off-screen

            if important_jobs.empty:
                tk.Label(self.scrollable_frame, text="No important jobs to display.", font=("Arial", 18)).pack(padx=20, pady=20)
            else:
                # To store text widths for averaging
                text_widths = []
                padx_values = []

                # First pass: Measure text widths
                for _, job in important_jobs.iterrows():
                    descr_text = shorten(job['DESCRIÇÃO DO TRABALHO'], width=60, placeholder="...")
                    client_text = shorten(job['CLIENTE'], width=35, placeholder="...")

                    details_text = f"{job['SACO']}  |  {client_text}  |  {descr_text}  |  {job['QUANT.']}  |  {job['SECTOR EM QUE ESTÁ']}"

                    # Set the font size
                    font_size = 16
                    font_name = "Arial"

                    # Calculate the width of the details_text
                    text_width = self.get_text_width(details_text, font_name, font_size)
                    text_widths.append(text_width)

                    # Calculate individual padx value
                    padx_value_details = max((self.fixed_width - text_width) // 2, 0)
                    padx_values.append(padx_value_details)

                # Calculate average padx and wraplength
                avg_padx_value = sum(padx_values) // len(padx_values) - (min(padx_values) // 2)
                avg_wraplength = self.fixed_width - 2 * avg_padx_value - 50

                # Second pass: Create and pack job frames using average padx and wraplength
                for idx, (_, job) in enumerate(important_jobs.iterrows()):
                    try:
                        text_color = 'red' if idx == 0 else 'black'
                        bd_value = 4 if idx == 0 else 2

                        # Create job frame with fixed width and prevent resizing
                        job_frame = tk.Frame(self.scrollable_frame, bd=bd_value, width=self.fixed_width, bg="lightgray")
                        
                        # Pack with center alignment
                        job_frame.pack(padx=5, pady=10, fill='x', expand=False, anchor='center')

                        self.job_frames.append(job_frame)

                        # Re-create the text strings
                        descr_text = shorten(job['DESCRIÇÃO DO TRABALHO'], width=60, placeholder="...")
                        client_text = shorten(job['CLIENTE'], width=35, placeholder="...")

                        details_text = f"{job['SACO']}  |  {client_text}  |  {descr_text}  |  {job['QUANT.']}  |  {job['SECTOR EM QUE ESTÁ']}"

                        # Use a Frame widget inside the job_frame for job details
                        details_frame = tk.Frame(job_frame, bg="lightgray", width=self.fixed_width, padx=10, pady=5)
                        details_frame.pack(fill='x', expand=False, padx=avg_padx_value, anchor='center')

                        # Apply the average wraplength
                        tk.Label(details_frame, text=details_text, font=("Arial", 20 if idx == 0 else 16), fg=text_color, bg="lightgray", wraplength=avg_wraplength, anchor='w').pack(pady=1)

                        if pd.isna(job['DATA ENTREGA']):
                            entrega_text = "SEM DATA ENTREGA"
                        else:
                            entrega_text = f"{job['DATA ENTREGA']}"

                        tk.Label(details_frame, text=entrega_text, font=("Arial", 20 if idx == 0 else 16), fg=text_color, bg="lightgray", wraplength=avg_wraplength, anchor='w').pack(pady=1)

                    except Exception as e:
                        messagebox.showerror("Error", f"Error displaying job {idx}: {e}")

            # Update canvas and scrollable_frame to reflect changes
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            # Scroll to the top after updating the display
            self.canvas.yview_moveto(0)

        except Exception as e:
            messagebox.showerror("Error", f"Error updating display: {e}")


    def get_text_width(self, text, font_name, font_size):
        """
        Measure the width of the text in pixels for a given font and size.
        """
        tk_font = font.Font(family=font_name, size=font_size)
        return tk_font.measure(text)

    def scroll_to_entry(self, index):
        try:
            if 0 <= index < len(self.entry_positions):
                # Calculate the position to scroll to
                y_position = self.entry_positions[index]
                self.canvas.yview_moveto(y_position / self.canvas.bbox("all")[3])  # Normalize the position
        except Exception as e:
            messagebox.showerror("Error", f"Error scrolling to entry {index}: {e}")

    def _on_mouse_wheel(self, event):
        try:
            # Normalize scroll direction based on platform
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
        except Exception as e:
            messagebox.showerror("Error", f"Error handling mouse wheel: {e}")

    def on_close(self):
        try:
            if self.on_close_callback:
                self.on_close_callback()
            # Remove the reference from the open_windows list
            global open_windows
            open_windows = [win for win in open_windows if win.window != self.window]
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error closing window: {e}")

def update_button_state(important_jobs_button, close_all_button):
    global original_text, original_command, num_windows
    try:
        if num_windows == 0:
            important_jobs_button.config(text=original_text, command=original_command)
            close_all_button.pack_forget()  # Hide the Close All button
    except Exception as e:
        messagebox.showerror("Error", f"Error updating button state: {e}")

class CustomModalDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="How many Important Jobs screens would you like to open?").grid(row=0)
        self.entry = tk.Entry(master)
        self.entry.grid(row=1)
        return self.entry  # initial focus on entry widget

    def validate(self):
        try:
            value = int(self.entry.get())
            if 1 <= value <= 10:
                self.result = value
                return True
            else:
                messagebox.showwarning("Invalid Input", "Please enter a number between 1 and 10.")
                return False
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid integer.")
            return False

def show_important_jobs(root, jobs_df, added_jobs_df, important_jobs_button, close_all_button):
    global original_text, original_command, num_windows

    try:
        # Create a custom modal dialog
        dialog = CustomModalDialog(root, title="Number of Screens")

        if dialog.result is not None:  # Check if user input was successful
            num_screens = dialog.result

            # Store the original button state if not already stored
            if not original_text:
                original_text = important_jobs_button.cget("text")
                original_command = important_jobs_button.cget("command")

            # Change button text and command
            important_jobs_button.config(text="Add Important Job Window", command=lambda: add_important_jobs_window(root, jobs_df, added_jobs_df, important_jobs_button, close_all_button))

            # Update the number of windows and open new ones
            num_windows = num_screens
            for _ in range(num_windows):
                window = ImportantJobsWindow(root, get_important_jobs_data(jobs_df, added_jobs_df), num_jobs=8, on_close_callback=lambda: window_closed(important_jobs_button, close_all_button))
                open_windows.append(window)

            # Show the Close All button
            close_all_button.pack(side=tk.LEFT, padx=5)

            def close_all_windows():
                global num_windows
                try:
                    if messagebox.askokcancel("Confirm Close", "Are you sure you want to close all Important Jobs windows? \n\n You can re-open them later."):
                        while open_windows:  # Ensure all windows are closed
                            window = open_windows.pop()
                            window.window.destroy()
                        num_windows = 0
                        update_button_state(important_jobs_button, close_all_button)  # Call to update button state
                except Exception as e:
                    messagebox.showerror("Error", f"Error closing all windows: {e}")

            close_all_button.config(command=close_all_windows)

    except Exception as e:
        messagebox.showerror("Error", f"Error showing important jobs: {e}")

def add_important_jobs_window(root, jobs_df, added_jobs_df, important_jobs_button, close_all_button):
    global num_windows
    try:
        num_windows += 1
        open_windows.append(ImportantJobsWindow(root, get_important_jobs_data(jobs_df, added_jobs_df), num_jobs=8, on_close_callback=lambda: window_closed(important_jobs_button, close_all_button)))
    except Exception as e:
        messagebox.showerror("Error", f"Error adding important jobs window: {e}")

def window_closed(important_jobs_button, close_all_button):
    global num_windows
    try:
        num_windows -= 1
        update_button_state(important_jobs_button, close_all_button)  # Call to update button state
    except Exception as e:
        messagebox.showerror("Error", f"Error handling window closed: {e}")

def get_important_jobs_data(jobs_df, added_jobs_df, num_jobs=8, buffer_size=20):
    global jobs_df_update, added_jobs_df_update

    try:
        jobs_df_update = jobs_df
        added_jobs_df_update = added_jobs_df

        if not jobs_df_update.empty or not added_jobs_df_update.dropna(how='all').empty:
            frames_to_concat = []
            if not jobs_df_update.empty:
                frames_to_concat.append(jobs_df_update)
            if not added_jobs_df_update.dropna(how='all').empty:
                frames_to_concat.append(added_jobs_df_update.dropna(how='all'))

            combined_df = pd.concat(frames_to_concat, ignore_index=True)

            try:
                combined_df['DATA ENTREGA'] = pd.to_datetime(combined_df['DATA ENTREGA'], format='%d/%m/%Y_%H:%M', errors='coerce')
            except Exception as e:
                messagebox.showerror("Error", f"Date conversion error: {e}")
                return pd.DataFrame()

            # Split the DataFrame into jobs with and without a valid date
            jobs_with_date = combined_df.dropna(subset=['DATA ENTREGA']).sort_values(by='DATA ENTREGA', ascending=True)
            jobs_without_date = combined_df[combined_df['DATA ENTREGA'].isna()]

            # Combine the jobs with date and fill up with jobs without date to reach buffer_size
            combined_jobs = pd.concat([jobs_with_date, jobs_without_date]).head(buffer_size)

            # Ensure to return only the required number of jobs to display
            return combined_jobs.head(num_jobs)
        else:
            messagebox.showinfo("Info", "No jobs to display.")
            return pd.DataFrame()
    except Exception as e:
        messagebox.showerror("Error", f"Error getting important jobs data: {e}")
        return pd.DataFrame()

def get_displayed_saco_values(df, num_jobs):
    try:
        # Get the 'SACO' values of the top num_jobs entries
        return list(df.head(num_jobs)['SACO'])
    except Exception as e:
        messagebox.showerror("Error", f"Error getting displayed SACO values: {e}")
        return []

def refresh_all_windows():
    global last_displayed_sacos
    
    try:
        # Get the updated data
        updated_data = get_important_jobs_data(jobs_df_update, added_jobs_df_update, num_jobs=8)

        # Always get the currently displayed 'SACO' values
        new_displayed_sacos = get_displayed_saco_values(updated_data, 6)

        # Update each open window with the latest data and refresh its display
        for window in open_windows:
            try:
                window.jobs_df = updated_data  # Update the data for the window
                window.update_display()  # Refresh the window display
            except Exception as e:
                messagebox.showerror("Error", f"Error refreshing window: {e}")

        # Update the last stored SACO values after the refresh
        last_displayed_sacos = new_displayed_sacos
    except Exception as e:
        messagebox.showerror("Error", f"Error refreshing all windows: {e}")