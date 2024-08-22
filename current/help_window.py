import tkinter as tk

class HelpFile:
    def __init__(self, root):
        self.root = root
        self.create_help_window()
        
    def create_help_window(self):
        # Create a new Toplevel window
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("Help - File Loading")
        
        # Maximize the window to fill the screen
        self.help_window.state('zoomed')  # This makes the window fill the screen

        # Create a frame for better control of content layout
        frame = tk.Frame(self.help_window)
        frame.pack(expand=True, fill=tk.BOTH)

        # Create a Text widget with the help message
        help_message = """
        - Pode submeter 2 tipos de ficheiros na aplicação:

            - Ficheiro excel - Load File
            - Ficheiro JSON - Load State

        O ficheiro excel submetido deve ter a formatação correta (A qual é do conhecimento dos colaboradores). \n
        O ficheiro JSON é gerado automaticamente no processo de salvamento do estado da aplicação e NÃO deve ser alterado manualmente, correndo o risco de corromper o mesmo.
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 18), padx=20, pady=20)
        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Create a close button
        close_button = tk.Button(frame, text="OK", command=self.help_window.destroy, font=('Arial', 17))
        close_button.pack(pady=10)

        # Keep the help window on top of the main window
        self.help_window.transient(self.root)
        self.help_window.grab_set()  # Capture all user input until the window is closed

        # Center the window after it has been fully rendered to avoid top left flickering
        self.help_window.after_idle(self.center_window)

    def center_window(self):
        width = self.help_window.winfo_screenwidth()
        height = self.help_window.winfo_screenheight()
        self.help_window.geometry(f'{width}x{height}+0+0')  # Adjust size and position

import tkinter as tk

class HelpData:
    def __init__(self, root):
        self.root = root
        self.create_help_window()
        
    def create_help_window(self):
        # Create a new Toplevel window
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("Help - Data Operations")
        
        # Maximize the window to fill the screen
        self.help_window.state('zoomed')  # This makes the window fill the screen

        # Create a frame for better control of content layout
        frame = tk.Frame(self.help_window)
        frame.pack(expand=True, fill=tk.BOTH)

        # Create a Text widget with the help message
        help_message = """
        Neste ecrã pode :

        1 - Adicionar um novo trabalho (Add New Job).
        2 - Editar um trabalho já existente na tabela (Edit Job)
        3 - Apagar um trabalho já existente na tabela (Delete Job)
        4 - Fazer uma pesquisa por palavras chave na barra "Search"

            A pesquisa pode ser feita por:
                - palavras "soltas", como por exemplo:
                    -  livros  - Que irá mostrar todos as entradas na tabela com "livros" em qualquer dos campos.
                - filtros, sendo que os filtros existentes são :
                    -  cliente:  (nome do cliente)
                    -  desc:     (descrição do trabalho)
                    -  quant:    (quantidade)
                    -  sector:   (sector em que está)
                    -  estado:   (Estado do trabalho)
                    -  urg:      (Urgência / Observações)
                    -  obs:      (Urgência / Observações)
                    -  year:     (Ano do trabalho)
                    -  month:    (Mês do trabalho)
                    -  day:      (Dia do trabalho)
            Nota: Os filtro day:, month: e year: apenas são aplicáveis a entradas da tabela com valores de data.

            Para adicionar ou editar um novo trabalho, este deve conter valores de, pelo menos, os seguintes campos:
            - Saco
            - Cliente
            - Descrição do trabalho
            - Quantidade
            - Sector em que está

            !Lembre-se sempre de respeitar o formato da data de entrega!
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 18), padx=20, pady=20)
        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Add a label to instruct the user to scroll
        scroll_instruction = tk.Label(frame, text="Deslize para baixo para ver mais!", font=('Arial', 15), fg='red')
        scroll_instruction.grid(row=1, column=0, pady=(5, 10), sticky="ew")

        # Create a close button
        close_button = tk.Button(frame, text="OK", command=self.help_window.destroy, font=('Arial', 17))
        close_button.grid(row=2, column=0, pady=10)

        # Configure row and column weights for expansion
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_columnconfigure(0, weight=1)

        # Keep the help window on top of the main window
        self.help_window.transient(self.root)
        self.help_window.grab_set()  # Capture all user input until the window is closed

        # Center the window after it has been fully rendered to avoid top left flickering
        self.help_window.after_idle(self.center_window)

    def center_window(self):
        width = self.help_window.winfo_screenwidth()
        height = self.help_window.winfo_screenheight()
        self.help_window.geometry(f'{width}x{height}+0+0')  # Adjust size and position
