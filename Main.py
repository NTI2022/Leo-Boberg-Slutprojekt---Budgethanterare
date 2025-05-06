import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

# Skapa databasen om den inte finns
def init_db():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, description TEXT, amount REAL, category TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
    
    # Lägg till standardkategorier om inga finns
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        default_categories = [("Mat",), ("Transport",), ("Nöje",)]
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", default_categories)
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def add_category(name):
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # kategorin finns redan
    conn.close()

def remove_category(name):
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
    # Uppdatera alla transaktioner som använder denna kategori
    cursor.execute("UPDATE transactions SET category = 'Ej tilldelad' WHERE category = ?", (name,))
    conn.commit()
    conn.close()

def set_budget(amount):
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budget")
    cursor.execute("INSERT INTO budget (amount) VALUES (?)", (amount,))
    conn.commit()
    conn.close()

def get_budget():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM budget LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def add_transaction(description, amount, category):
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (description, amount, category) VALUES (?, ?, ?)", (description, amount, category))
    conn.commit()
    conn.close()
    messagebox.showinfo("Info", "Transaktion sparad!")

def calculate_remaining_budget():
    budget = get_budget()
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions")
    result = cursor.fetchone()
    total_spent = result[0] if result[0] else 0
    conn.close()
    return budget - total_spent

def clear_budget():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budget")
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()
    messagebox.showinfo("Info", "All data har rensats!")

# Visa transaktionshistorik, grupperat per kategori
def show_transaction_history(root):
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("SELECT description, amount, category FROM transactions ORDER BY category")
    transactions = cursor.fetchall()
    conn.close()

    trans_window = tk.Toplevel(root)
    trans_window.title("Transaktionshistorik")
    trans_window.geometry("400x300")

    listbox = tk.Listbox(trans_window, width=60)
    listbox.pack(pady=10, padx=10, fill="both", expand=True)

    if transactions:
        current_category = None
        for desc, amount, category in transactions:
            # Om kategorin ändras, skriv ut kategorin och lägg till mellanrum
            if category != current_category:
                if current_category is not None:
                    listbox.insert(tk.END, "")  # Tom rad för mellanrum mellan kategorier
                listbox.insert(tk.END, f"[{category}]")  # Skriv ut kategorin
                listbox.insert(tk.END, "-" * 50)  # Linje för att separera kategorier
                current_category = category
            # Skriv ut transaktionen under kategorin
            listbox.insert(tk.END, f"{desc} - {amount:.2f} kr")
    else:
        listbox.insert(tk.END, "Inga transaktioner än.")

# GUI med sidomeny och flikar
def main():
    init_db()
    root = tk.Tk()
    root.title("Budgethanterare")
    root.geometry("700x500")

    # skapa sidomeny
    sidebar = tk.Frame(root, width=150, bg='#2f4f4f', height=500, relief="sunken")
    sidebar.pack(side="left", fill="y")

    # Sätt aktiv flik till grön, annars grå
    def set_active_button(button, is_active):
        if is_active:
            button.config(bg="#3cb371")  # grön när aktiv
        else:
            button.config(bg="#2f4f4f")  # standardfärg när inaktiv

    # visa vald flik
    def show_frame(frame_name):
        for widget in content_frame.winfo_children():
            widget.pack_forget()  # ta bort tidigare visad flik

        if frame_name == "budget":
            set_active_button(budget_button, True)
            set_active_button(add_button, False)
            set_active_button(history_button, False)
            set_active_button(categories_button, False)
            show_budget()
        elif frame_name == "add":
            set_active_button(budget_button, False)
            set_active_button(add_button, True)
            set_active_button(history_button, False)
            set_active_button(categories_button, False)
            show_add_transaction()
        elif frame_name == "history":
            set_active_button(budget_button, False)
            set_active_button(add_button, False)
            set_active_button(history_button, True)
            set_active_button(categories_button, False)
            show_transaction_history(root)  # skickar med root här
        elif frame_name == "categories":
            set_active_button(budget_button, False)
            set_active_button(add_button, False)
            set_active_button(history_button, False)
            set_active_button(categories_button, True)
            show_categories()

    # visa budget
    def show_budget():
        tk.Label(content_frame, text="Ange budget:").pack(pady=5)
        budget_entry = tk.Entry(content_frame)
        budget_entry.pack(pady=5)

        def save_budget():
            try:
                set_budget(float(budget_entry.get()))
                messagebox.showinfo("Info", "Budget sparad!")
            except ValueError:
                messagebox.showerror("Fel", "Ange ett giltigt nummer")

        tk.Button(content_frame, text="Spara budget", command=save_budget).pack(pady=5)
        tk.Button(content_frame, text="Visa återstående budget",
                  command=lambda: messagebox.showinfo("Budget", f"Återstående budget: {calculate_remaining_budget():.2f} kr")).pack(pady=5)

    # visa och lägg till transaktioner
    def show_add_transaction():
        tk.Label(content_frame, text="Lägg till transaktion:").pack(pady=10)
        description_entry = tk.Entry(content_frame)
        description_entry.pack(pady=2)

        amount_entry = tk.Entry(content_frame)
        amount_entry.pack(pady=2)

        category_var = tk.StringVar()
        categories = get_categories()
        category_var.set(categories[0])
        category_menu = tk.OptionMenu(content_frame, category_var, *categories)
        category_menu.pack(pady=5)

        def save_transaction():
            try:
                desc = description_entry.get().strip()
                amount = float(amount_entry.get())
                category = category_var.get()
                if not desc or amount <= 0:
                    raise ValueError
                add_transaction(desc, amount, category)
                description_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Fel", "Ange giltig beskrivning och belopp > 0")

        tk.Button(content_frame, text="Lägg till transaktion", command=save_transaction).pack(pady=5)

    # Visa och hantera kategorier
    def show_categories():
        tk.Label(content_frame, text="Lägg till ny kategori:").pack(pady=5)
        new_cat_entry = tk.Entry(content_frame)
        new_cat_entry.pack(pady=2)

        def save_new_category():
            name = new_cat_entry.get().strip()
            if name:
                add_category(name)
                new_cat_entry.delete(0, tk.END)
                messagebox.showinfo("Info", f"Kategorin {name} har lagts till!")

        tk.Button(content_frame, text="Spara ny kategori", command=save_new_category).pack(pady=2)

        tk.Label(content_frame, text="Välj kategori att ta bort:").pack(pady=5)
        remove_cat_var = tk.StringVar()
        categories = get_categories()
        remove_cat_var.set(categories[0])
        remove_cat_menu = tk.OptionMenu(content_frame, remove_cat_var, *categories)
        remove_cat_menu.pack(pady=5)

        def remove_selected_category():
            category_to_remove = remove_cat_var.get()
            remove_category(category_to_remove)
            show_categories()  # uppdatera vy med nya kategorier
            messagebox.showinfo("Info", f"Kategorin {category_to_remove} har tagits bort!")

        tk.Button(content_frame, text="Radera kategori", command=remove_selected_category, fg="white", bg="red").pack(pady=5)

    # Huvudframe för innehållet
    content_frame = tk.Frame(root)
    content_frame.pack(side="right", fill="both", expand=True)

    # menyknappar
    budget_button = tk.Button(sidebar, text="Budget", command=lambda: show_frame("budget"), bg="#2f4f4f", fg="white", width=20)
    budget_button.pack(pady=10)

    add_button = tk.Button(sidebar, text="Lägg till", command=lambda: show_frame("add"), bg="#2f4f4f", fg="white", width=20)
    add_button.pack(pady=10)

    history_button = tk.Button(sidebar, text="Transaktioner", command=lambda: show_frame("history"), bg="#2f4f4f", fg="white", width=20)
    history_button.pack(pady=10)

    categories_button = tk.Button(sidebar, text="Kategorier", command=lambda: show_frame("categories"), bg="#2f4f4f", fg="white", width=20)
    categories_button.pack(pady=10)

    # rensa allt-knapp längst ner
    clear_button = tk.Button(sidebar, text="Rensa allt", command=clear_budget, fg="white", bg="red", width=20)
    clear_button.pack(pady=10, side="bottom")

    # starta med budgetfliken
    show_frame("budget")
    root.mainloop()

if __name__ == "__main__":
    main()
