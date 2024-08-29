# Oficial libraries
import tkinter as tk
from datetime import datetime

# Developed libraries
from date_placeholder import PlaceholderEntry
from constants import *
from help_window import HelpAdd

class AddJobForm:
    def __init__(self, parent, add_callback):
        self.parent = parent
        self.add_callback = add_callback

        self.top = tk.Toplevel(parent)
        self.top.title("Add Job")
        self.top.withdraw()  # Hide window until it's fully set up

        # Set the AddJobForm window to be on top of the parent window
        self.top.transient(parent)
        self.top.grab_set()

        frame = tk.Frame(self.top, padx=20, pady=20)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        tk.Label(frame, text="Add Job", font=('SFPro', 25, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Form Fields
        self.fields = {}
        row = 1
        for field in [CONST_SACO, CONST_CLIENTE, CONST_DESC, CONST_QUANT, CONST_SECTOR, CONST_ESTADO, 'URGENCIA', CONST_DATA_ENTR]:
            tk.Label(frame, text=field, width=25, anchor='w', font=('SFPro', 21)).grid(row=row, column=0, sticky='w', pady=5)
            if field == CONST_DATA_ENTR:
                entry = PlaceholderEntry(frame, "DD/MM/YYYY_HH:MM", width=50, bg='#1e1e1e', fg='white', insertbackground='white', borderwidth=1, relief=tk.FLAT, font=('SFPro', 20))
            else:
                entry = tk.Entry(frame, width=50, bg='#1e1e1e', fg='white', insertbackground='white', borderwidth=1, relief=tk.FLAT, font=('SFPro', 20))
            entry.grid(row=row, column=1, sticky='ew', padx=5)
            self.fields[field] = entry
            row += 1

        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))

        save_button = tk.Button(button_frame, text="Save", fg='green', font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.save_job, width=10, height=1)
        save_button.grid(row=0, column=0, padx=3)
        cancel_button = tk.Button(button_frame, text="Cancel", font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.cancel_job, width=10, height=1)
        cancel_button.grid(row=0, column=1, padx=3)
        self.add_help_button = tk.Button(button_frame, text="Help", font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.show_add_help)
        self.add_help_button.grid(row=0, column=2, padx=3)

        self.top.geometry('600x400')  # Adjust size as needed
        self.top.update_idletasks()
        self.center_window(self.top)
        self.top.deiconify()

        # Make sure the form stays on top and disable interaction with the parent
        self.top.focus_set()
        self.top.grab_set()
        self.parent.wait_window(self.top)  # Wait until this window is closed

    def show_add_help(self):
        HelpAdd(self.top)

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def save_job(self):
        # Collect the input from the form fields
        job = {field: entry.get() for field, entry in self.fields.items()}

        # Replace placeholder date with '-' if it hasn't been modified
        if job[CONST_DATA_ENTR] == 'DD/MM/YYYY_HH:MM':
            job[CONST_DATA_ENTR] = '-'

        # Fields that are required
        required_fields = [CONST_SACO, CONST_CLIENTE, CONST_DESC, CONST_QUANT, CONST_SECTOR]

        # Check if any required fields are empty
        missing_fields = [field for field in required_fields if not job[field].strip()]
        if missing_fields:
            tk.messagebox.showerror("Missing Information", f"The following fields are required: {', '.join(missing_fields)}")
            return  # Stop the save process if required fields are missing

        # Validate the datetime format for CONST_DATA_ENTR
        if not self.validate_datetime(job[CONST_DATA_ENTR]):
            tk.messagebox.showerror("Invalid Input", "The date/time format is incorrect. Please use DD/MM/YYYY_HH:MM format.")
            return  # Stop the save process if the datetime format is incorrect


        # Replace empty fields with "-"
        for field in job:
            if not job[field].strip():
                job[field] = "-"
        # If all validations pass, proceed to add the job and close the form
        self.add_callback(job)
        self.top.grab_release()  # Release the grab before destroying the window
        self.top.destroy()

    def cancel_job(self):
        self.top.grab_release()  # Release the grab before destroying the window
        self.top.destroy()

    def validate_datetime(self, datetime_str):
        if datetime_str == '-' or datetime_str == '':
            return True
        try:
            datetime.strptime(datetime_str, DATE_FORMAT)
            return True
        except ValueError:
            return False