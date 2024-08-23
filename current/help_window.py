import tkinter as tk

class HelpFile:
    def __init__(self, root):
        self.root = root
        self.create_help_window()
        
    def create_help_window(self):
        # Create a new Toplevel window
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("Help - File Loading")
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.help_window.geometry(f'{self.screen_width}x{self.screen_height}')
        print(str(self.screen_width))
        print(str(self.screen_height))
        # Prevent resizing
        self.help_window.resizable(False, False)
        self.help_window.withdraw()  # Hide the window initially

        # Set the HelpFile window to be on top of the parent window
        self.help_window.transient(self.root)
        self.help_window.grab_set()

        # Create a frame for better control of content layout
        frame = tk.Frame(self.help_window, padx=20, pady=20)
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to allow resizing
        self.help_window.grid_rowconfigure(0, weight=1)
        self.help_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Create a Text widget with the help message
        help_message = """
        - Pode submeter 2 tipos de ficheiros na aplicação:

            - Ficheiro excel - Load File
            - Ficheiro JSON - Load State

        O ficheiro excel submetido deve ter a formatação correta (A qual é do conhecimento dos colaboradores). \n
        O ficheiro JSON é gerado automaticamente no processo de salvamento do estado da aplicação e NÃO deve ser alterado manualmente, correndo o risco de corromper o mesmo.
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 18), padx=20, pady=20, height=20)  # Set a fixed height
        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Create a close button
        close_button = tk.Button(frame, text="OK", font=('Arial', 18),command=self.help_window.destroy, borderwidth=2, relief=tk.RIDGE, pady=1)
        close_button.grid(row=1, column=0, pady=5, sticky='s')

        # Center the window after it has been fully rendered to avoid top left flickering
        self.help_window.update_idletasks()
        self.center_window_Add_Edit(self.help_window)  # Center the help window itself
        self.help_window.deiconify()

        # Make sure the help window stays on top and disable interaction with the parent
        self.help_window.focus_set()
        self.help_window.grab_set()
        
    def center_window_Add_Edit(self, window):
        window.update_idletasks()
        width = 800
        height = 450
        screen_width = window.winfo_screenwidth() - 16
        screen_height = window.winfo_screenheight() - 75
        print(str(screen_width))
        print(str(screen_height))
        x = 0
        y = 0
        window.geometry(f'{screen_width}x{screen_height}+{x}+{y}')

    def center_window(self):
        # Get the screen width and height, subtracting 50 pixels from height for the taskbar
        screen_width = self.help_window.winfo_screenwidth()
        screen_height = self.help_window.winfo_screenheight() - 50  # Adjust this value if needed

        # Calculate the window size to avoid offset
        window_width = screen_width
        window_height = screen_height
        x_position = 0
        y_position = 0

        # Set the geometry with calculated values
        self.help_window.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')


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

        1 - Adicionar um novo trabalho (Botão Add New Job).
        2 - Editar/Apagar um trabalho já existente na tabela (Botões Edit Job e Delete Job)
        3 - Fazer uma pesquisa por palavras chave na barra "Search"
        4 - Abrir uma (ou mais) janela que mostra os oito trabalhos mais urgentes ordenados por data de entrega. 

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

            !Lembre-se sempre de respeitar o formato da data de entrega!
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 18), padx=20, pady=20)
        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create a close button
        close_button = tk.Button(frame, text="OK", font=('Arial', 20),command=self.help_window.destroy, borderwidth=2, relief=tk.RIDGE, pady=5)
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

class HelpAdd:
    def __init__(self, root):
        self.root = root
        self.create_help_window()

    def create_help_window(self):
        # Create a new Toplevel window
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("Help - Add Job")
        self.help_window.geometry('600x400')  # Explicitly set the size to 600x400
        self.help_window.resizable(False, False)  # Prevent the window from being resized
        self.help_window.withdraw()  # Hide window until it's fully set up

        # Set the HelpFile window to be on top of the parent window
        self.help_window.transient(self.root)
        self.help_window.grab_set()

        # Create a frame for better control of content layout
        frame = tk.Frame(self.help_window, padx=20, pady=20)
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to allow resizing
        self.help_window.grid_rowconfigure(0, weight=1)
        self.help_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Create a Text widget with the help message
        help_message = """
        Para adicionar uma nova entrada na tabela com sucesso, a mesma deve ter, pelo menos, os seguintes campos preenchidos:
            -  Saco
            -  Cliente
            -  Descrição do trabalho
            -  Quantidade
            -  Sector em que está
        
        Caso queira adicionar um valor de data de entrega, lembre-se de respeitar sempre o formato da mesma!
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 18), padx=20, pady=20)
        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create a close button
        close_button = tk.Button(frame, text="OK", font=('Arial', 20), command=self.help_window.destroy, borderwidth=2, relief=tk.RIDGE, pady=5)
        close_button.grid(row=1, column=0, pady=10, sticky="s")

        self.help_window.update_idletasks()
        center_window_Add_Edit(self.help_window)  # Center the help window itself
        self.help_window.deiconify()

        # Make sure the help window stays on top and disable interaction with the parent
        self.help_window.focus_set()
        self.help_window.grab_set()

class HelpEdit:
    def __init__(self, root):
        self.root = root
        self.create_help_window()

    def create_help_window(self):
        # Create a new Toplevel window
        self.help_window = tk.Toplevel(self.root)
        self.help_window.title("Help - Edit Job")
        self.help_window.geometry('600x400')  # Explicitly set the size to 600x400
        self.help_window.resizable(False, False)  # Prevent the window from being resized
        self.help_window.withdraw()  # Hide window until it's fully set up

        # Set the HelpFile window to be on top of the parent window
        self.help_window.transient(self.root)
        self.help_window.grab_set()

        # Create a frame for better control of content layout
        frame = tk.Frame(self.help_window, padx=20, pady=20)
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to allow resizing
        self.help_window.grid_rowconfigure(0, weight=1)
        self.help_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Create a Text widget with the help message
        help_message = """
        Para editar uma entrada na tabela com sucesso, a mesma deve ter, pelo menos, os seguintes campos preenchidos:
            -  Saco
            -  Cliente
            -  Descrição do trabalho
            -  Quantidade
            -  Sector em que está
        
        Caso queira adicionar um valor de data de entrega, lembre-se de respeitar sempre o formato da mesma!
        """
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 18), padx=20, pady=20)
        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make text read-only
        text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create a close button
        close_button = tk.Button(frame, text="OK", font=('Arial', 20), command=self.help_window.destroy, borderwidth=2, relief=tk.RIDGE, pady=5)
        close_button.grid(row=1, column=0, pady=10, sticky="s")

        self.help_window.update_idletasks()
        center_window_Add_Edit(self.help_window)  # Center the help window itself
        self.help_window.deiconify()

        # Make sure the help window stays on top and disable interaction with the parent
        self.help_window.focus_set()
        self.help_window.grab_set()

def center_window_Add_Edit(window):
        window.update_idletasks()
        width = 800
        height = 450
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')