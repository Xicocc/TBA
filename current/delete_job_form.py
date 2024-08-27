import tkinter as tk
from tkinter import messagebox

class DeleteJobForm:
    def __init__(self, parent, job, delete_callback):
        self.parent = parent
        self.job = job
        self.delete_callback = delete_callback

        self.top = tk.Toplevel(parent)
        self.top.title("Delete Job")
        self.top.withdraw()  # Hide window until it's fully set up

        # Set the DeleteJobForm window to be on top of the parent window
        self.top.transient(parent)
        self.top.grab_set()

        frame = tk.Frame(self.top, padx=20, pady=20)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        tk.Label(frame, text="Delete Job", font=('SFPro', 25, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Display job details
        details_frame = tk.Frame(frame)
        details_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        for idx, (field, value) in enumerate(self.job.items()):
            tk.Label(details_frame, text=field, width=25, anchor='w', font=('SFPro', 21)).grid(row=idx, column=0, sticky='w', pady=5)
            tk.Label(details_frame, text=value, width=50, anchor='w', fg='white',bg='#1e1e1e', borderwidth=1, font=('SFPro', 20)).grid(row=idx, column=1, sticky='ew', padx=5)

        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        delete_button = tk.Button(button_frame, text="Delete", font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.confirm_deletion_popup, fg="red", width=10, height=1)
        delete_button.grid(row=0, column=0, padx=3)
        cancel_button = tk.Button(button_frame, text="Cancel", font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.cancel_deletion, width=10, height=1)
        cancel_button.grid(row=0, column=1, padx=3)

        self.top.geometry('400x300')  # Adjust size as needed
        self.top.update_idletasks()
        self.center_window(self.top)
        self.top.deiconify()  # Show the window

        # Make sure the form stays on top and disable interaction with the parent
        self.top.focus_set()
        self.top.grab_set()
        self.parent.wait_window(self.top)  # Wait until this window is closed

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def confirm_deletion_popup(self):
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this job? This is a permanent action.")
        if response:
            if self.delete_callback:
                self.delete_callback(self.job)
            self.top.grab_release()  # Release the grab before destroying the window
            self.top.destroy()
        else:
            self.top.grab_release()  # Release the grab before destroying the window
            self.top.destroy()

    def cancel_deletion(self):
        self.top.grab_release()  # Release the grab before destroying the window
        self.top.destroy()