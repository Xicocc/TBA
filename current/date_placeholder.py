# Oficial libraries
import tkinter as tk

class PlaceholderEntry(tk.Entry):
    def __init__(self, parent, placeholder, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'light gray'  # Color for placeholder text
        self.default_fg_color = self.cget("fg")  # Default text color
        self.set_placeholder()
        self.bind("<FocusIn>", lambda event: self.on_focus_in())
        self.bind("<FocusOut>", lambda event: self.on_focus_out())

    def set_placeholder(self):
        if not self.get() or self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

    def on_focus_in(self):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg_color)

    def on_focus_out(self):
        if not self.get():
            self.set_placeholder()