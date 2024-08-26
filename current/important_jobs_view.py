import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
from textwrap import shorten
from tkinter import font
from constants import *

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

    #Beggining of functions to handle the creation/updating of the important jobs windows

    def update_display(self):
        try:
            self.clear_job_frames()

            important_jobs = self.jobs_df.head(self.num_jobs)
            screen_width = self.scrollable_frame.winfo_screenwidth()
            self.fixed_width = screen_width - 40
            self.max_frame_width = screen_width - 140

            if important_jobs.empty:
                self.display_no_jobs_message()
            else:
                padx_values, avg_wraplength = self.calculate_padding_and_wraplength(important_jobs)

                # Determine the date of the first job entry
                first_entry_date = self.get_date_from_job(important_jobs.iloc[0])

                # Iterate over the jobs to apply conditional formatting
                for idx, (_, job) in enumerate(important_jobs.iterrows()):
                    job_date = self.get_date_from_job(job)

                    # Determine if the job should be highlighted and set font size
                    is_highlighted = self.should_highlight_job(job_date, first_entry_date, idx)
                    font_size = self.get_font_size(is_highlighted, idx == 0)

                    # Create and display the job frames
                    self.create_and_display_job_frame(job, idx, is_highlighted, font_size, padx_values, avg_wraplength)

            self.update_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating display: {e}")

    def get_date_from_job(self, job):
        """Extract the date part (day, month, year) from the job's CONST_DATA_ENTR field."""
        if pd.isna(job[CONST_DATA_ENTR]):
            return None
        return job[CONST_DATA_ENTR].date()

    def should_highlight_job(self, job_date, first_entry_date, idx):
        """Determine whether a job should be highlighted based on its date."""
        if job_date is None:
            return False
        # Highlight the job if it shares the same date as the first entry or if it's the first entry
        return job_date == first_entry_date or idx == 0

    def get_font_size(self, is_highlighted, is_first_entry):
        """Determine the font size based on whether the job is highlighted and if it's the first entry."""
        if is_highlighted:
            return 24 if is_first_entry else 22
        return 18

    def clear_job_frames(self):
        """Clear existing job frames from the display."""
        for frame in self.job_frames:
            frame.destroy()
        self.job_frames = []

    def display_no_jobs_message(self):
        """Display a message when there are no important jobs."""
        tk.Label(self.scrollable_frame, text="No important jobs to display.", font=("Arial", 18)).pack(padx=20, pady=20)

    def get_text_width(self, text, font_name, font_size):
        """
        Measure the width of the text in pixels for a given font and size.
        """
        tk_font = font.Font(family=font_name, size=font_size)
        return tk_font.measure(text)

    def calculate_padding_and_wraplength(self, jobs):
        """Calculate padding and wraplength based on job text lengths."""
        text_widths = []
        padx_values = []
        font_name = "Arial"
        font_size = 18

        for _, job in jobs.iterrows():
            details_text = self.create_details_text(job)
            text_width = self.get_text_width(details_text, font_name, font_size)
            text_widths.append(text_width)

            padx_value = max((self.fixed_width - text_width) // 2, 0)
            padx_values.append(padx_value)

        avg_padx_value = sum(padx_values) // len(padx_values) - (min(padx_values) // 2)
        avg_wraplength = self.fixed_width - 2 * avg_padx_value - 35

        # Ensure the wraplength does not exceed the max_frame_width
        if avg_wraplength > self.max_frame_width:
            avg_wraplength = self.max_frame_width

        return avg_padx_value, avg_wraplength

    def create_and_display_job_frame(self, job, idx, is_highlighted, font_size, padx_values, avg_wraplength):
        """Create and display a job frame with appropriate formatting."""
        try:
            job_frame = self.create_job_frame(is_highlighted)
            self.job_frames.append(job_frame)

            details_text = self.create_details_text(job)
            entrega_text = self.create_entrega_text(job)

            self.add_details_to_frame(job_frame, details_text, entrega_text, is_highlighted, font_size, padx_values, avg_wraplength)
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying job {idx}: {e}")

    def create_job_frame(self, is_highlighted):
        """Create and return a job frame widget with conditional styling."""
        text_color = 'red' if is_highlighted else 'black'
        bd_value = 4 if is_highlighted else 2

        job_frame = tk.Frame(self.scrollable_frame, bd=bd_value, width=self.fixed_width, bg="lightgray")
        job_frame.pack(padx=5, pady=10, fill='x', expand=False, anchor='center')
        return job_frame

    def create_details_text(self, job):
        """Create and return the details text for a job."""
        descr_text = shorten(job[ORI_CONST_DESC], width=60, placeholder="...")
        client_text = shorten(job[CONST_CLIENTE], width=35, placeholder="...")
        return f"{job[CONST_SACO]}  |  {client_text}  |  {descr_text}  |  {job[CONST_QUANT]}  |  {job[ORI_CONST_SECTOR]}"

    def create_entrega_text(self, job):
        """Create and return the entrega text for a job."""
        return "SEM DATA ENTREGA" if pd.isna(job[CONST_DATA_ENTR]) else f"{job[CONST_DATA_ENTR]}"

    def add_details_to_frame(self, job_frame, details_text, entrega_text, is_highlighted, font_size, avg_padx_value, avg_wraplength):
        """Add details labels to the job frame with conditional styling."""
        text_color = 'red' if is_highlighted else 'black'

        details_frame = tk.Frame(job_frame, bg="lightgray", width=self.fixed_width, padx=10, pady=5)
        details_frame.pack(fill='x', expand=False, padx=avg_padx_value, anchor='center')

        tk.Label(details_frame, text=details_text, font=("Arial", font_size), fg=text_color, bg="lightgray", wraplength=avg_wraplength, anchor='w').pack(pady=1)
        tk.Label(details_frame, text=entrega_text, font=("Arial", font_size), fg=text_color, bg="lightgray", wraplength=avg_wraplength, anchor='w').pack(pady=1)

    def update_canvas(self):
        """Update the canvas and scroll region."""
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)

    #End of the creation/updating functions

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

            # Unbind the mouse wheel events
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

            # Remove the reference from the open_windows list
            global open_windows
            open_windows = [win for win in open_windows if win.window != self.window]
            
            self.window.destroy()
            self.window = None
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
                window = ImportantJobsWindow(root, get_important_jobs_data(jobs_df, added_jobs_df), num_jobs=10, on_close_callback=lambda: window_closed(important_jobs_button, close_all_button))
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
        open_windows.append(ImportantJobsWindow(root, get_important_jobs_data(jobs_df, added_jobs_df), num_jobs=10, on_close_callback=lambda: window_closed(important_jobs_button, close_all_button)))
    except Exception as e:
        messagebox.showerror("Error", f"Error adding important jobs window: {e}")

def window_closed(important_jobs_button, close_all_button):
    global num_windows
    try:
        num_windows -= 1
        update_button_state(important_jobs_button, close_all_button)  # Call to update button state
    except Exception as e:
        messagebox.showerror("Error", f"Error handling window closed: {e}")

def get_important_jobs_data(jobs_df, added_jobs_df, num_jobs=10, buffer_size=20):
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
                combined_df[CONST_DATA_ENTR] = pd.to_datetime(combined_df[CONST_DATA_ENTR], format=DATE_FORMAT, errors='coerce')
            except Exception as e:
                messagebox.showerror("Error", f"Date conversion error: {e}")
                return pd.DataFrame()

            # Split the DataFrame into jobs with and without a valid date
            jobs_with_date = combined_df.dropna(subset=[CONST_DATA_ENTR]).sort_values(by=CONST_DATA_ENTR, ascending=True)
            jobs_without_date = combined_df[combined_df[CONST_DATA_ENTR].isna()]

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
        # Get the CONST_SACO values of the top num_jobs entries
        return list(df.head(num_jobs)[CONST_SACO])
    except Exception as e:
        messagebox.showerror("Error", f"Error getting displayed SACO values: {e}")
        return []

def refresh_all_windows():
    global last_displayed_sacos
    
    try:
        # Get the updated data
        updated_data = get_important_jobs_data(jobs_df_update, added_jobs_df_update, num_jobs=10)

        # Always get the currently displayed CONST_SACO values
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