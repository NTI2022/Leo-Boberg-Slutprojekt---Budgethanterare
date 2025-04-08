import sqlite3
import tkinter as tk
from tkinter import messagebox

# Skapa och anslut till databasen
def init_db():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, description TEXT, amount REAL)''')
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

def add_transaction(description, amount):
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (description, amount) VALUES (?, ?)", (description, amount))
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

def main():
    init_db()
    root = tk.Tk()
    root.title("Budgethanterare")
    root.geometry("600x400")
    
    frame = tk.Frame(root)
    frame.pack(expand=True)

    # Funktion för att visa transaktioner
    def show_transactions():
        conn = sqlite3.connect("budget.db")
        cursor = conn.cursor()
        cursor.execute("SELECT description, amount FROM transactions")
        transactions = cursor.fetchall()
        conn.close()

        trans_window = tk.Toplevel(root)
        trans_window.title("Transaktionshistorik")
        trans_window.geometry("400x300")

        listbox = tk.Listbox(trans_window, width=50)
        listbox.pack(pady=10, padx=10, fill="both", expand=True)

        if transactions:
            for desc, amount in transactions:
                listbox.insert(tk.END, f"{desc} - {amount} kr")
        else:
            listbox.insert(tk.END, "Inga transaktioner än.")

    # Grafiskt 
    tk.Label(frame, text="Ange budget:").pack(pady=5)
    budget_entry = tk.Entry(frame)
    budget_entry.pack(pady=5)

    def save_budget():
        try:
            set_budget(float(budget_entry.get()))
            messagebox.showinfo("Info", "Budget sparad!")
        except ValueError:
            messagebox.showerror("Fel", "Ange ett giltigt nummer")

    tk.Button(frame, text="Spara budget", command=save_budget).pack(pady=5)

    tk.Button(frame, text="Visa återstående budget", command=lambda: messagebox.showinfo("Budget", f"Återstående budget: {calculate_remaining_budget()}")).pack(pady=5)

    #Lägg till transaktion
    tk.Label(frame, text="Lägg till transaktion:").pack(pady=10)
    description_entry = tk.Entry(frame)
    description_entry.pack(pady=2)
    description_entry.insert(0, "")

    amount_entry = tk.Entry(frame)
    amount_entry.pack(pady=2)
    amount_entry.insert(0, "")

    def save_transaction():
        try:
            desc = description_entry.get()
            amount = float(amount_entry.get())
            if amount <= 0:
                raise ValueError
            add_transaction(desc, amount)
        except ValueError:
            messagebox.showerror("Fel", "Ange ett giltigt belopp större än 0")

    tk.Button(frame, text="Lägg till transaktion", command=save_transaction).pack(pady=5)

    #Visa transaktioner knapp
    tk.Button(frame, text="Visa transaktioner", command=show_transactions).pack(pady=5)

    #rensa allt
    tk.Button(frame, text="Rensa all data", command=clear_budget, fg="red").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
