import tkinter as tk
from tkinter import messagebox, ttk
import random

# --- DONNÉES COULEURS ---
COULEURS_DISPO = [
    '#FF1493', # ROSE
    '#8e44ad', # Violet
    '#3498db', # Bleu clair
    '#16a085', # Vert d'eau
    '#f1c40f', # Jaune
    '#e67e22', # Orange
    '#2ecc71', # Vert émeraude
    '#FFFFFF', # BLANC
    '#8B4513', # MARRON
    '#2c3e50', # Bleu nuit
    '#c0392b', # Rouge foncé
    '#000000'  # NOIR
]

EMOJIS_DISPO = [
    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', 
    '🐻', '🐼', '🐨', '🐯', '🦁', '🐮',
    '🐷', '🐸', '🐵'
]

COULEUR_DOS = "#bdc3c7" 

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeu de Memory - Complet")
        self.root.geometry("700x850")
        
        self.nb_joueurs_var = tk.IntVar(value=1)
        self.difficulte_var = tk.StringVar(value="12")
        
        self.nb_cartes = 12
        self.mode_chrono = False
        self.mode_emoji = False
        
        self.cartes = []       
        self.boutons = []       
        self.premier_choix = None 
        self.verrouille = False 
        
        self.indices_trouves = [] 
        
        self.scores = [0, 0]
        self.joueur_actuel = 0 
        self.paires_trouvees = 0
        self.coups_solo = 0
        
        self.temps_restant = 0
        self.timer_running = False
        self.joker_utilise = False

        self.menu_etape_1()

    # --- ÉTAPE 1 : CONFIGURATION ---
    def menu_etape_1(self):
        self.vider_fenetre()
        frame = tk.Frame(self.root, pady=20)
        frame.pack()

        tk.Label(frame, text="1. Configuration", font=("Arial", 24, "bold")).pack(pady=20)

        tk.Label(frame, text="Nombre de joueurs :", font=("Arial", 12)).pack()
        ttk.Combobox(frame, textvariable=self.nb_joueurs_var, values=[1, 2], state="readonly").pack(pady=5)

        tk.Label(frame, text="Difficulté :", font=("Arial", 12)).pack(pady=10)
        options = [
            "Très Facile (6 cartes)",
            "Facile (12 cartes)", 
            "Moyen (18 cartes)", 
            "Difficile (24 cartes)", 
            "EXTRÊME (30 cartes)"
        ]
        combo = ttk.Combobox(frame, textvariable=self.difficulte_var, values=options, state="readonly", width=25)
        combo.current(1)
        combo.pack(pady=5)

        tk.Button(frame, text="SUIVANT ➜", bg="#2980b9", fg="white", font=("Arial", 12, "bold"), 
                  command=self.menu_etape_2_choix_mode).pack(pady=30)

    # --- ÉTAPE 2 : CHOIX DU MODE ---
    def menu_etape_2_choix_mode(self):
        selection = self.difficulte_var.get()
        
        if "6" in selection: self.nb_cartes = 6
        elif "12" in selection: self.nb_cartes = 12
        elif "18" in selection: self.nb_cartes = 18
        elif "24" in selection: self.nb_cartes = 24
        elif "30" in selection: self.nb_cartes = 30
        
        self.mode_emoji = (self.nb_cartes == 30)

        self.vider_fenetre()
        frame = tk.Frame(self.root, pady=20)
        frame.pack()

        tk.Label(frame, text="2. Choisissez le Mode", font=("Arial", 24, "bold")).pack(pady=20)
        
        desc = "Extrême (Émojis)" if self.mode_emoji else "Classique (Couleurs)"
        tk.Label(frame, text=f"Niveau : {self.nb_cartes} cartes - {desc}", fg="gray").pack(pady=10)

        btn_normal = tk.Button(frame, text="☕ Mode Détente\n(Pas de chrono)", 
                               bg="#27ae60", fg="white", font=("Arial", 14), width=30, height=3,
                               command=lambda: self.lancer_partie(chrono=False))
        btn_normal.pack(pady=10)

        btn_chrono = tk.Button(frame, text="⚡ Mode Time Attack\n(Chrono + Joker)", 
                               bg="#c0392b", fg="white", font=("Arial", 14), width=30, height=3,
                               command=lambda: self.lancer_partie(chrono=True))
        btn_chrono.pack(pady=10)
        
        tk.Button(frame, text="⬅ Retour", command=self.menu_etape_1).pack(pady=20)

    # --- INITIALISATION JEU ---
    def lancer_partie(self, chrono):
        self.mode_chrono = chrono
        self.nb_j = self.nb_joueurs_var.get()
        
        self.scores = [0, 0]
        self.coups_solo = 0
        self.joueur_actuel = 0
        self.paires_trouvees = 0
        self.premier_choix = None
        self.verrouille = False
        self.joker_utilise = False
        self.indices_trouves = [] 
        
        source = EMOJIS_DISPO if self.mode_emoji else COULEURS_DISPO
        nb_paires = self.nb_cartes // 2
        deck = source[:nb_paires] * 2
        random.shuffle(deck)
        self.cartes = deck

        if self.mode_chrono:
            if self.nb_cartes == 6: self.temps_restant = 30
            elif self.nb_cartes == 12: self.temps_restant = 60
            elif self.nb_cartes == 18: self.temps_restant = 75
            elif self.nb_cartes == 24: self.temps_restant = 90
            elif self.nb_cartes == 30: self.temps_restant = 120
            self.timer_running = True
        else:
            self.timer_running = False

        self.creer_interface_jeu()
        
        if self.mode_chrono:
            self.gestion_chrono()

    # --- INTERFACE JEU ---
    def creer_interface_jeu(self):
        self.vider_fenetre()
        
        top_bar = tk.Frame(self.root, pady=10, bg="#34495e")
        top_bar.pack(fill="x")
        
        if self.mode_chrono:
            self.label_chrono = tk.Label(top_bar, text=f"Temps: {int(self.temps_restant)}s", 
                                         font=("Arial", 16, "bold"), bg="#34495e", fg="#e74c3c")
            self.label_chrono.pack(side="left", padx=20)
            
            self.btn_joker = tk.Button(top_bar, text="👀 JOKER", bg="#f1c40f", font=("Arial", 10, "bold"),
                                       command=self.activer_joker)
            self.btn_joker.pack(side="left", padx=20)
        else:
            tk.Label(top_bar, text="Mode Détente ☕", font=("Arial", 14), bg="#34495e", fg="white").pack(side="left", padx=20)

        tk.Button(top_bar, text="Menu", command=self.arret_jeu, bg="#95a5a6", fg="white").pack(side="right", padx=20)

        self.info_frame = tk.Frame(self.root, pady=5)
        self.info_frame.pack(fill="x")
        self.label_info = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.label_info.pack()
        self.maj_affichage_info()

        grid_frame = tk.Frame(self.root, pady=10)
        grid_frame.pack()
        
        if self.nb_cartes == 6: colonnes = 3
        elif self.nb_cartes >= 18: colonnes = 6
        else: colonnes = 4
        
        # --- AJUSTEMENT TAILLE BOUTONS (LE FIX EST ICI) ---
        if self.nb_cartes == 30:
            # Mode Extrême : Boutons petits
            b_width = 4
            b_height = 2
            f_size = 18 if self.mode_emoji else 8
        else:
            # Mode Normal : Boutons confortables
            b_width = 8
            b_height = 4
            f_size = 24 if self.mode_emoji else 10

        self.boutons = []
        for i in range(self.nb_cartes):
            font_style = ("Segoe UI Emoji", f_size) if self.mode_emoji else ("Arial", f_size)
            
            btn = tk.Button(grid_frame, bg=COULEUR_DOS, text="", 
                            width=b_width, height=b_height, font=font_style,
                            command=lambda index=i: self.clic_carte(index))
            btn.grid(row=i//colonnes, column=i%colonnes, padx=3, pady=3)
            self.boutons.append(btn)

    # --- LOGIQUE ---
    def gestion_chrono(self):
        if self.timer_running and self.temps_restant > 0:
            self.temps_restant -= 1
            self.label_chrono.config(text=f"Temps: {int(self.temps_restant)}s")
            if self.temps_restant < 10: self.label_chrono.config(fg="#ff0000")
            self.root.after(1000, self.gestion_chrono)
        elif self.temps_restant <= 0 and self.timer_running:
            self.fin_de_partie_perdu()

    def activer_joker(self):
        if self.joker_utilise or self.verrouille: return
        self.joker_utilise = True
        self.btn_joker.config(state="disabled", bg="#95a5a6", text="Joker épuisé")
        self.verrouille = True
        
        for i, btn in enumerate(self.boutons):
            if i not in self.indices_trouves:
                val = self.cartes[i]
                if self.mode_emoji: btn.config(text=val, bg="white")
                else: btn.config(bg=val)
        
        self.root.after(2000, self.fin_joker)

    def fin_joker(self):
        for i, btn in enumerate(self.boutons):
            if i not in self.indices_trouves:
                if self.mode_emoji: self.boutons[i].config(text="", bg=COULEUR_DOS)
                else: self.boutons[i].config(bg=COULEUR_DOS)
        self.verrouille = False

    def clic_carte(self, index):
        if self.verrouille: return
        if index in self.indices_trouves: return
        
        est_retournee = (self.boutons[index]['text'] != "") if self.mode_emoji else (self.boutons[index]['bg'] != COULEUR_DOS)
        if est_retournee: return

        valeur = self.cartes[index]
        if self.mode_emoji: self.boutons[index].config(text=valeur, bg="white")
        else: self.boutons[index].config(bg=valeur)

        if self.premier_choix is None:
            self.premier_choix = index
        else:
            self.verrouille = True
            if self.nb_j == 1: self.coups_solo += 1
            idx1 = self.premier_choix
            idx2 = index
            
            if self.cartes[idx1] == self.cartes[idx2]:
                self.paires_trouvees += 1
                if self.nb_j == 2: self.scores[self.joueur_actuel] += 1
                
                self.indices_trouves.append(idx1)
                self.indices_trouves.append(idx2)

                self.premier_choix = None
                self.verrouille = False
                self.maj_affichage_info()
                self.verifier_fin()
            else:
                self.root.after(1000, lambda: self.cacher_cartes(idx1, idx2))

    def cacher_cartes(self, idx1, idx2):
        if self.mode_emoji:
            self.boutons[idx1].config(text="", bg=COULEUR_DOS)
            self.boutons[idx2].config(text="", bg=COULEUR_DOS)
        else:
            self.boutons[idx1].config(bg=COULEUR_DOS)
            self.boutons[idx2].config(bg=COULEUR_DOS)
        self.premier_choix = None
        self.verrouille = False
        if self.nb_j == 2: self.joueur_actuel = 1 - self.joueur_actuel
        self.maj_affichage_info()

    def maj_affichage_info(self):
        if self.nb_j == 1:
            txt = f"Coups : {self.coups_solo}"
        else:
            j = "Joueur 1" if self.joueur_actuel == 0 else "Joueur 2"
            self.label_info.config(fg="#e67e22" if self.joueur_actuel == 0 else "#9b59b6")
            txt = f"Tour : {j}  |  J1: {self.scores[0]}  -  J2: {self.scores[1]}"
        self.label_info.config(text=txt)

    def verifier_fin(self):
        if self.paires_trouvees == self.nb_cartes // 2:
            self.timer_running = False
            msg = ""
            if self.nb_j == 1:
                msg = f"🏆 VICTOIRE !\nTerminé en {self.coups_solo} coups."
            else:
                res = "Égalité !"
                if self.scores[0] > self.scores[1]: res = "Joueur 1 gagne !"
                elif self.scores[1] > self.scores[0]: res = "Joueur 2 gagne !"
                msg = f"{res}\nScore: {self.scores[0]} - {self.scores[1]}"
            messagebox.showinfo("Bravo !", msg)
            self.menu_etape_1()

    def fin_de_partie_perdu(self):
        self.verrouille = True
        messagebox.showwarning("Game Over", "⏰ Temps écoulé ! Vous avez perdu.")
        self.menu_etape_1()

    def arret_jeu(self):
        self.timer_running = False
        self.menu_etape_1()
    
    def vider_fenetre(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryGame(root)
    root.mainloop()
     
