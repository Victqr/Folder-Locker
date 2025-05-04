import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os, json
import hashlib
import base64
import time
from cryptography.fernet import Fernet

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_WIDTH = 900
APP_HEIGHT = 600
USERS_FILE = "users.json"

def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()

def generate_key(password: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            data = json.load(f)
            return {k.lower(): v for k, v in data.items()}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_config_file(username):
    return f"config_{username.lower()}.json"

class FolderLockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.title("🔒 Folder Locker")
        if os.path.exists("appicon.ico"):
            self.iconbitmap("appicon.ico")
        self.resizable(False, False)
        self.failed_attempts = 0
        self.user = None
        self.password = None
        self.folder_list = []

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.fade_in()
        self.show_login()

    def on_close(self):
        if self.folder_list:
            self.lock_all() 
        self.destroy()  

    def fade_in(self):
        self.attributes("-alpha", 0.0)
        for i in range(20):
            self.attributes("-alpha", i / 20)
            self.update()
            time.sleep(0.01)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()

        frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#34495e", width=380, height=360)  
        frame.place(relx=0.5, rely=0.5, anchor="center")  

        ctk.CTkLabel(frame, text="Login", font=("Arial", 24, "bold"), text_color="#ecf0f1").pack(pady=10)

        self.login_username = ctk.CTkEntry(frame, placeholder_text="Gebruikersnaam", width=320, height=35, corner_radius=10) 
        self.login_username.pack(pady=8)

        self.login_password = ctk.CTkEntry(frame, show="*", placeholder_text="Wachtwoord", width=320, height=35, corner_radius=10)  
        self.login_password.pack(pady=8)

        ctk.CTkButton(frame, text="Login", width=320, height=45, command=self.login, fg_color="#2980b9", hover_color="#3498db", corner_radius=15).pack(pady=12)

        ctk.CTkButton(frame, text="Nog geen account? Registreer", width=320, height=45, command=self.show_register, fg_color="#27ae60", hover_color="#2ecc71", corner_radius=15).pack(pady=10)

        ctk.CTkLabel(frame, text="Of gebruik een bestaand account", text_color="#bdc3c7", font=("Arial", 12)).pack(pady=8)


    def show_register(self):
        self.clear()
        frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#34495e")
        frame.pack(pady=40, padx=40)

        ctk.CTkLabel(frame, text="Account aanmaken", font=("Arial", 20), text_color="#ecf0f1").pack(pady=10)
        self.reg_username = ctk.CTkEntry(frame, placeholder_text="Gebruikersnaam", width=300)
        self.reg_username.pack(pady=5)
        self.reg_password = ctk.CTkEntry(frame, show="*", placeholder_text="Wachtwoord", width=300)
        self.reg_password.pack(pady=5)
        self.theme_dropdown = ctk.CTkComboBox(frame, values=["dark", "light", "system"], width=300)
        self.theme_dropdown.set("dark")
        self.theme_dropdown.pack(pady=5)

        self.photo_path = None
        def choose_photo():
            path = filedialog.askopenfilename(filetypes=[("Afbeeldingen", "*.jpg *.png")])
            if path:
                self.photo_path = path
                ctk.CTkLabel(frame, text="Foto geselecteerd ✅", text_color="#ecf0f1").pack()

        ctk.CTkButton(frame, text="Optionele profielfoto kiezen", width=200, command=choose_photo, fg_color="#8e44ad", hover_color="#9b59b6").pack(pady=5)
        ctk.CTkButton(frame, text="Account registreren", width=200, height=40, command=self.register, fg_color="#2980b9", hover_color="#3498db").pack(pady=10)
        ctk.CTkButton(frame, text="← Terug", width=200, height=40, command=self.show_login, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)

    def register(self):
        username = self.reg_username.get().lower()
        password = self.reg_password.get()
        theme = self.theme_dropdown.get()
        users = load_users()
        if username in users:
            messagebox.showerror("Fout", "Gebruikersnaam bestaat al.")
            return
        users[username] = {
            "password": hash_password(password),
            "photo": self.photo_path,
            "theme": theme
        }
        save_users(users)
        messagebox.showinfo("Succes", "Account aangemaakt!")
        self.show_login()

    def login(self):
        username = self.login_username.get().lower()
        password = self.login_password.get()
        users = load_users()
        if username in users and users[username]["password"] == hash_password(password):
            self.user = users[username]
            self.user["username"] = username
            self.password = password
            ctk.set_appearance_mode(self.user.get("theme", "dark"))
            self.load_main()
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.destroy()
            else:
                messagebox.showerror("Fout", f"Onjuiste login ({self.failed_attempts}/3)")

    def load_main(self):
        self.clear()
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=20)

        topbar = ctk.CTkFrame(self.main_frame)
        topbar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(topbar, text=f"Ingelogd als: {self.user['username']}", font=("Arial", 14), text_color="#ecf0f1").pack(side="left", padx=10)

        ctk.CTkButton(topbar, text="Profiel", command=self.show_profile, fg_color="#2ecc71", hover_color="#27ae60").pack(side="right", padx=5)
        ctk.CTkButton(topbar, text="Logout", command=self.logout, fg_color="#e74c3c", hover_color="#c0392b").pack(side="right", padx=5)

        self.folder_box = ctk.CTkTextbox(self.main_frame, width=600, height=150, state="disabled", corner_radius=10)
        self.folder_box.pack(pady=(5, 15))

        self.unlock_dropdown = ctk.CTkComboBox(self.main_frame, values=[], width=400)
        self.unlock_dropdown.set("Selecteer folder om te unlocken")
        self.unlock_dropdown.pack(pady=5)

        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=15)
        ctk.CTkButton(button_frame, text="Folder toevoegen", command=self.add_folder).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Folder verwijderen", command=self.remove_folder).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Unlock geselecteerde", command=self.unlock_selected).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Unlock alles", command=self.unlock_all).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Lock alles", command=self.lock_all).grid(row=2, column=0, columnspan=2, pady=(10, 5))

        self.refresh_folder_display()

    def show_profile(self):
        self.clear()
        frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#34495e")
        frame.pack(pady=50, padx=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Profielinstellingen", font=("Arial", 20), text_color="#ecf0f1").pack(pady=10)

        if self.user.get("photo") and os.path.exists(self.user["photo"]):
            img = Image.open(self.user["photo"]).resize((100, 100))
            img = ImageOps.fit(img, (100, 100), centering=(0.5, 0.5))
            photo = ImageTk.PhotoImage(img)
            label = ctk.CTkLabel(frame, image=photo, text="")
            label.image = photo
            label.pack(pady=10)

        name_entry = ctk.CTkEntry(frame, placeholder_text="Nieuwe gebruikersnaam (optioneel)", width=300)
        name_entry.pack(pady=10)
        
        pass_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Nieuw wachtwoord (optioneel)", width=300)
        pass_entry.pack(pady=10)
        
        theme_box = ctk.CTkComboBox(frame, values=["dark", "light", "system"], width=300)
        theme_box.set(self.user.get("theme", "dark"))
        theme_box.pack(pady=10)

        def choose_photo():
            path = filedialog.askopenfilename(filetypes=[("Afbeeldingen", "*.jpg *.png")])
            if path:
                self.user["photo"] = path
                users = load_users()
                users[self.user["username"]]["photo"] = path
                save_users(users)
                messagebox.showinfo("Succes", "Profielfoto gewijzigd!")

        ctk.CTkButton(frame, text="Wijzig profielfoto", command=choose_photo, width=200, fg_color="#8e44ad", hover_color="#9b59b6").pack(pady=10)

        def apply_changes():
            new_name = name_entry.get().strip().lower()
            new_pass = pass_entry.get().strip()
            new_theme = theme_box.get()
            users = load_users()

            if new_name and new_name != self.user["username"]:
                if new_name in users:
                    messagebox.showerror("Fout", "Gebruikersnaam bestaat al.")
                    return
                users[new_name] = users.pop(self.user["username"])
                self.user["username"] = new_name
                messagebox.showinfo("Succes", "Naam gewijzigd. Herstart vereist.")
                save_users(users)
                self.destroy()
                return

            if new_pass:
                users[self.user["username"]]["password"] = hash_password(new_pass)
                self.password = new_pass

            users[self.user["username"]]["theme"] = new_theme
            save_users(users)
            messagebox.showinfo("Profiel", "Wijzigingen opgeslagen!")

        ctk.CTkButton(frame, text="Wijzig gegevens", command=apply_changes, width=200, fg_color="#2980b9", hover_color="#3498db").pack(pady=10)
        ctk.CTkButton(frame, text="← Terug naar home", command=self.load_main, width=200, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)


    def logout(self):
        self.user = None
        self.password = None
        self.folder_list = []
        self.show_login()

    def config_file(self):
        return get_config_file(self.user["username"])

    def refresh_folder_display(self):
        self.folder_box.configure(state="normal")
        self.folder_box.delete("0.0", "end")

        if os.path.exists(self.config_file()):
            with open(self.config_file()) as f:
                data = json.load(f)
                self.folder_list = data.get("folders", [])
                for folder in self.folder_list:
                    self.folder_box.insert("end", folder + "\n")

        self.folder_box.configure(state="disabled")
        self.unlock_dropdown.configure(values=self.folder_list)

    def save_config(self):
        with open(self.config_file(), "w") as f:
            json.dump({
                "hash": hashlib.sha256(self.password.encode()).hexdigest(),
                "folders": self.folder_list
            }, f)

    def add_folder(self):
        path = filedialog.askdirectory()
        if path and path not in self.folder_list:
            self.folder_list.append(path)
            self.save_config()
            self.refresh_folder_display()

    def remove_folder(self):
        path = filedialog.askdirectory(title="Folder selecteren om te verwijderen")
        if path in self.folder_list:
            locked_files = [f for f in os.listdir(path) if f.endswith(".locked")]
            if locked_files:
                keuze = messagebox.askyesno("Blokkering", "Deze folder bevat gelockte bestanden. Wil je ze nu unlocken en daarna verwijderen?")
                if keuze:
                    self.unlock_folder(path)
                    self.folder_list.remove(path)
                    self.save_config()
                    self.refresh_folder_display()
                    messagebox.showinfo("Verwijderd", "Folder werd ge-unlocked en verwijderd.")
                return
            self.folder_list.remove(path)
            self.save_config()
            self.refresh_folder_display()
            messagebox.showinfo("Verwijderd", "Folder succesvol verwijderd.")
        else:
            messagebox.showerror("Niet gevonden", "Folder zit niet in je lijst.")

    def unlock_selected(self):
        path = self.unlock_dropdown.get()
        if path and os.path.exists(path):
            self.unlock_folder(path)

    def unlock_folder(self, path):
        key = generate_key(self.password)
        f = Fernet(key)
        for file in os.listdir(path):
            if file.endswith(".locked"):
                with open(os.path.join(path, file), "rb") as locked:
                    data = locked.read()
                try:
                    decrypted = f.decrypt(data)
                    with open(os.path.join(path, file[:-7]), "wb") as original:
                        original.write(decrypted)
                    os.remove(os.path.join(path, file))
                except:
                    messagebox.showerror("Fout", "Ongeldig wachtwoord.")
        messagebox.showinfo("Unlock", "Folder unlockt.")

    def unlock_all(self):
        for folder in self.folder_list:
            self.unlock_folder(folder)

    def lock_all(self):
        key = generate_key(self.password)
        f = Fernet(key)
        for folder in self.folder_list:
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                if os.path.isfile(full_path) and not file.endswith(".locked"):
                    with open(full_path, "rb") as original:
                        data = original.read()
                    encrypted = f.encrypt(data)
                    with open(full_path + ".locked", "wb") as locked:
                        locked.write(encrypted)
                    os.remove(full_path)
        messagebox.showinfo("Gelockt", "Alle bestanden zijn gelockt.")

if __name__ == "__main__":
    app = FolderLockerApp()
    app.mainloop()
