import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from add_job_form import AddJobForm
from edit_job_form import EditJobForm
from delete_job_form import DeleteJobForm
from important_jobs_view import show_important_jobs, add_important_jobs_window, refresh_all_windows, get_important_jobs_data
import json_operations
from constants import *
from help_window import HelpFile, HelpData

class JobDisplayApp:
    #Avoid any future incompatibilities by making sure it converts to future versions of panda
    pd.set_option('future.no_silent_downcasting', True)

    def __init__(self, root):
        self.root = root
        self.root.title("Job Display")
        self.root.state('zoomed')
        self.is_loaded_data = False

        # Initialize data structures
        self.jobs_df = pd.DataFrame()
        self.added_jobs_df = pd.DataFrame(columns=[CONST_SACO, CONST_CLIENTE, ORI_CONST_DESC, CONST_QUANT, ORI_CONST_SECTOR, CONST_ESTADO, 'URGENCIA', CONST_DATA_ENTR])
        self.file_path = ""
        self.selected_job_index = None
        self.editing_added_job = False
        self.tree_index_map = {}

        # Create a frame to hold the initial buttons
        self.initial_button_frame = tk.Frame(root)
        self.initial_button_frame.pack(pady=10)

        # Create select file button
        self.select_file_button = tk.Button(
            self.initial_button_frame, text="Load File",
            font=('SFPro', 20), pady=5, borderwidth=2, relief=tk.RIDGE,
            command=self.load_file)
        self.select_file_button.pack(side=tk.LEFT, padx=5)

        # Create Load State button
        self.load_state_button = tk.Button(
            self.initial_button_frame, text="Load State",
            font=('SFPro', 20), pady=5, borderwidth=2, relief=tk.RIDGE,
            command=self.load_state)
        self.load_state_button.pack(side=tk.LEFT, padx=5)

        # Create file help button and pack it to the right side within the same frame
        self.file_help_button = tk.Button(
            root, text="Help", 
            font=('SFPro', 17), pady=5, borderwidth=2, relief=tk.RIDGE, 
            command=self.show_file_help
        )
        self.file_help_button.pack(side=tk.BOTTOM, anchor='center', pady=10)

        # Create warning frame and place it below the initial button frame
        self.warning_frame = tk.Frame(root)
        self.warning_frame.pack(pady=(10, 0), fill=tk.X)  # Place below initial_button_frame

        # Create and show the warning label inside the warning frame
        self.warning_label = tk.Label(
            self.warning_frame, text="Não se esqueça de periodicamente apagar os ficheiros JSON criados :) \n"
                + "Apenas apague os ficheiros que tem a certeza que não precisa.",
            font=('SFPro', 17), wraplength=600
        )
        self.warning_label.pack(pady=10, anchor='center')  # Center the text in the frame

        # Add a "tag" label at the bottom right of the screen
        self.tag_label = tk.Label(
            root, text="Developed by Francisco Carvalho, 2024 \nAll rights reserved",
            font=('SFPro', 8), fg="gray"
        )
        # Use place() to position the label at the bottom right corner
        self.tag_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-18)

        self.cont_tag_label = tk.Label(
            root, text="Contact :\nfranciscocosta2000@gmail.com",
            font=('SFPro', 8), fg="gray"
        )
        # Use place() to position the label at the bottom left corner
        self.cont_tag_label.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-20)

        # Create button frame and buttons
        self.button_frame = tk.Frame(root)
        self.add_job_button = tk.Button(self.button_frame, text="Add New Job", font=('SFPro', 15), fg='green', pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_add_job_form, state=tk.DISABLED)
        self.edit_job_button = tk.Button(self.button_frame, text="Edit Job", font=('SFPro', 15), fg='#2f73b4',pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_edit_job_form, state=tk.DISABLED)
        self.delete_job_button = tk.Button(self.button_frame, text="Delete Job", font=('SFPro', 15), fg='red',pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_delete_job_form, state=tk.DISABLED)
        self.important_jobs_button = tk.Button(self.button_frame, text="Show Important Jobs", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.show_important_jobs, state=tk.DISABLED)
        self.close_all_button = tk.Button(self.button_frame, text="Close All Important Jobs Windows", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE)
        self.data_help_button = tk.Button(self.button_frame, text="Help", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.show_data_help)
        self.reset_screen_button = tk.Button(self.button_frame, text="Back to files", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.reset_screen)

        self.add_job_button.pack(side=tk.LEFT, padx=5)
        self.edit_job_button.pack(side=tk.LEFT, padx=5)
        self.delete_job_button.pack(side=tk.LEFT, padx=5)
        self.important_jobs_button.pack(side=tk.LEFT, padx=5)
        self.close_all_button.pack(side=tk.LEFT, padx=5)
        self.data_help_button.pack(side=tk.LEFT, padx=5)
        self.reset_screen_button.pack(side=tk.LEFT, padx=5, anchor='w')

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

    def reset_screen(self):
        response = messagebox.askyesno("Confirm", "Are you sure you want to go back to the main screen? All progress will be lost.")
        if response:
            """Reset to the initial main screen by creating a new instance of JobDisplayApp."""
            # Destroy the current window
            self.root.destroy()
            
            # Create a new root window
            new_root = tk.Tk()
            
            # Initialize a new instance of JobDisplayApp
            JobDisplayApp(new_root)

    def show_file_help(self):
        HelpFile(self.root)

    def show_data_help(self):
        HelpData(self.root)

    def load_state(self):
        """Load the saved state from a file."""
        try:
            data = json_operations.load_json_file()
            if data:
                if isinstance(data, dict):
                    # Load jobs_df
                    if 'jobs_df' in data:
                        self.jobs_df = pd.DataFrame(data['jobs_df'])
                    else:
                        messagebox.showerror('Error', 'Missing jobs_df data')
                        self.root.focus_force()
                        return

                    # Load added_jobs_df
                    if 'added_jobs_df' in data:
                        self.added_jobs_df = pd.DataFrame(data['added_jobs_df'])
                        if self.added_jobs_df.empty:
                            # Reinitialize with the correct columns if loaded DataFrame is empty
                            self.added_jobs_df = pd.DataFrame(columns=[CONST_SACO, CONST_CLIENTE, ORI_CONST_DESC, CONST_QUANT, ORI_CONST_SECTOR, CONST_ESTADO, 'URGENCIA', CONST_DATA_ENTR])
                    else:
                        messagebox.showerror('Error', 'Missing added_jobs_df data')
                        self.root.focus_force()
                        return

                    # Standardize column names
                    self.jobs_df.columns = self.jobs_df.columns.str.replace(ORI_CONST_URG, CONST_URG, regex=False)
                    self.added_jobs_df.columns = self.added_jobs_df.columns.str.replace(ORI_CONST_URG, CONST_URG, regex=False)

                    # Set up Treeview columns
                    self.tree['columns'] = list(self.jobs_df.columns)
                    for col in self.tree['columns']:
                        if col == ORI_CONST_SECTOR:
                            #Change the column name in treeview from 'SECTOR EM QUE ESTÁ' to 'SECTOR' for consistency
                            self.tree.heading(col, text='SECTOR')
                            self.tree.column(col, anchor="w")
                        else:
                            self.tree.heading(col, text=col)
                            self.tree.column(col, anchor="w")

                    self.initial_button_frame.pack_forget()
                    self.warning_frame.pack_forget()
                    self.file_help_button.pack_forget()
                    messagebox.showinfo('Success', 'Data restored successfully')
                    self.refresh_view()
                    self.root.focus_force()
                    self.is_loaded_data = True
                    self.enable_buttons()
                else:
                    messagebox.showerror('Error', 'Expected a dictionary with data keys')
                    self.root.focus_force()
            else:
                messagebox.showerror('Error', 'Failed to load data')
                self.root.focus_force()
        except json.JSONDecodeError:
            messagebox.showerror('Error', 'Error decoding data. The file may be corrupted.')
            self.root.focus_force()
        except pd.errors.EmptyDataError:
            messagebox.showerror('Error', 'Data is empty or could not be processed.')
            self.root.focus_force()
        except KeyError as e:
            messagebox.showerror('Error', f'Missing expected key: {e}')
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror('Error', f'Unexpected error: {e}')
            self.root.focus_force()

    def on_close(self):
        """Handle the window closing event."""
        try:
            if self.is_loaded_data:
                result = messagebox.askyesno("Save State", "Do you want to save the current state?")
                self.root.focus_force()

                if result:
                    state = {
                        'added_jobs_df': self.added_jobs_df.to_dict(orient='records'),
                        'jobs_df': self.jobs_df.to_dict(orient='records')
                    }
                    for job in state['added_jobs_df']:
                        if job[CONST_DATA_ENTR] == 'DD/MM/YYYY_HH:MM':
                            job[CONST_DATA_ENTR] = '-'
                    if json_operations.save_json_file(state):
                        messagebox.showinfo("Info", "State saved successfully")
                    else:
                        messagebox.showerror("Error", "Failed to save state. The application will not close.")
                        self.root.focus_force()
                        return
                self.root.destroy()
                self.root.quit()
            else:
                self.root.destroy()
                self.root.quit()
        except IOError as e:
            messagebox.showerror("Error", f"File I/O error: {e}")
            self.root.focus_force()
            self.root.destroy()
            self.root.quit()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Data encoding issues prevented state saving.")
            self.root.focus_force()
            self.root.destroy()
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.root.focus_force()
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
        required_fields = [CONST_SACO, CONST_CLIENTE, ORI_CONST_DESC, CONST_QUANT, ORI_CONST_SECTOR]
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
            self.cont_tag_label.place_forget()
            self.warning_frame.pack_forget()
            self.tag_label.place_forget()
            self.file_help_button.pack_forget()
            self.search_label.master.pack(pady=10)
            self.button_frame.pack(pady=10)
            self.add_job_button.configure(state=tk.NORMAL)
            self.important_jobs_button.configure(state=tk.NORMAL)
            self.data_help_button.configure(state=tk.NORMAL)
            self.edit_job_button.configure(state=tk.DISABLED)
            self.delete_job_button.configure(state=tk.DISABLED)

    def load_file(self):
        """Handles file selection and initializes Treeview columns."""
        try:
            self.file_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
            )

            if not self.file_path:
                raise FileNotFoundError("No file selected. Please try again.")

            self.is_loaded_data = True
            self.initial_button_frame.pack_forget()

            self.tree['columns'] = ('job_id', 'client', 'description', 'quantity', 'sector', 'state', 'urgency', 'delivery')
            self.tree.heading('job_id', text=CONST_SACO)
            self.tree.heading('client', text=CONST_CLIENTE)
            self.tree.heading('description', text='DESCRIÇÃO')
            self.tree.heading('quantity', text=CONST_QUANT)
            self.tree.heading('sector', text='SECTOR')
            self.tree.heading('state', text=CONST_ESTADO)
            self.tree.heading('urgency', text=CONST_URG)
            self.tree.heading('delivery', text=CONST_DATA_ENTR)

            self.load_jobs()
            self.root.focus_force()

        except FileNotFoundError as fnf_error:
            messagebox.showerror("File Error", str(fnf_error))
            self.root.focus_force()
        except pd.errors.EmptyDataError as empty_data_error:
            messagebox.showerror("Data Error", f"File is empty or cannot be read. {empty_data_error}")
            self.root.focus_force()
        except ValueError as value_error:
            messagebox.showerror("Value Error", f"Value error: {value_error}")
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            self.root.focus_force()

    def parse_date(self, date_str, format=DATE_FORMAT):
        """Parse a date string to a datetime object and format it back to string.
        
        Args:
            date_str (str): Date string to parse.
            format (str): Format to parse and format the date string.
            
        Returns:
            str: Formatted date string or '-' if date is invalid or empty.
        """
        try:
            date_obj = pd.to_datetime(date_str, format=format, errors='coerce')
            return date_obj.strftime(format) if pd.notna(date_obj) else '-'
        except ValueError:
            return '-'

    def load_jobs(self):
        try:
            # Load the Excel file
            df = pd.read_excel(self.file_path, skiprows=4)
            df.drop(df.columns[0], axis=1, inplace=True)
            df = df.iloc[1:]
            df = df[[CONST_SACO, CONST_CLIENTE, ORI_CONST_DESC, CONST_QUANT, ORI_CONST_SECTOR, CONST_ESTADO, ORI_CONST_URG, CONST_DATA_ENTR, 'Unnamed: 7', 'Unnamed: 8']]
            df.columns = [CONST_SACO, CONST_CLIENTE, ORI_CONST_DESC, CONST_QUANT, ORI_CONST_SECTOR, CONST_ESTADO, 'URGENCIA', CONST_DATA_ENTR, 'ALTER', 'REPET']

            def determine_state(row):
                if pd.notna(row[CONST_ESTADO]) and row[CONST_ESTADO] == 'N':
                    return 'NOVO'
                elif pd.notna(row['ALTER']) and row['ALTER'] == 'A':
                    return 'ALTER.'
                elif pd.notna(row['REPET']) and row['REPET'] == 'R':
                    return 'REPET.'
                else:
                    return 'UNKNOWN'

            df[CONST_ESTADO] = df.apply(determine_state, axis=1)
            df.drop(['ALTER', 'REPET'], axis=1, inplace=True)
            df.columns = [CONST_SACO, CONST_CLIENTE, ORI_CONST_DESC, CONST_QUANT, ORI_CONST_SECTOR, CONST_ESTADO, ORI_CONST_URG, CONST_DATA_ENTR]

            df = df.dropna(subset=[CONST_SACO])
            last_valid_index = df[df[CONST_SACO] != '-'].index.max()
            if pd.notna(last_valid_index):
                df = df.loc[:last_valid_index]

            # Use the parse_date utility function to format CONST_DATA_ENTR
            df[CONST_DATA_ENTR] = df[CONST_DATA_ENTR].apply(self.parse_date)

            # Update the jobs_df with the new data
            self.jobs_df = df

            # Fill NaN values differently for numeric and non-numeric columns
            self.jobs_df = self.jobs_df.apply(lambda x: x.fillna(0) if x.dtype in ['float64', 'int64'] else x.fillna("-"))

            self.warning_frame.pack_forget()
            self.file_help_button.pack_forget()
            messagebox.showinfo('Success', 'Data imported from excel file successfully')
            self.enable_buttons()
            self.refresh_view()

        except FileNotFoundError:
            messagebox.showerror("File Error", "The selected file was not found. Please try again.")
            self.root.focus_force()
        except pd.errors.EmptyDataError:
            messagebox.showerror("Data Error", "The selected file is empty or cannot be read. Please check the file.")
            self.root.focus_force()
        except pd.errors.ParserError:
            messagebox.showerror("Parse Error", "There was an error parsing the file. Please check the file format.")
            self.root.focus_force()
        except ValueError as value_error:
            messagebox.showerror("Value Error", f"Value error occurred: {value_error}")
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load jobs: {e}")
            self.root.focus_force()

    def filter_by_date(self, df, query):
        """Filter DataFrame based on date components specified in the query."""
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

        # Convert CONST_DATA_ENTR to datetime
        df[CONST_DATA_ENTR] = pd.to_datetime(df[CONST_DATA_ENTR], format=DATE_FORMAT, errors='coerce')

        # Apply the date filter
        filtered_df = df[df[CONST_DATA_ENTR].apply(lambda date: match_date(date, query))]

        return filtered_df

    def filter_data(self, df, query):
        """Filter the DataFrame based on the search query."""
        
        # Initialize the filtered DataFrame
        filtered_df = df.copy()

        # Apply specific filters based on the query prefix
        if query.startswith("day:") or query.startswith("month:") or query.startswith("year:"):
            # Use the existing filter_by_date for date-based queries
            filtered_df = self.filter_by_date(filtered_df, query)
        else:
            # Dictionary mapping query prefixes to column names
            column_mapping = {
                "saco:": CONST_SACO,
                "cliente:": CONST_CLIENTE,
                "desc:": ORI_CONST_DESC,
                "quant:": CONST_QUANT,
                "sector:": ORI_CONST_SECTOR,
                "estado:": CONST_ESTADO,
                "urg:": CONST_URG,
                "obs:": CONST_URG  # Handling 'obs:' as equivalent to 'urg:'
            }

            # Identify the column to filter based on the query prefix
            column_to_filter = None
            search_value = None
            for prefix, column in column_mapping.items():
                if query.startswith(prefix):
                    column_to_filter = column
                    search_value = query[len(prefix):].strip()
                    break

            if column_to_filter and search_value:
                # Apply filter for the specific column
                filtered_df = filtered_df[filtered_df[column_to_filter].astype(str).str.contains(search_value, case=False, na=False)]
            else:
                # Apply general search filter
                search_value = query.strip().lower()
                filtered_df = filtered_df[filtered_df.apply(
                    lambda row: any(search_value in str(row[col]).lower() for col in filtered_df.columns),
                    axis=1
                )]

        return filtered_df

    def refresh_view(self, *args):
        """Refresh the view based on the current data and search query."""
        try:
            search_query = self.search_var.get().strip()

            # Generate new data
            frames_to_concat = []
            if not self.jobs_df.empty:
                frames_to_concat.append(self.jobs_df)
            if not self.added_jobs_df.dropna(how='all').empty:
                frames_to_concat.append(self.added_jobs_df.dropna(how='all'))

            if frames_to_concat:
                combined_df = pd.concat(frames_to_concat, ignore_index=True)

                # Apply filtering
                filtered_df = self.filter_data(combined_df, search_query)

                # Convert CONST_DATA_ENTR to datetime format for sorting
                filtered_df[CONST_DATA_ENTR] = pd.to_datetime(filtered_df[CONST_DATA_ENTR], format=DATE_FORMAT, errors='coerce')

                # Sort by CONST_DATA_ENTR if the column exists
                if CONST_DATA_ENTR in filtered_df.columns:
                    filtered_df = filtered_df.sort_values(by=CONST_DATA_ENTR, ascending=True)

                # Replace NaT with '-'
                filtered_df[CONST_DATA_ENTR] = filtered_df[CONST_DATA_ENTR].apply(lambda x: x.strftime(DATE_FORMAT) if pd.notna(x) else '-')

                # Replace NaN or empty string with "-"
                filtered_df = filtered_df.replace({pd.NA: "-", pd.NaT: "-"})

                # Store the mapping of Treeview indices to DataFrame indices
                new_tree_index_map = {}
                for idx, row in filtered_df.iterrows():
                    row_list = row.tolist()
                    tree_item = self.tree.insert('', 'end', values=row_list)
                    new_tree_index_map[tree_item] = idx

                # Remove old items
                old_items = set(self.tree_index_map.keys()) - set(new_tree_index_map.keys())
                for item in old_items:
                    self.tree.delete(item)

                # Update existing items
                for item, idx in new_tree_index_map.items():
                    if item not in self.tree_index_map:
                        continue
                    self.tree.item(item, values=filtered_df.loc[idx].tolist())

                # Update Treeview index map
                self.tree_index_map = new_tree_index_map

                # Adjust column widths based on content length
                self.adjust_column_widths()

                get_important_jobs_data(self.jobs_df, self.added_jobs_df)
                refresh_all_windows()

        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "No data available to refresh the view.")
        except AttributeError as e:
            messagebox.showerror("Error", f"Attribute error: {e}")
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

        # Ensure CONST_DATA_ENTR is string and handle NaN values
        updated_job[CONST_DATA_ENTR] = str(updated_job[CONST_DATA_ENTR]).replace("nan", "-")

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