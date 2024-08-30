# Oficial libraries
import json
import tkinter as tk
import logging
from tkinter import filedialog, messagebox
from datetime import datetime

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def save_json_file(data):
    root = tk.Tk()
    root.withdraw()

    date_str = datetime.now().strftime("%d-%m-%Y")
    default_filename = f"state_{date_str}.json"

    file_path = filedialog.asksaveasfilename(
        title="Save JSON File",
        defaultextension=".json",
        initialfile=default_filename,
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if file_path:
        if not file_path.lower().endswith('.json'):
            file_path += '.json'

        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except IOError as e:
            messagebox.showerror("Erro", f"Erro ao escrever ficheiro JSON (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
            logging.error(f"IOError: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Opps! Um erro inesperado aconteceu (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
            logging.error(f"Unexpected Error: {e}")
    return False

def load_json_file():
    # Opens a file dialog for the user to select a JSON file and loads its contents.
    # Returns -> dict: Contents of the JSON file as a dictionary.
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if file_path:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Falha ao descodificar ficheiro JSON. Por favor verifique que está a usar o ficheiro JSON correto")
        except Exception as e:
            messagebox.showerror("Erro", f"Opps! Um erro inesperado aconteceu (Este erro é, provavelmente, do sistema, não é culpa sua, por favor tente fechar e voltar a abrir a aplicação) : {e}")
    return None