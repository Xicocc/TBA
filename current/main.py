import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from add_job_form import AddJobForm
from edit_job_form import EditJobForm
from delete_job_form import DeleteJobForm
from important_jobs_view import show_important_jobs, add_important_jobs_window, refresh_all_windows, get_important_jobs_data
import json_operations

#Avoid any future incompatibilities by making sure it converts to future versions of panda
pd.set_option('future.no_silent_downcasting', True)

class JobDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Display")
        self.root.state('zoomed')
        self.is_loaded_data = False
        messagebox.showwarning('Warning', 'Não se esqueça de periodicamente apagar os ficheiros JSON criados no processo de salvamento :)')
        self.root.focus_force()

        # Initialize data structures
        self.jobs_df = pd.DataFrame()
        self.added_jobs_df = pd.DataFrame(columns=['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ', 'ESTADO', 'URGENCIA', 'DATA ENTREGA'])
        self.file_path = ""
        self.selected_job_index = None
        self.editing_added_job = False

        # Create a frame to hold the initial buttons
        self.initial_button_frame = tk.Frame(root)
        self.initial_button_frame.pack(pady=10)

        # Create select file button
        self.select_file_button = tk.Button(self.initial_button_frame, text="Select Excel File", font=('SFPro', 20), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.load_file)
        self.select_file_button.pack(side=tk.LEFT, padx=5)

        # Create Load State button
        self.load_state_button = tk.Button(self.initial_button_frame, text="Load State", font=('SFPro', 20), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.load_state)
        self.load_state_button.pack(side=tk.LEFT, padx=5)

        # Create button frame and buttons
        self.button_frame = tk.Frame(root)
        self.refresh_button = tk.Button(self.button_frame, text="Refresh Jobs", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE,command=self.refresh_view, state=tk.DISABLED)
        self.add_job_button = tk.Button(self.button_frame, text="Add New Job", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_add_job_form, state=tk.DISABLED)
        self.edit_job_button = tk.Button(self.button_frame, text="Edit Job", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_edit_job_form, state=tk.DISABLED)
        self.delete_job_button = tk.Button(self.button_frame, text="Delete Job", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_delete_job_form, state=tk.DISABLED)
        self.important_jobs_button = tk.Button(self.button_frame, text="Show Important Jobs", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.show_important_jobs, state=tk.DISABLED)
        self.close_all_button = tk.Button(self.button_frame, text="Close All Important Jobs Windows", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE)


        self.refresh_button.pack(side=tk.LEFT, padx=5)
        self.add_job_button.pack(side=tk.LEFT, padx=5)
        self.edit_job_button.pack(side=tk.LEFT, padx=5)
        self.delete_job_button.pack(side=tk.LEFT, padx=5)
        self.important_jobs_button.pack(side=tk.LEFT, padx=5)
        self.close_all_button.pack(side=tk.LEFT, padx=5)

        # Pack button_frame but keep it hidden initially
        self.button_frame.pack_forget()
        self.close_all_button.pack_forget()  # Hide the close all important jobs button initially

        # Configure the Treeview style
        self.tree_font = ('SFPro', 14)  # Set your desired font and size here
        style = ttk.Style()
        style.configure("Treeview", font=self.tree_font, rowheight=int(self.tree_font[1] * 1.5))  # Adjust row height
        style.configure("Treeview.Heading", font=('SFPro', 16, 'bold'))

        # Create an empty Treeview
        self.tree = ttk.Treeview(root, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Create and initially hide search bar
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.refresh_view)  # Update view on search query change

        search_frame = tk.Frame(root)
        self.search_label = tk.Label(search_frame, text="Search:")
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_frame.pack(pady=10)
        self.search_label.pack(side=tk.LEFT)
        self.search_entry.pack(side=tk.LEFT)
        search_frame.pack_forget()

        # Bind the select event
        self.tree.bind('<<TreeviewSelect>>', self.on_treeview_select)

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_state(self):
        data = json_operations.load_json_file()
        if data:
            if isinstance(data, dict):
                # Load jobs_df
                if 'jobs_df' in data:
                    self.jobs_df = pd.DataFrame(data['jobs_df'])
                else:
                    messagebox.showerror('Error', 'Missing jobs_df data')
                    self.root.focus_force()  # Re-focus on the main window
                    return

                # Load added_jobs_df
                if 'added_jobs_df' in data:
                    self.added_jobs_df = pd.DataFrame(data['added_jobs_df'])
                    if self.added_jobs_df.empty:
                        # Reinitialize with the correct columns if loaded DataFrame is empty
                        self.added_jobs_df = pd.DataFrame(columns=['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ', 'ESTADO', 'URGENCIA', 'DATA ENTREGA'])
                else:
                    messagebox.showerror('Error', 'Missing added_jobs_df data')
                    self.root.focus_force()  # Re-focus on the main window
                    return

                # Standardize column names
                self.jobs_df.columns = self.jobs_df.columns.str.replace('URGÊNCIA / OBSERVAÇÕES', 'URGÊNCIA / OBS.', regex=False)
                self.added_jobs_df.columns = self.added_jobs_df.columns.str.replace('URGÊNCIA / OBSERVAÇÕES', 'URGÊNCIA / OBS.', regex=False)

                # Set up Treeview columns
                self.tree['columns'] = list(self.jobs_df.columns)
                for col in self.tree['columns']:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, anchor="w")

                self.refresh_view()
                messagebox.showinfo('Success', 'Data restored successfully')
                self.root.focus_force()  # Re-focus on the main window
                self.is_loaded_data = True
                self.enable_buttons()
                self.initial_button_frame.pack_forget()
            else:
                messagebox.showerror('Error', 'Expected a dictionary with data keys')
                self.root.focus_force()  # Re-focus on the main window
        else:
            messagebox.showerror('Error', 'Failed to load data')
            self.root.focus_force()  # Re-focus on the main window

    def on_close(self):
        # Handle the window closing event
        try:
            if self.is_loaded_data:
                # Prompt the user if they want to save the state
                result = messagebox.askyesno("Save State", "Do you want to save the current state?")
                self.root.focus_force()  # Re-focus on the main window

                if result:
                    state = {
                    'added_jobs_df': self.added_jobs_df.to_dict(orient='records'),
                    'jobs_df': self.jobs_df.to_dict(orient='records')}
                    # User wants to save the state
                    for job in state['added_jobs_df']:
                        if job['DATA ENTREGA'] == 'DD/MM/YYYY_HH:MM':
                            job['DATA ENTREGA'] = '-'
                    if json_operations.save_json_file(state):
                        # Successfully saved state, now close the application
                        messagebox.showinfo("Info", "State saved successfully")
                        self.root.focus_force()  # Re-focus on the main window
                        self.root.destroy()
                        self.root.quit()
                    else:
                        # Failed to save the state, show error message
                        messagebox.showerror("Error", "Failed to save state. The application will not close.")
                        self.root.focus_force()  # Re-focus on the main window
                else:
                    # User chose not to save, just close the application
                    self.root.destroy()
                    self.root.quit()
            else:
                self.root.destroy()
                self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.root.focus_force()  # Re-focus on the main window
            self.root.destroy()
            self.root.quit()

    def on_treeview_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            tree_item = selected_item[0]
            df_index = self.tree_index_map[tree_item]
            if df_index < len(self.jobs_df):
                self.selected_job_index = df_index
                self.editing_added_job = False
            else:
                self.selected_job_index = df_index - len(self.jobs_df)
                self.editing_added_job = True
            self.edit_job_button.configure(state=tk.NORMAL)
            self.delete_job_button.configure(state=tk.NORMAL)
        else:
            self.selected_job_index = None
            self.editing_added_job = False
            self.edit_job_button.configure(state=tk.DISABLED)
            self.delete_job_button.configure(state=tk.DISABLED)

    def open_add_job_form(self):
        AddJobForm(self.root, self.add_job)

    def validate_job(self, job):
        # Check for required fields
        required_fields = ['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ']
        for field in required_fields:
            if not job.get(field):
                return False, f"The field '{field}' is required."

        # The date field is optional and not validated
        return True, ""

    def add_job(self, job):
        valid, message = self.validate_job(job)
        if not valid:
            messagebox.showerror("Validation Error", message)
            return  # Prevent the form from closing by returning early
        
        # Append new job to the added_jobs_df DataFrame
        new_job_df = pd.DataFrame([job], columns=self.added_jobs_df.columns)
        
        # Drop all-NA columns from new_job_df to prevent issues during concatenation
        new_job_df = new_job_df.dropna(axis=1, how='all')
        
        # Ensure new_job_df has the same columns as self.added_jobs_df
        new_job_df = new_job_df.reindex(columns=self.added_jobs_df.columns)
        
        # Use .loc to add rows
        self.added_jobs_df.loc[len(self.added_jobs_df)] = new_job_df.iloc[0]
        self.refresh_view()

    def enable_buttons(self):
        # Show buttons after file is loaded
            self.select_file_button.pack_forget()
            self.load_state_button.pack_forget()
            self.search_label.master.pack(pady=10)
            self.button_frame.pack(pady=10)
            self.add_job_button.configure(state=tk.NORMAL)
            self.refresh_button.configure(state=tk.NORMAL)
            self.important_jobs_button.configure(state=tk.NORMAL)
            self.edit_job_button.configure(state=tk.DISABLED)
            self.delete_job_button.configure(state=tk.DISABLED)

    def load_file(self):
        """Handles file selection and initializes Treeview columns."""
        try:
            self.file_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
            )

            if self.file_path:
                self.is_loaded_data = True
                self.enable_buttons()
                self.initial_button_frame.pack_forget()

                # Initialize Treeview columns only after the file is loaded
                self.tree['columns'] = ('job_id', 'client', 'description', 'quantity', 'sector', 'state', 'urgency', 'delivery')
                self.tree.heading('job_id', text='SACO')
                self.tree.heading('client', text='CLIENTE')
                self.tree.heading('description', text='DESCRI. DO TRABALHO')
                self.tree.heading('quantity', text='QUANT.')
                self.tree.heading('sector', text='SETOR')
                self.tree.heading('state', text='ESTADO')
                self.tree.heading('urgency', text='URGÊNCIA / OBS.')
                self.tree.heading('delivery', text='DATA ENTREGA')

                # Load the jobs from the file
                self.load_jobs()
                self.root.focus_force()

            else:
                raise FileNotFoundError("No file selected. Please try again.")

        except FileNotFoundError as fnf_error:
            messagebox.showerror("File Error", str(fnf_error))
            self.root.focus_force()  # Re-focus on the main window

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.root.focus_force()  # Re-focus on the main window

    def load_jobs(self):
        try:
            # Load the Excel file
            df = pd.read_excel(self.file_path, skiprows=4)
            df.drop(df.columns[0], axis=1, inplace=True)
            df = df.iloc[1:]
            df = df[['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ', 'ESTADO', 'URGÊNCIA / OBSERVAÇÕES', 'DATA ENTREGA', 'Unnamed: 7', 'Unnamed: 8']]
            df.columns = ['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ', 'ESTADO', 'URGENCIA', 'DATA ENTREGA', 'ALTER', 'REPET']

            def determine_state(row):
                if pd.notna(row['ESTADO']) and row['ESTADO'] == 'N':
                    return 'NOVO'
                elif pd.notna(row['ALTER']) and row['ALTER'] == 'A':
                    return 'ALTER.'
                elif pd.notna(row['REPET']) and row['REPET'] == 'R':
                    return 'REPET.'
                else:
                    return 'UNKNOWN'

            df['ESTADO'] = df.apply(determine_state, axis=1)
            df.drop(['ALTER', 'REPET'], axis=1, inplace=True)
            df.columns = ['SACO', 'CLIENTE', 'DESCRIÇÃO DO TRABALHO', 'QUANT.', 'SECTOR EM QUE ESTÁ', 'ESTADO', 'URGÊNCIA / OBSERVAÇÕES', 'DATA ENTREGA']

            df = df.dropna(subset=['SACO'])
            last_valid_index = df[df['SACO'] != '-'].index.max()
            if pd.notna(last_valid_index):
                df = df.loc[:last_valid_index]

            # Convert 'DATA ENTREGA' to string and handle NaN values
            df['DATA ENTREGA'] = df['DATA ENTREGA'].astype(str)
            df['DATA ENTREGA'].replace('NaT', '-', inplace=True)
            df['DATA ENTREGA'].replace('nan', '-', inplace=True)

            # Update the jobs_df with the new data
            self.jobs_df = df

            # Fill NaN values differently for numeric and non-numeric columns
            self.jobs_df = self.jobs_df.apply(lambda x: x.fillna(0) if x.dtype in ['float64', 'int64'] else x.fillna("-"))

            self.refresh_view()

        except FileNotFoundError:
            messagebox.showerror("File Error", "The selected file was not found. Please try again.")
            self.root.focus_force()
        except pd.errors.EmptyDataError:
            messagebox.showerror("Data Error", "The selected file is empty or cannot be read. Please check the file.")
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load jobs: {e}")
            self.root.focus_force()

    def filter_by_date(self, df, query):
        # The `query` should be in the form of 'day:DD', 'month:MM', or 'year:YYYY'.
        def match_date(date, query):
            if pd.isna(date):
                return False
            
            try:
                if query.startswith("day:"):
                    day = int(query.split(':')[1])
                    return date.day == day
                elif query.startswith("month:"):
                    month = int(query.split(':')[1])
                    return date.month == month
                elif query.startswith("year:"):
                    year = int(query.split(':')[1])
                    return date.year == year
            except ValueError:
                return False
            
            return False
        
        # Convert 'DATA ENTREGA' to datetime
        df['DATA ENTREGA'] = pd.to_datetime(df['DATA ENTREGA'], format='%d/%m/%Y_%H:%M', errors='coerce')

        # Apply the date filter
        return df[df['DATA ENTREGA'].apply(lambda date: match_date(date, query))]

    def refresh_view(self, *args):
        try:
            search_query = self.search_var.get().strip()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            frames_to_concat = []
            if not self.jobs_df.empty:
                frames_to_concat.append(self.jobs_df)
            if not self.added_jobs_df.dropna(how='all').empty:
                frames_to_concat.append(self.added_jobs_df.dropna(how='all'))

            if frames_to_concat:
                combined_df = pd.concat(frames_to_concat, ignore_index=True)

                # Apply date-based filtering if the query specifies a date component
                if any(search_query.startswith(prefix) for prefix in ["day:", "month:", "year:"]):
                    filtered_df = self.filter_by_date(combined_df, search_query)
                else:
                    # Convert 'DATA ENTREGA' to datetime and handle errors
                    combined_df['DATA ENTREGA'] = pd.to_datetime(combined_df['DATA ENTREGA'], format='%d/%m/%Y_%H:%M', errors='coerce')
                    
                    # General search (for other fields, if needed)
                    def match_query(row):
                        for column in combined_df.columns:
                            if str(row[column]).lower().find(search_query.lower()) != -1:
                                return True
                        return False

                    filtered_df = combined_df[combined_df.apply(match_query, axis=1)]

                # Sort by 'DATA ENTREGA'
                filtered_df = filtered_df.sort_values(by='DATA ENTREGA', ascending=True)

                # Replace NaN or empty string with "-"
                filtered_df = filtered_df.replace({pd.NA: "-", pd.NaT: "-"})

                # Store the mapping of Treeview indices to DataFrame indices
                self.tree_index_map = {}
                for idx, row in filtered_df.iterrows():
                    row_list = row.tolist()
                    tree_item = self.tree.insert('', 'end', values=row_list)
                    self.tree_index_map[tree_item] = idx

                # Adjust column widths based on content length
                self.adjust_column_widths()
                get_important_jobs_data(self.jobs_df, self.added_jobs_df)
                refresh_all_windows()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh view: {e}. Please try closing and reopening the app :)")

    def adjust_column_widths(self):
        for col in self.tree['columns']:
            col_values = [self.tree.heading(col, 'text')] + [str(self.tree.item(child)['values'][self.tree['columns'].index(col)]) for child in self.tree.get_children()]
            max_length = max(len(value) for value in col_values)
            self.tree.column(col, width=max_length * 5)

    def open_edit_job_form(self):
        if self.selected_job_index is not None:
            if self.editing_added_job:
                job = self.added_jobs_df.iloc[self.selected_job_index].to_dict()
            else:
                job = self.jobs_df.iloc[self.selected_job_index].to_dict()
            EditJobForm(self.root, job, self.update_job)

    def update_job(self, updated_job):
        valid, message = self.validate_job(updated_job)
        if not valid:
            messagebox.showerror("Validation Error", message)
            self.root.focus_force()  # Re-focus on the main window
            return

        # Update job in the appropriate DataFrame
        if self.editing_added_job:
            df = self.added_jobs_df
        else:
            df = self.jobs_df

        # Ensure correct data types for each column before assignment
        for column, value in updated_job.items():
            if df[column].dtype == 'float64':
                try:
                    updated_job[column] = float(value)
                except ValueError:
                    updated_job[column] = float('nan')  # Assign NaN if conversion fails
            elif df[column].dtype == 'int64':
                try:
                    updated_job[column] = int(value)
                except ValueError:
                    updated_job[column] = pd.NA  # Assign NA if conversion fails
            # For non-numeric columns, ensure value is a string
            elif df[column].dtype == 'object':
                updated_job[column] = str(value)

        # Ensure 'DATA ENTREGA' is string and handle NaN values
        updated_job['DATA ENTREGA'] = str(updated_job['DATA ENTREGA']).replace("nan", "-")

        if self.editing_added_job:
            self.added_jobs_df.iloc[self.selected_job_index] = updated_job
        else:
            self.jobs_df.iloc[self.selected_job_index] = updated_job

        self.refresh_view()
        self.selected_job_index = None
        self.edit_job_button.configure(state=tk.DISABLED)

    def open_delete_job_form(self):
        if self.selected_job_index is not None:
            if self.editing_added_job:
                job = self.added_jobs_df.iloc[self.selected_job_index].to_dict()
            else:
                job = self.jobs_df.iloc[self.selected_job_index].to_dict()
            DeleteJobForm(self.root, job, self.delete_job)

    def delete_job(self, job):
        # Convert job dictionary to a DataFrame row format for comparison
        job_series = pd.Series(job)
        
        if self.editing_added_job:
            # For added jobs DataFrame
            indices_to_drop = self.added_jobs_df[self.added_jobs_df.apply(lambda row: row.equals(job_series), axis=1)].index
        else:
            # For main jobs DataFrame
            indices_to_drop = self.jobs_df[self.jobs_df.apply(lambda row: row.equals(job_series), axis=1)].index
        
        if not indices_to_drop.empty:
            # Drop the job from the DataFrame
            if self.editing_added_job:
                self.added_jobs_df = self.added_jobs_df.drop(indices_to_drop)
            else:
                self.jobs_df = self.jobs_df.drop(indices_to_drop)
            
            # Reset index to keep it contiguous
            if self.editing_added_job:
                self.added_jobs_df = self.added_jobs_df.reset_index(drop=True)
            else:
                self.jobs_df = self.jobs_df.reset_index(drop=True)
            
            # Refresh the view
            self.refresh_view()
        else:
            messagebox.showerror("Error", "Job not found for deletion.")
            self.root.focus_force()  # Re-focus on the main window
        
        self.selected_job_index = None
        self.edit_job_button.configure(state=tk.DISABLED)
        self.delete_job_button.configure(state=tk.DISABLED)

    def show_important_jobs(self):
        show_important_jobs(self.root, self.jobs_df, self.added_jobs_df, self.important_jobs_button, self.close_all_button)

    def add_important_jobs_window(self):
        add_important_jobs_window(self.root, self.jobs_df, self.added_jobs_df, self.important_jobs_button, self.close_all_button)

if __name__ == "__main__":
    root = tk.Tk()
    app = JobDisplayApp(root)
    root.mainloop()