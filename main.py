import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB = "autosalon.db"

# ================= DATABASE =================
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cars(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        price REAL,
        status TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        client_id INTEGER,
        FOREIGN KEY(car_id) REFERENCES cars(id),
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users(username,password) VALUES(?,?)", ("admin","1234"))
    con.commit()
    con.close()

def get_connection():
    return sqlite3.connect(DB)

# ================= LOGIN WINDOW =================
def login_window():
    login_win = tk.Tk()
    login_win.title("Avtosalon sistemasi - Login")
    login_win.geometry("400x300")
    login_win.configure(bg="#2c3e50")

    tk.Label(login_win, text="Avtosalon sistemasi", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
    tk.Label(login_win, text="Paydalaniwshi ati", bg="#2c3e50", fg="white").pack()
    e_user = tk.Entry(login_win)
    e_user.pack(pady=5)

    tk.Label(login_win, text="Parol", bg="#2c3e50", fg="white").pack()
    e_pass = tk.Entry(login_win, show="*")
    e_pass.pack(pady=5)

    def login():
        username = e_user.get()
        password = e_pass.get()
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
            if cur.fetchone():
                login_win.destroy()
                main_window()
            else:
                messagebox.showerror("Xato", "Login yaki parol qate!")

    tk.Button(login_win, text="Kiriw", width=15, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), command=login).pack(pady=20)

    login_win.mainloop()

# ================= MAIN WINDOW =================
def main_window():
    root = tk.Tk()
    root.title("Avtosalon Basqariw")
    root.geometry("1000x600")
    root.configure(bg="#ecf0f1")

    # ===== HEADER =====
    header = tk.Frame(root, bg="#34495e", height=60)
    header.pack(fill="x")
    tk.Label(header, text="AVTOSALON BASQARIW", font=("Arial", 22, "bold"), fg="white", bg="#34495e").pack(pady=10)

    main = tk.Frame(root, bg="#ecf0f1")
    main.pack(fill="both", expand=True)

    # ===== MENU =====
    menu = tk.Frame(main, width=200, bg="#2c3e50")
    menu.pack(side="left", fill="y")
    menu.pack_propagate(False)

    # ===== CONTENT =====
    content = tk.Frame(main, bg="#ecf0f1")
    content.pack(side="right", fill="both", expand=True)

    def clear():
        for w in content.winfo_children():
            w.destroy()

    # ================= DASHBOARD =================
    def dashboard_page():
        clear()
        tk.Label(content, text="Dashboard", font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=20)

        with get_connection() as con:
            f = con.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
            c = con.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            s = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]

        stats = tk.Frame(content, bg="#ecf0f1")
        stats.pack(pady=20)

        tk.Label(stats, text=f"Avtomobiller sani: {f}", font=("Arial", 14), bg="#ecf0f1").pack(pady=5)
        tk.Label(stats, text=f"Klientler sani: {c}", font=("Arial", 14), bg="#ecf0f1").pack(pady=5)
        tk.Label(stats, text=f"Satilgan mashinalar sani: {s}", font=("Arial", 14), bg="#ecf0f1").pack(pady=5)

    # ================= CARS =================
    def cars_page():
        clear()
        tk.Label(content, text="Avtomobiller", font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=10)

        form = tk.Frame(content, bg="#ecf0f1")
        form.pack(pady=10)

        tk.Label(form, text="Model", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
        e_model = tk.Entry(form)
        e_model.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Bahasi", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5)
        e_price = tk.Entry(form)
        e_price.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Jagdayi", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5)
        e_status = ttk.Combobox(form, values=["Jaqsi","Ortasha","Jaman"], state="readonly")
        e_status.grid(row=2, column=1, padx=5, pady=5)
        e_status.set("Jaqsi")

        table_frame = tk.Frame(content)
        table_frame.pack(fill="both", expand=True, pady=10)

        table = ttk.Treeview(table_frame, columns=("id","m","p","s"), show="headings", height=10)
        table.pack(side="left", fill="both", expand=True)
        for col, txt in zip(("id","m","p","s"), ("ID","Model","Narxi","Holati")):
            table.heading(col, text=txt)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def load():
            table.delete(*table.get_children())
            with get_connection() as con:
                for r in con.execute("SELECT * FROM cars"):
                    table.insert("", "end", values=r)

        def add():
            if not e_model.get() or not e_price.get() or not e_status.get():
                messagebox.showwarning("Xato", "Hamme maydanlardi toldirin!")
                return
            with get_connection() as con:
                con.execute("INSERT INTO cars(model,price,status) VALUES(?,?,?)",
                            (e_model.get(), e_price.get(), e_status.get()))
            e_model.delete(0, tk.END)
            e_price.delete(0, tk.END)
            e_status.set("Yaxshi")
            load()

        def delete():
            sel = table.selection()
            if not sel: return
            if messagebox.askyesno("Ogohlantirish","Oshiriesiz be?"):
                cid = table.item(sel[0])["values"][0]
                with get_connection() as con:
                    con.execute("DELETE FROM cars WHERE id=?", (cid,))
                load()

        btn = tk.Frame(content, bg="#ecf0f1")
        btn.pack(pady=5)
        tk.Button(btn, text="Qosiw", command=add, bg="#27ae60", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn, text="Oshiriw", command=delete, bg="#c0392b", fg="white", width=12).pack(side="left", padx=5)

        load()

    # ================= CLIENTS =================
    def clients_page():
        clear()
        tk.Label(content, text="Klientler", font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=10)

        form = tk.Frame(content, bg="#ecf0f1")
        form.pack(pady=10)

        tk.Label(form, text="Ati", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
        e_name = tk.Entry(form)
        e_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Email", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5)
        e_email = tk.Entry(form)
        e_email.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Telefon", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5)
        e_phone = tk.Entry(form)
        e_phone.grid(row=2, column=1, padx=5, pady=5)

        table_frame = tk.Frame(content)
        table_frame.pack(fill="both", expand=True, pady=10)

        table = ttk.Treeview(table_frame, columns=("i","n","e","p"), show="headings", height=10)
        table.pack(side="left", fill="both", expand=True)
        for c, txt in zip(("i","n","e","p"), ("ID","Ism","Email","Telefon")):
            table.heading(c, text=txt)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def load():
            table.delete(*table.get_children())
            with get_connection() as con:
                for r in con.execute("SELECT * FROM clients"):
                    table.insert("", "end", values=r)

        def add():
            if not e_name.get() or not e_email.get() or not e_phone.get():
                messagebox.showwarning("Xato", "Hamme maydanlardi toldirin!")
                return
            with get_connection() as con:
                con.execute("INSERT INTO clients(name,email,phone) VALUES(?,?,?)",
                            (e_name.get(), e_email.get(), e_phone.get()))
            e_name.delete(0, tk.END)
            e_email.delete(0, tk.END)
            e_phone.delete(0, tk.END)
            load()

        def delete():
            sel = table.selection()
            if not sel: return
            if messagebox.askyesno("Ogohlantirish","Oshiresiz be?"):
                cid = table.item(sel[0])["values"][0]
                with get_connection() as con:
                    con.execute("DELETE FROM clients WHERE id=?", (cid,))
                load()

        btn = tk.Frame(content, bg="#ecf0f1")
        btn.pack(pady=5)
        tk.Button(btn, text="Qosiw", command=add, bg="#27ae60", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn, text="Oshiriw", command=delete, bg="#c0392b", fg="white", width=12).pack(side="left", padx=5)

        load()

    # ================= SALES =================
    def sales_page():
        clear()
        tk.Label(content, text="Mashina aliw", font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=10)
        tk.Label(content, text="Avtomobil ID", bg="#ecf0f1").pack()
        e_car = tk.Entry(content)
        e_car.pack(pady=5)
        tk.Label(content, text="Klient ID", bg="#ecf0f1").pack()
        e_client = tk.Entry(content)
        e_client.pack(pady=5)

        def add():
            if not e_car.get() or not e_client.get():
                messagebox.showwarning("Xato","Hamme maydanlardi toldirin!")
                return
            with get_connection() as con:
                con.execute("INSERT INTO sales(car_id,client_id) VALUES(?,?)",
                            (e_car.get(), e_client.get()))
            e_car.delete(0, tk.END)
            e_client.delete(0, tk.END)
            messagebox.showinfo("OK","Sawda qosildi")

        tk.Button(content, text="Qosiw", command=add, bg="#2980b9", fg="white", width=15).pack(pady=10)

    # ===== MENU BUTTONS =====
    btn_params = {"width":20, "font":("Arial",12,"bold"), "bg":"#34495e", "fg":"white"}
    tk.Button(menu, text="Dashboard", command=dashboard_page, **btn_params).pack(pady=5)
    tk.Button(menu, text="Avtomobiller", command=cars_page, **btn_params).pack(pady=5)
    tk.Button(menu, text="Klientler", command=clients_page, **btn_params).pack(pady=5)
    tk.Button(menu, text="Mashina aliw", command=sales_page, **btn_params).pack(pady=5)

    dashboard_page()
    root.mainloop()

# ================= RUN =================
if __name__ == "__main__":
    init_db()
    login_window()
