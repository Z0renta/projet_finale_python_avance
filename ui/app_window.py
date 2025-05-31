import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import create_table, clear_table, insert_data, fetch_all
from api import fetch_posts
import os
import requests
import re
from collections import Counter
from docx import Document
from docx.shared import Inches
from PIL import Image
from io import BytesIO
from collections import defaultdict


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
        data_menu.add_command(label="Afficher l'agrégation", command=self.show_aggregation)
        menu_bar.add_cascade(label="Données", menu=data_menu)

        book_menu = tk.Menu(menu_bar, tearoff=0)
        book_menu.add_command(label="Traiter un livre", command=self.process_book)
        menu_bar.add_cascade(label="Livre", menu=book_menu)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(label="Changer la couleur", command=self.set_bg_color)
        menu_bar.add_cascade(label="Options", menu=options_menu)

        self.config(menu=menu_bar)

    def create_widgets(self):
        self.text_area = tk.Text(self)
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def clear_database(self):
        confirm = messagebox.askyesno("Confirmation", "Supprimer complètement le fichier de base de données ?")
        if confirm:
            db_path = "data/donnees.db"
            if os.path.exists(db_path):
                os.remove(db_path)
                messagebox.showinfo("Succès", "Le fichier de base de données a été supprimé.")
            else:
                messagebox.showwarning("Erreur", "Le fichier n'existe pas.")

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

    def show_aggregation(self):
        rows = fetch_all()
        if not rows:
            messagebox.showinfo("information", "Aucune donnée à afficher.")
            return

        user_length = defaultdict(list)

        for row in rows:
            user_id = row[1]
            body_length = len(row[3])
            user_length[user_id].append(body_length)

        user_avg = {user: sum(lengths) / len(lengths) for user, lengths in user_length.items()}

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Moyenne des longueurs de texte par utilisateur :\n\n")
        for user, avg in sorted(user_avg.items()):
            self.text_area.insert(tk.END, f"User {user} : {avg:.2f} caractères en moyenne\n")


        fig, ax = plt.subplots()
        ax.bar(user_avg.keys(), user_avg.values())
        ax.set_title("Longueur moyenne des posts par utilisateur")
        ax.set_xlabel("User ID")
        ax.set_ylabel("Longueur moyenne (caractères)")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def set_bg_color(self):
        color = simpledialog.askstring("Options", "Entrez une couleur de fond :")
        if color:
            self.text_area.config(bg=color)


    # ======= MÉTHODES LIVRE =======

    def download_book_text(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        return response.text

    def extract_metadata_and_first_chapter(self, text):
        title_match = re.search(r'Title:\s*(.*)', text)
        title = title_match.group(1).strip() if title_match else "Inconnu"

        author_match = re.search(r'Author:\s*(.*)', text)
        author = author_match.group(1).strip() if author_match else "Inconnu"

        chapters = re.split(r'\nChapter [0-9IVXLC]+\.*\s*\n', text, flags=re.IGNORECASE)
        if len(chapters) > 1:
            first_chapter = chapters[1].strip()
        else:
            first_chapter = text

        return title, author, first_chapter

    def count_words_per_paragraph(self, chapter_text):
        paragraphs = [p.strip() for p in chapter_text.split('\n\n') if p.strip()]
        counts = []
        for p in paragraphs:
            nb_mots = len(p.split())
            nb_mots_rounded = round(nb_mots / 10) * 10
            counts.append(nb_mots_rounded)
        return counts

    def paragraph_length_distribution(self, counts):
        counter = Counter(counts)
        sorted_counts = sorted(counter.items())
        return sorted_counts

    def download_image_1(self, url, save_path='image1.jpg'):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.save(save_path)
        return save_path

    def crop_and_resize_image(self, path, crop_box=(100, 100, 400, 400), size=(300, 300)):
        img = Image.open(path)
        cropped = img.crop(crop_box)
        resized = cropped.resize(size)
        resized.save(path)

    def overlay_logo_on_image(self, background_path, logo_path, output_path, position=(10, 10), rotation_angle=45):
        background = Image.open(background_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.rotate(rotation_angle, expand=True)
        background.paste(logo, position, logo)
        background.save(output_path)

    def process_book(self):
        url_book = simpledialog.askstring("Livre", "Entrez l'URL du livre texte (Project Gutenberg) :")
        if not url_book:
            return

        # Télécharger le texte, extraire métadonnées + 1er chapitre
        text = self.download_book_text(url_book)
        title, author, first_chapter = self.extract_metadata_and_first_chapter(text)

        # Afficher les infos dans le text_area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, f"Titre: {title}\nAuteur: {author}\n\nPremier Chapitre:\n{first_chapter[:2000]}...")

        # Analyse paragraphes (mots par paragraphe, arrondis)
        counts = self.count_words_per_paragraph(first_chapter)
        distrib = self.paragraph_length_distribution(counts)

        # Graphique distribution longueurs paragraphes
        x, y = zip(*distrib)
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_xlabel("Nombre de mots par paragraphe (arrondi)")
        ax.set_ylabel("Nombre de paragraphes")
        ax.set_title("Distribution des longueurs des paragraphes")
        plt.show()

        # Télécharger l'image 1
        url_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Old_book_icon.svg/1024px-Old_book_icon.svg.png"
        img1_path = self.download_image_1(url_img)

        # Recadrer et redimensionner
        self.crop_and_resize_image(img1_path)

        # Ajouter logo (image n°2 en noir et blanc sur disque)
        logo_path = "logo_bw.png"  # Met ici ton chemin vers le logo B/N
        output_path = "final_image.png"
        self.overlay_logo_on_image(img1_path, logo_path, output_path)

        messagebox.showinfo("Terminé", f"Traitement terminé ! Image finale sauvegardée dans {output_path}")

