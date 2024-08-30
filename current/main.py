# Oficial libraries
import json
import tkinter as tk
import pandas as pd
import locale
import logging
import os, sys
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Developed libraries
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
        self.root.title("jBxCC")
        self.root.state('zoomed')
        self.is_loaded_data = False

        # Initialize data structures
        self.jobs_df = pd.DataFrame()
        self.added_jobs_df = pd.DataFrame(columns=[CONST_SACO, CONST_CLIENTE, CONST_DESC, CONST_QUANT, CONST_SECTOR, CONST_ESTADO, CONST_DATA_ENTR])
        self.file_path = ""
        self.selected_job_index = None
        self.editing_added_job = False
        self.tree_index_map = {}

        # Create a frame to hold the initial buttons
        self.initial_button_frame = tk.Frame(root)
        self.initial_button_frame.pack(pady=10)

        # Create select file button
        self.select_file_button = tk.Button(
            self.initial_button_frame, text="Carregar Excel",
            font=('SFPro', 20), pady=5, borderwidth=2, relief=tk.RIDGE,
            command=self.load_file)
        self.select_file_button.pack(side=tk.LEFT, padx=5)

        # Create Load State button
        self.load_state_button = tk.Button(
            self.initial_button_frame, text="Carregar JSON",
            font=('SFPro', 20), pady=5, borderwidth=2, relief=tk.RIDGE,
            command=self.load_state)
        self.load_state_button.pack(side=tk.LEFT, padx=5)

        # Create file help button and pack it to the right side within the same frame
        self.file_help_button = tk.Button(
            root, text="Ajuda", 
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
                + "Apenas apague os ficheiros que tem a certeza que não precisa.\n"
                + "Por favor não interfira com os ficheiros .json, o mesmo pode resultar na corrupção de dados.",
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
        self.add_job_button = tk.Button(self.button_frame, text="Adicionar Encomenda", font=('SFPro', 15), fg='green', pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_add_job_form, state=tk.DISABLED)
        self.edit_job_button = tk.Button(self.button_frame, text="Editar Encomenda", font=('SFPro', 15), fg='#2f73b4',pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_edit_job_form, state=tk.DISABLED)
        self.delete_job_button = tk.Button(self.button_frame, text="Apagar Encomenda", font=('SFPro', 15), fg='red',pady=5, borderwidth=2, relief=tk.RIDGE, command=self.open_delete_job_form, state=tk.DISABLED)
        self.important_jobs_button = tk.Button(self.button_frame, text="Abrir Encomendas Importantes", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.show_important_jobs, state=tk.DISABLED)
        self.close_all_button = tk.Button(self.button_frame, text="Fechar Todas Enc. Import.", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE)
        self.move_win_button = tk.Button(self.button_frame, text="Mover Encomendas Importantes", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE)
        self.data_help_button = tk.Button(self.button_frame, text="Ajuda", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.show_data_help)
        self.reset_screen_button = tk.Button(self.button_frame, text="Voltar Ecrã Principal", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.reset_screen)

        self.add_job_button.pack(side=tk.LEFT, padx=5)
        self.edit_job_button.pack(side=tk.LEFT, padx=5)
        self.delete_job_button.pack(side=tk.LEFT, padx=5)
        self.important_jobs_button.pack(side=tk.LEFT, padx=5)
        self.close_all_button.pack(side=tk.LEFT, padx=5)
        self.move_win_button.pack(side=tk.LEFT, padx=5)
        self.data_help_button.pack(side=tk.LEFT, padx=5)
        self.reset_screen_button.pack(side=tk.LEFT, padx=5, anchor='w')


        self.export_pdf_button = tk.Button(self.button_frame, text="Exportar PDF", font=('SFPro', 15), pady=5, borderwidth=2, relief=tk.RIDGE, command=self.export_to_pdf)
        self.export_pdf_button.pack(side=tk.LEFT, padx=5)


        # Pack button_frame but keep it hidden initially
        self.button_frame.pack_forget()
        self.close_all_button.pack_forget()
        self.move_win_button.pack_forget()

        # Configure the Treeview style
        self.tree_font = ('SFPro', 15)  # Set your desired font and size here
        style = ttk.Style()
        style.configure("Treeview", font=self.tree_font, rowheight=int(self.tree_font[1] * 1.9))  # Adjust row height
        style.configure("Treeview.Heading", font=('SFPro', 16, 'bold'))

        # Create an empty Treeview
        self.tree = ttk.Treeview(root, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Create and initially hide search bar
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.refresh_view)  # Update view on search query change

        search_frame = tk.Frame(root)
        self.search_label = tk.Label(search_frame, text="Procurar:")
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_frame.pack(pady=10)
        self.search_label.pack(side=tk.LEFT)
        self.search_entry.pack(side=tk.LEFT)
        search_frame.pack_forget()

        # Bind the select event
        self.tree.bind('<<TreeviewSelect>>', self.on_treeview_select)

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def export_to_pdf(self):
        """Exports the current jobs data to a multi-page PDF file with horizontal orientation using reportlab."""
        try:
            # Check if there is data in the filtered DataFrame
            if not hasattr(self, 'filtered_df') or self.filtered_df.empty:
                messagebox.showerror("Erro", "Não existem dados para exportar para PDF.")
                return

            # Drop the last column from the DataFrame
            filtered_df = self.filtered_df  # Drop the last column

            # Set locale to Portuguese for date formatting
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            # Format today's date in Portuguese
            today_date = datetime.now().strftime("%d de %B de %Y").capitalize()

            # Generate default filename with today's date
            date_str = datetime.now().strftime("%d-%m-%Y")
            default_filename = f"relatorio_encomendas_{date_str}.pdf"

            # Ask the user where to save the PDF file
            pdf_file = filedialog.asksaveasfilename(
                title="Save PDF File",
                defaultextension=".pdf",
                initialfile=default_filename,
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if not pdf_file:
                return

            # Create a PDF canvas with landscape orientation
            pdf_canvas = canvas.Canvas(pdf_file, pagesize=landscape(A4))
            page_width, page_height = landscape(A4)

            # Determine if the application is running as a standalone executable
            if getattr(sys, 'frozen', False):
                # Get the path to the temporary folder created by PyInstaller
                logo_path = os.path.join(sys._MEIPASS, 'logo_tba.png')
            else:
                # When running in a normal Python environment, use the relative path
                logo_path = 'logo_tba.png'

            # Load the image file
            aspect_ratio = 609 / 1089  # Adjust based on your logo's aspect ratio
            logo_width = 1.15 * inch
            logo_height = logo_width * aspect_ratio  # Calculated height to keep the aspect ratio # Reduced height to maintain aspect ratio


            # Convert filtered DataFrame to list format (reportlab Table requires a list of lists)
            data = [filtered_df.columns.to_list()] + filtered_df.values.tolist()

            # Define title position and spacing
            title_spacing = 0.5 * inch  # Adjust space between title and table

            # Define the color for the title
            title_color = "#2f73b4"  # Hex color code

            # Define styles for text wrapping in cells
            styles = getSampleStyleSheet()
            normal_style = styles['Normal']
            normal_style.wordWrap = 'CJK'  # Enable word wrapping for CJK text

            # Function to create a Paragraph for text wrapping in cells
            def wrap_text(text):
                """Wrap text in a cell using Paragraph."""
                return Paragraph(str(text), style=normal_style)

            # Convert DataFrame data to wrapped text
            wrapped_data = [[wrap_text(cell) for cell in row] for row in data]

            # Define table styles with a gray background for the header
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])

            # Calculate column widths dynamically based on the maximum text width in each column
            def calculate_column_widths(data, max_width):
                """Calculate column widths based on maximum text wrapping within given width."""
                col_widths = []
                for col_idx in range(len(data[0])):
                    # Calculate max width needed for each column
                    max_col_width = max(wrap_text(row[col_idx]).wrap(max_width / len(data[0]), 0)[1] for row in data)
                    col_widths.append(min(max_col_width + 20, max_width / len(data[0])))  # Adjust width and padding
                return col_widths

            # Margin settings
            side_margin = 0.5 * inch  # Reduced left and right margins
            top_margin = 0.75 * inch  # Adjusted top margin to include title spacing
            bottom_margin = inch  # Keep bottom margin as it was

            # Pagination settings
            max_table_height = page_height - top_margin - bottom_margin - title_spacing  # Calculate max table height for pagination

            def draw_table(data, start_row, include_header=True):
                """Draw the table on the PDF canvas with pagination."""
                if start_row >= len(data):  # Safety check to avoid empty data being passed
                    return 0  # No rows drawn if we reach past the end of data

                # Include header if specified, otherwise only data rows
                table_data = [data[0]] + data[start_row:]
                col_widths = calculate_column_widths(data, page_width - 2 * side_margin)  # Adjust column widths based on data

                # Always include header row (repeatRows=1)
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                table.setStyle(table_style)

                # Calculate how many rows fit on the page
                table.wrapOn(pdf_canvas, page_width, page_height)
                table_height = table._height

                # If table height exceeds page height, calculate rows that fit
                if table_height > max_table_height:
                    rows_that_fit = 0
                    current_height = 0
                    for i, row in enumerate(table_data):
                        row_height = Table([row], colWidths=col_widths).wrapOn(pdf_canvas, page_width, page_height)[1]
                        if current_height + row_height <= max_table_height:
                            current_height += row_height
                            rows_that_fit = i + 1
                        else:
                            break
                    table_data = table_data[:rows_that_fit]

                # Draw the table
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                table.setStyle(table_style)
                table.wrapOn(pdf_canvas, page_width, page_height)
                table.drawOn(pdf_canvas, side_margin, page_height - top_margin - table._height - title_spacing)  # Adjust position with title spacing

                return len(table_data) - 1  # Return number of data rows drawn

            def draw_logo():
                """Draws the logo on the top right of the page."""
                # Position the image at the top-right corner, adjusting for image width and height
                pdf_canvas.drawImage(logo_path, page_width - side_margin - logo_width, page_height - top_margin - (logo_height / 2.25), width=logo_width, height=logo_height)

            # Draw the first page with header, title, and logo
            draw_logo()  # Draw logo
            pdf_canvas.setFont("Helvetica-Bold", 14)
            pdf_canvas.setFillColor(title_color)  # Set title color
            pdf_canvas.drawString(0.5 * inch, page_height - 0.75 * inch, f"Relatório de encomendas - {today_date}")

            rows_drawn = draw_table(wrapped_data, 1, include_header=True)
            current_row = rows_drawn + 1  # Start from the next row for subsequent pages

            # Loop through data and create tables for each subsequent page
            while current_row < len(wrapped_data):
                pdf_canvas.showPage()  # Create a new page in the PDF
                draw_logo()  # Draw logo on each page
                pdf_canvas.setFont("Helvetica-Bold", 14)
                pdf_canvas.setFillColor(title_color)  # Set title color on subsequent pages
                pdf_canvas.drawString(0.5 * inch, page_height - 0.75 * inch, f"Relatório de Vagas - {today_date}")  # Draw title on subsequent pages
                rows_drawn = draw_table(wrapped_data, current_row, include_header=True)
                current_row += rows_drawn

            # Save the PDF
            pdf_canvas.save()

            messagebox.showinfo("Sucesso", "Dados exportados para PDF com sucesso!.")
            self.root.focus_force()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar PDF. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")

    def reset_screen(self):
        response = messagebox.askyesno("Confirmar", "Tem a certeza que quer voltar ao ecrã inicial? Todo o progresso será perdido")
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
                if isinstance(data, dict) and 'data' in data:
                    loaded_data = data['data']

                    # Load jobs_df
                    if 'jobs_df' in loaded_data:
                        self.jobs_df = pd.DataFrame(loaded_data['jobs_df'])
                    else:
                        messagebox.showerror('Erro', 'Dados incompletos. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação)')
                        self.root.focus_force()
                        return

                    # Load added_jobs_df
                    if 'added_jobs_df' in loaded_data:
                        self.added_jobs_df = pd.DataFrame(loaded_data['added_jobs_df'])
                        if self.added_jobs_df.empty:
                            # Reinitialize with the correct columns if loaded DataFrame is empty
                            self.added_jobs_df = pd.DataFrame(columns=[CONST_SACO, CONST_CLIENTE, CONST_DESC, CONST_QUANT, CONST_SECTOR, CONST_ESTADO, 'URGENCIA', CONST_DATA_ENTR])
                    else:
                        messagebox.showerror('Erro', 'Dados incompletos. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação)')
                        self.root.focus_force()
                        return

                    # Clear existing items
                    # self.tree.delete(*self.tree.get_children())

                    # Insert data into Treeview using identifiers from tree_index_map
                    if 'tree_index_map' in data:
                        self.tree_index_map = data['tree_index_map']
                    else:
                        self.tree_index_map = {}

                    for identifier, idx in self.tree_index_map.items():
                        if idx < len(self.jobs_df):
                            row = self.jobs_df.iloc[idx]
                            row_list = row.tolist()
                            self.tree.insert('', 'end', values=row_list, iid=identifier)

                    # Hide initial elements and show success message
                    self.initial_button_frame.pack_forget()
                    self.warning_frame.pack_forget()
                    self.file_help_button.pack_forget()
                    messagebox.showinfo('Sucesso', 'Dados restaurados com sucesso!')
                    
                    # Set up Treeview columns

                    self.tree['columns'] = COLUMN_NAMES
                    for col in self.tree['columns']:
                        self.tree.heading(col, text=col)
                        self.tree.column(col, anchor="w")

                    self.refresh_view()
                    self.root.focus_force()
                    self.is_loaded_data = True
                    self.enable_buttons()
                else:
                    messagebox.showerror('Erro', 'Esperado dicionário com chaves de dados. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação).')
                    self.root.focus_force()
            else:
                messagebox.showerror('Erro', 'Falha ao carregar dados')
                self.root.focus_force()
        except json.JSONDecodeError:
            messagebox.showerror('Erro', 'Erro ao descodificar dados. O ficheiro pode ter sido corrompido.')
            self.root.focus_force()
        except pd.errors.EmptyDataError:
            messagebox.showerror('Erro', 'Dados vazios ou não podem ser processados.')
            self.root.focus_force()
        except KeyError as e:
            messagebox.showerror('Error', f'Chave esperada desaparecida. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}')
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror('Erro', f'Oops! Um erro inesperado aconteceu. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}')
            self.root.focus_force()

    def on_close(self):
        """Handle the window closing event."""
        try:
            if self.is_loaded_data:
                result = messagebox.askyesno("Guardar estado", "Quer guardar o estado da aplicação?")
                self.root.focus_force()

                if result:
                    # Standardize column names
                    self.jobs_df.columns = self.jobs_df.columns.astype(str).str.replace(ORI_CONST_SECTOR, CONST_SECTOR, regex=False)
                    self.added_jobs_df.columns = self.added_jobs_df.columns.astype(str).str.replace(ORI_CONST_SECTOR, CONST_SECTOR, regex=False)

                    self.jobs_df.columns = self.jobs_df.columns.astype(str).str.replace(ORI_CONST_DESC, CONST_DESC, regex=False)
                    self.added_jobs_df.columns = self.added_jobs_df.columns.astype(str).str.replace(ORI_CONST_DESC, CONST_DESC, regex=False)

                    self.jobs_df.columns = self.jobs_df.columns.astype(str).str.replace(ORI_CONST_URG, CONST_URG, regex=False)
                    self.added_jobs_df.columns = self.added_jobs_df.columns.astype(str).str.replace(ORI_CONST_URG, CONST_URG, regex=False)

                    # Create state dictionary with DataFrames included
                    state = {
                        'jobs_df': self.jobs_df.to_dict(orient='records'),
                        'added_jobs_df': self.added_jobs_df.to_dict(orient='records'),
                        'tree_index_map': self.tree_index_map
                    }

                    # Process the date entries in 'added_jobs_df'
                    for job in state['added_jobs_df']:
                        if job.get(CONST_DATA_ENTR) == 'DD/MM/YYYY_HH:MM':
                            job[CONST_DATA_ENTR] = '-'

                    # Save the state to a JSON file
                    if json_operations.save_json_file({'data': state}):
                        messagebox.showinfo("Info", "Estado guardado com sucesso.\nA aplicação vai agora fechar :).")
                    else:
                        messagebox.showerror("Erro", "Erro ao guardar estado.\nA aplicação não vai fechar :(.")
                        self.root.focus_force()
                        return

                self.root.destroy()
                self.root.quit()
            else:
                self.root.destroy()
                self.root.quit()
        except IOError as e:
            messagebox.showerror("Erro", f"Ficheiro OG em falta. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação): {e}")
            self.root.focus_force()
            self.root.destroy()
            self.root.quit()
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erros ao codificar dados preveniram o salvamento de estad. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação)")
            self.root.focus_force()
            self.root.destroy()
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Erro", f"Oops! Um erro inesperado aconteceu. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
            self.root.focus_force()
            self.root.destroy()
            self.root.quit()

    def on_treeview_select(self, event):
        """Handle Treeview item selection."""
        try:
            selected_item = self.tree.selection()
            if selected_item:
                tree_item = selected_item[0]
                if tree_item in self.tree_index_map:
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
                    # Handle missing item in map
                    messagebox.showerror("Erro", f"Entrda da árvore '{tree_item}' nao encontrado no mapa de indexes. Verifique que o ficheir JSON não foi corrompido. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação)")
                    self.selected_job_index = None
                    self.editing_added_job = False
                    self.edit_job_button.configure(state=tk.DISABLED)
                    self.delete_job_button.configure(state=tk.DISABLED)
            else:
                self.selected_job_index = None
                self.editing_added_job = False
                self.edit_job_button.configure(state=tk.DISABLED)
                self.delete_job_button.configure(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Erro", f"Oops! Um erro inesperado aconteceu (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
            logging.error(f"Exception in on_treeview_select: {e}")

    def open_add_job_form(self):
        AddJobForm(self.root, self.add_job)

    def validate_job(self, job):
        # Check for required fields
        required_fields = [CONST_SACO, CONST_CLIENTE, CONST_DESC, CONST_QUANT, CONST_SECTOR]
        for field in required_fields:
            if not job.get(field):
                return False, f"O campo '{field}' é obrigatório."

        # The date field is optional and not validated
        return True, ""

    def add_job(self, job):
        valid, message = self.validate_job(job)
        if not valid:
            messagebox.showerror("Erro validação", message)
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
                title="Selecione ficheiro Excel",
                filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
            )

            if not self.file_path:
                raise FileNotFoundError("Nenhum ficheiro seleciona. Por favor tente de novo.")

            self.is_loaded_data = True
            self.initial_button_frame.pack_forget()

            self.load_jobs()

            self.root.focus_force()

        except FileNotFoundError as fnf_error:
            messagebox.showerror("Erro ficheiro", f"{fnf_error} (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação)")
            self.root.focus_force()
        except pd.errors.EmptyDataError as empty_data_error:
            messagebox.showerror("Erro de dados", f"Ficheiro vazio ou não pode ser lido. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {empty_data_error}")
            self.root.focus_force()
        except ValueError as value_error:
            messagebox.showerror("Erro valor", f"Erro valor. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {value_error}")
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror("Erro", f"Oops, um erro inesperado aconteceu. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
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
            df.columns = [CONST_SACO, CONST_CLIENTE, CONST_DESC, CONST_QUANT, CONST_SECTOR, CONST_ESTADO, CONST_URG, CONST_DATA_ENTR]

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

            messagebox.showinfo('Sucesso', 'Dados importados de ficheiro Excel com sucesso! :)')

            self.tree['columns'] = COLUMN_NAMES
            for col in self.tree['columns']:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="w")

            self.refresh_view()

            self.enable_buttons()

        except FileNotFoundError:
            messagebox.showerror("Erro ficheiro", f"Ficheiro não encontrado.")
            self.root.focus_force()
        except pd.errors.EmptyDataError:
            messagebox.showerror("Erro dados", "O ficheiro selecionado está vazio ou não poder ser lido. Verifique o mesmo.")
            self.root.focus_force()
        except pd.errors.ParserError:
            messagebox.showerror("Erro parse", "Ocorreu um erro ao parsar ficheiro. Verique o mesmo")
            self.root.focus_force()
        except ValueError as value_error:
            messagebox.showerror("Erro valor", f"Value error occurred: {value_error}")
            self.root.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Erro valor. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {value_error}")
            self.root.focus_force()

    def filter_by_date(self, df, query):
        """Filter DataFrame based on date components specified in the query."""
        def match_date(date, query):
            if pd.isna(date):
                return False
            
            try:
                if query.startswith("dia:"):
                    day = int(query.split(':')[1])
                    return date.day == day
                elif query.startswith("mes:"):
                    month = int(query.split(':')[1])
                    return date.month == month
                elif query.startswith("ano:"):
                    year = int(query.split(':')[1])
                    return date.year == year
            except ValueError:
                return False
            
            return False

        # Convert CONST_DATA_ENTR to datetime
        df[CONST_DATA_ENTR] = pd.to_datetime(df[CONST_DATA_ENTR], format=DATE_FORMAT, errors='coerce')

        # Apply the date filter
        self.filtered_df = df[df[CONST_DATA_ENTR].apply(lambda date: match_date(date, query))]

        return self.filtered_df

    def filter_data(self, df, query):
        """Filter the DataFrame based on the search query."""

        # Initialize the filtered DataFrame
        self.filtered_df = df.copy()

        # Apply specific filters based on the query prefix
        if query.startswith("dia:") or query.startswith("mes:") or query.startswith("ano:"):
            # Use the existing filter_by_date for date-based queries
            self.filtered_df = self.filter_by_date(self.filtered_df, query)
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
                self.filtered_df = self.filtered_df[self.filtered_df[column_to_filter].astype(str).str.contains(search_value, case=False, na=False)]
            else:
                # Apply general search filter
                search_value = query.strip().lower()
                self.filtered_df = self.filtered_df[self.filtered_df.apply(
                    lambda row: any(search_value in str(row[col]).lower() for col in self.filtered_df.columns),
                    axis=1
                )]

        return self.filtered_df

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

            # Only proceed if there is data to combine
            if frames_to_concat:
                combined_df = pd.concat(frames_to_concat, ignore_index=True)

                # Apply filtering
                self.filtered_df = self.filter_data(combined_df, search_query)

                # Convert CONST_DATA_ENTR to datetime format for sorting
                self.filtered_df[CONST_DATA_ENTR] = pd.to_datetime(self.filtered_df[CONST_DATA_ENTR], format=DATE_FORMAT, errors='coerce')

                # Sort by CONST_DATA_ENTR if the column exists
                if CONST_DATA_ENTR in self.filtered_df.columns:
                    self.filtered_df = self.filtered_df.sort_values(by=CONST_DATA_ENTR, ascending=True)

                # Replace NaT with '-'
                self.filtered_df[CONST_DATA_ENTR] = self.filtered_df[CONST_DATA_ENTR].apply(lambda x: x.strftime(DATE_FORMAT) if pd.notna(x) else '-')

                # Replace NaN or empty string with "-"
                self.filtered_df = self.filtered_df.replace({pd.NA: "-", pd.NaT: "-"})

                # Store the mapping of Treeview indices to DataFrame indices
                new_tree_index_map = {}

                # Remove old items from Treeview first
                self.tree.delete(*self.tree.get_children()) 

                # Insert new data into Treeview
                for idx, row in self.filtered_df.iterrows():
                    row_list = row.tolist()
                    tree_item = self.tree.insert('', 'end', values=row_list)
                    new_tree_index_map[tree_item] = idx

                # Update Treeview index map
                self.tree_index_map = new_tree_index_map

                # Adjust column widths based on content length
                self.adjust_column_widths()

                get_important_jobs_data(self.jobs_df, self.added_jobs_df)
                refresh_all_windows()

            else:
                # Clear the Treeview if no data is available
                self.tree.delete(*self.tree.get_children())
                self.tree_index_map.clear()

        except pd.errors.EmptyDataError:
            messagebox.showerror("Erro", "Não existem dados para atualizar ecrã")
        except AttributeError as e:
            messagebox.showerror("Erro", f"Erro de atributo. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar o ecrã {e}. (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) :)")
            logging.error(f"Exception in refresh_view: {e}")

    def adjust_column_widths(self):
        column_exc = ['DESCRIÇÃO DO TRABALHO']

        for col in self.tree['columns']:
            col_values = [self.tree.heading(col, 'text')]  # Start with column header text
            
            # Iterate over all children (rows) in the Treeview
            for child in self.tree.get_children():
                # Safely get the index of the column in the values list
                col_index = self.tree['columns'].index(col)
                
                # Safely access the values, checking if the index exists
                child_values = self.tree.item(child)['values']
                if len(child_values) > col_index:  # Ensure the index exists in the values list
                    col_values.append(str(child_values[col_index]))
                else:
                    # Handle cases where the column index is not present in the child's values
                    col_values.append('')

            # Check if col_values is not empty to avoid division by zero (when user filters and there's nothing to display)
            if len(col_values) > 1:
                # Calculate the average length based on the exclusion list
                if col in column_exc:
                    avg_length = max(
                        int(len(col_values[0]) * 2), 
                        sum(len(value) for value in col_values[1:]) / max(1, len(col_values[1:]))
                    )
                else:
                    avg_length = max(
                        len(col_values[0]), 
                        sum(len(value) for value in col_values[1:]) / max(1, len(col_values[1:]))
                    )
            else:
                avg_length = len(col_values[0])

            # Set the new width based on calculated average length
            new_width = int(avg_length) * 5

            # Ensure the width is at least as wide as the column header text
            min_width = len(self.tree.heading(col, 'text')) * 5
            new_width = max(new_width, min_width)

            # Set the column width
            self.tree.column(col, width=new_width)

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
            messagebox.showerror("Erro validação", message)
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
            messagebox.showerror("Erro", "Encomenda não encontrada")
            self.root.focus_force()  # Re-focus on the main window
        
        self.selected_job_index = None
        self.edit_job_button.configure(state=tk.DISABLED)
        self.delete_job_button.configure(state=tk.DISABLED)

    def show_important_jobs(self):
        show_important_jobs(self.root, self.jobs_df, self.added_jobs_df, self.important_jobs_button, self.close_all_button, self.move_win_button)

    def add_important_jobs_window(self):
        add_important_jobs_window(self.root, self.jobs_df, self.added_jobs_df, self.important_jobs_button, self.close_all_button, self.move_win_button)

if __name__ == "__main__":
    root = tk.Tk()
    app = JobDisplayApp(root)
    root.mainloop()