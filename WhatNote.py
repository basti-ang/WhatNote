import os 
from datetime import datetime
import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, Frame, X, Label, LEFT, RIGHT, Button, TOP
import ctypes
import pywhatkit

#Whatsapp Kontakt
whatsappContact = "YOUR PHONE NUMBER HERE"

#DPI Skalierung
ctypes.windll.shcore.SetProcessDpiAwareness(1)

#Hauptfenster
window = tk.Tk()
window.geometry("700x500+50+50")
window.title("WhatNote")

#Placeholder Management
def on_entry_click(event):
    if note_entry.get("1.0", "end-1c") == placeholder:
        note_entry.delete("1.0", tk.END)
        note_entry.config(fg='black')

def on_entry_leave(event):
    if note_entry.get("1.0", "end-1c") == '':
        note_entry.insert("1.0", placeholder)
        note_entry.config(fg="gray")

placeholder = "Neue Notiz..."

note_entry = tk.Text(window, height=10, width=40, wrap=tk.WORD)
note_entry.pack()
note_entry.insert("1.0", placeholder)
note_entry.config(fg='gray')
note_entry.bind('<FocusIn>', on_entry_click)
note_entry.bind('<FocusOut>', on_entry_leave)

db_selection_label = tk.Label(window, text="Datenbank auswählen:")
db_selection_label.pack()

#Datenbank Management
def load_db_options():
    db_options = [os.path.basename(filename) for filename in os.listdir() if filename.endswith(".db")]
    return db_options

db_options = load_db_options()
selected_db = tk.StringVar()

if db_options:
    selected_db.set(db_options[0])
else:
    selected_db.set("Notizbuch 1.db")
    new_db_name = "Notizbuch 1.db"
    conn = sqlite3.connect(new_db_name)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)")
    conn.commit()
    conn.close()
    db_options.append(new_db_name)

db_dropdown = tk.OptionMenu(window, selected_db, *db_options)
db_dropdown.pack()

button_frame = tk.Frame(window)
button_frame.pack()

#Funktionen/Buttons:

#Datum/Uhrzeit der aktuellen Notiz
def note_date():
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M")
    return date_time
    
#Notiz speichern Btn
def save_note():
    entry = note_entry.get("1.0", "end-1c")
    note = str(entry)

    if not note.strip() or note.strip() == placeholder:
        return

    note_date()
    note_with_date = note_date() + ":\n" + note

    conn = sqlite3.connect(os.path.join(os.getcwd(), selected_db.get()))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)")
    cursor.execute("INSERT INTO notes (content) VALUES (?)", (note_with_date,))
    conn.commit()
    conn.close()

    note_entry.delete("1.0", tk.END)
    note_entry.insert("1.0", placeholder)
    note_entry.config(fg='gray')

save_button = tk.Button(button_frame, text="Speichern", command=save_note)
save_button.pack(side=tk.LEFT)

#Notiz speichern und als Whatsapp Nachricht senden Btn
def sendWhatsapp():
    entry = note_entry.get("1.0", "end-1c")
    note = str(entry)

    if not note.strip() or note.strip() == placeholder:
        return

    # Syntax: Telefonnummer mit Ländercode, Nachricht, Stunde und Minuten
    currentH = datetime.now().strftime("%H")
    currentM = datetime.now().strftime("%M")
    currentS = datetime.now().strftime("%S")
    nachricht = str(note_entry.get("1.0", "end-1c"))

    try:
        pywhatkit.sendwhatmsg_instantly(whatsappContact, nachricht, 15, True, 2)
        print("Nachricht gesendet!")

    except:
        print("Fehler beim Senden aufgetreten!")

    save_note()

saveandsend_button = tk.Button(button_frame, text="Whatsapp", command=sendWhatsapp)
saveandsend_button.pack(side=tk.LEFT)

#Notizen Anzeigen Btn
def view_notes():
    conn = sqlite3.connect(os.path.join(os.getcwd(), selected_db.get()))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()
    conn.close()

    #Exportieren der aktuellen Datenbank als txt Datei
    def export_notes(notes):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])

        if file_path:
            with open(file_path, "w") as file:
                for i, note in enumerate(notes, start=1):
                    note_text = note[1].split(":\n", 1)
                    file.write(f"{i}. {note_text[0]}:\n")
                    if len(note_text) > 1:
                        file.write(note_text[1] + "\n")
                    if i < len(notes):
                        file.write("-" * 40 + "\n")

    view_window = tk.Toplevel(window)
    view_window.title("Notizen")

    view_text = scrolledtext.ScrolledText(view_window, wrap=tk.WORD)
    view_text.pack(fill="both", expand=True)

    view_text.tag_configure("bold", font=("Helvetica", 10, "bold"))

    num_notes = len(notes)

    for i, note in enumerate(notes, start=1):
        note_text = note[1].split(":\n", 1)

        if len(note_text) == 2:
            view_text.insert(tk.END, f"{num_notes - i + 1}. ", "bold")
            view_text.insert(tk.END, note_text[0] + ":\n", "bold")
            view_text.insert(tk.END, note_text[1] + "\n")
        else:
            view_text.insert(tk.END, f"{num_notes - i + 1}. {note[1]}\n")

        if i < num_notes:
            view_text.insert(tk.END, "-" * 40 + "\n")

    export_button = tk.Button(view_window, text="Exportieren", command=lambda: export_notes(notes))
    export_button.pack()

    view_text.pack()

view_button = tk.Button(button_frame, text="Notizen...", command=view_notes)
view_button.pack(side=tk.LEFT)

db_button_frame = tk.Frame(window)
db_button_frame.pack()

#Neues Notizbuch erstellen Btn
def create_new_db():
    new_db_name = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite-Datenbanken", "*.db")])
    if new_db_name:
        conn = sqlite3.connect(new_db_name)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)")
        conn.commit()
        conn.close()
        db_options.append(os.path.basename(new_db_name))
        db_dropdown["menu"].delete(0, "end")
        for option in db_options:
            db_dropdown["menu"].add_command(label=option, command=tk._setit(selected_db, option))

create_db_button = tk.Button(db_button_frame, text="Neues Notizbuch", command=create_new_db)
create_db_button.pack(side=tk.LEFT)

#Notizbuch löschen Btn
def delete_db():
    selected_db_name = selected_db.get()
    confirm_delete = messagebox.askyesno("Notizbuch löschen", f"Sind Sie sicher, dass Sie '{selected_db_name}' löschen möchten?")
    if confirm_delete:
        db_options.remove(selected_db_name)
        db_dropdown["menu"].delete(0, "end")
        for option in db_options:
            db_dropdown["menu"].add_command(label=option, command=tk._setit(selected_db, option))
        os.remove(os.path.join(os.getcwd(), selected_db_name))
        selected_db.set(db_options[0])

delete_db_button = tk.Button(db_button_frame, text="Notizbuch löschen", command=delete_db)
delete_db_button.pack(side=tk.LEFT)

#Programm starten
window.mainloop()
