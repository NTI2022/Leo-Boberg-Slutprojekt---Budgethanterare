import sqlite3
import tkinter as tk
from tkinter import messagebox

# Skapa och anslut till databasen
def init_db():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, amount REAL)''')
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

def clear_budget():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budget")
    conn.commit()
    conn.close()
    messagebox.showinfo("Info", "Budgeten har rensats!")

def calculate_remaining_budget():
    budget = get_budget()
    return budget

def main():
    init_db()
    root = tk.Tk()
    root.title("Budgethanterare")
    
    root.geometry("600x300")  #storleken på fönstret i pixlar
    
    #Frame för att hålla alla widgets och centrera dem
    frame = tk.Frame(root)
    frame.pack(expand=True)  # Gör så ramen tar upp så mycket utrymme som möjligt
    
    #lägger till widgets i ramen
    tk.Label(frame, text="Ange budget:").pack(pady=10)
    budget_entry = tk.Entry(frame)
    budget_entry.pack(pady=10)
    
    def save_budget():
        set_budget(float(budget_entry.get()))
        messagebox.showinfo("Info", "Budget sparad!")
    
    tk.Button(frame, text="Spara budget", command=save_budget).pack(pady=10)
    tk.Button(frame, text="Visa återstående budget", command=lambda: messagebox.showinfo("Budget", f"Återstående budget: {calculate_remaining_budget()}")).pack(pady=10)
    
    #knapp för att rensa budgeten
    tk.Button(frame, text="Rensa all data", command=clear_budget, fg="red").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
