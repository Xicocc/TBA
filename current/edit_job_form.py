import tkinter as tk
from datetime import datetime
from date_placeholder import PlaceholderEntry

class EditJobForm:
    def __init__(self, parent, job, update_callback):
        self.parent = parent
        self.job = job
        self.update_callback = update_callback

        self.top = tk.Toplevel(parent)
        self.top.title("Edit Job")
        self.top.withdraw()  # Hide window until it's fully set up

        # Set the EditJobForm window to be on top of the parent window
        self.top.transient(parent)
        self.top.grab_set()

        frame = tk.Frame(self.top, padx=20, pady=20)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        tk.Label(frame, text="Edit Job", font=('Arial', 20, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Form Fields
        self.fields = {}
        row = 1
        for field, value in job.items():
            tk.Label(frame, text=field, width=25, anchor='w', font=('Arial', 17)).grid(row=row, column=0, sticky='w', pady=5)
            if field == 'DATA ENTREGA' and value == '-':
                entry = PlaceholderEntry(frame, "DD/MM/YYYY_HH:MM", width=50, bg='#1e1e1e', fg='white', insertbackground='white', borderwidth=1, relief=tk.FLAT, font=('Arial', 15))
            else:
                entry = tk.Entry(frame, width=50, bg='#1e1e1e', fg='white', insertbackground='white', borderwidth=1, relief=tk.FLAT, font=('Arial', 15))
                entry.insert(0, value)
            entry.grid(row=row, column=1, sticky='ew', padx=5)
            self.fields[field] = entry
            row += 1

        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))

        save_button = tk.Button(button_frame, text="Save", fg='#2f73b4', font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.save_job, width=10, height=1)
        save_button.grid(row=0, column=0, padx=3)
        cancel_button = tk.Button(button_frame, text="Cancel", font=('SFPro', 25), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.cancel_edit, width=10, height=1)
        cancel_button.grid(row=0, column=1, padx=3)

        self.top.geometry('600x400')  # Adjust size as needed
        self.top.update_idletasks()
        self.center_window(self.top)
        self.top.deiconify()

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

    def save_job(self):
        job = {field: entry.get() for field, entry in self.fields.items()}
        if self.validate_datetime(job['DATA ENTREGA']):
            # Fields that are required
            required_fields = ['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ']

            # Check if any required fields are empty
            missing_fields = [field for field in required_fields if not job[field].strip()]
            if missing_fields:
                tk.messagebox.showerror("Missing Information", f"The following fields are required: {', '.join(missing_fields)}")
                return  # Stop the save process if required fields are missing
            else :
                # Replace empty fields with "-"
                for field in job:
                    if not job[field].strip():
                        job[field] = " - "
                self.update_callback(job)
                self.top.grab_release()  # Release the grab before destroying the window
                self.top.destroy()
        else:
            tk.messagebox.showerror("Invalid Input", "The date/time format is incorrect. Please use DD/MM/YYYY_HH:MM format.")

    def cancel_edit(self):
        self.top.grab_release()  # Release the grab before destroying the window
        self.top.destroy()

    def validate_datetime(self, datetime_str):
        if datetime_str == "DD/MM/YYYY_HH:MM" or datetime_str == '':
            return True
        try:
            datetime.strptime(datetime_str, "%d/%m/%Y_%H:%M")
            return True
        except ValueError:
            return False