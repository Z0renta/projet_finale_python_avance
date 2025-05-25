import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import create_table, clear_table, insert_data, fetch_all
from api import fetch_posts

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Application de Données JSON")
        self.geometry("800x600")
        create_table()
        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menu_bar = tk.Menu(self)
        data_menu = tk.Menu(menu_bar, tearoff=0)
        data_menu.add_command(label="Effacer la base de données", command=self.clear_database)
        data_menu.add_command(label="Télécharger les données", command=self.download_data)
        data_menu.add_command(label="Afficher le graphique", command=self.show_graph)
        menu_bar.add_cascade(label="Données", menu=data_menu)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(label="Changer la couleur", command=self.set_bg_color)
        menu_bar.add_cascade(label="Options", menu=options_menu)

        self.config(menu=menu_bar)

    def create_widgets(self):
        self.text_area = tk.Text(self)
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def clear_database(self):
        clear_table()
        messagebox.showinfo("Succès", "La base de données a été effacée.")

    def download_data(self):
        try:
            data = fetch_posts()
            insert_data(data)
            self.display_data()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def display_data(self):
        rows = fetch_all()
        self.text_area.delete(1.0, tk.END)
        for row in rows:
            self.text_area.insert(tk.END, f"ID: {row[0]}, UserID: {row[1]}\nTitre: {row[2]}\nCorps: {row[3]}\n\n")

    def show_graph(self):
        rows = fetch_all()
        user_counts = {}
        for row in rows:
            user_counts[row[1]] = user_counts.get(row[1], 0) + 1

        fig, ax = plt.subplots()
        ax.bar(user_counts.keys(), user_counts.values())
        ax.set_xlabel("UserID")
        ax.set_ylabel("Nombre de posts")
        ax.set_title("Posts par utilisateur")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def set_bg_color(self):
        color = simpledialog.askstring("Options", "Entrez une couleur de fond :")
        if color:
            self.text_area.config(bg=color)