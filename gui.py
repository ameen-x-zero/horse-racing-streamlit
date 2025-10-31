import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="horse_racing"
    )


def run_query_and_populate(tree, query, params=()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # clear existing
        for item in tree.get_children():
            tree.delete(item)

        for r in rows:
            tree.insert('', 'end', values=r)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def add_race_with_results_gui(parent):
    # dialog to enter race details
    race_id = simpledialog.askstring("Race ID", "Enter race ID:", parent=parent)
    if not race_id:
        return
    race_name = simpledialog.askstring("Race name", "Enter race name:", parent=parent) or ''
    track_name = simpledialog.askstring("Track name", "Enter track name:", parent=parent) or ''
    race_date = simpledialog.askstring("Race date", "Enter race date (YYYY-MM-DD):", parent=parent) or ''
    race_time = simpledialog.askstring("Race time", "Enter race time (HH:MM):", parent=parent) or ''

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Race (raceId, raceName, trackName, raceDate, raceTime)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (race_id, race_name, track_name, race_date, race_time)
        )
        conn.commit()
        # add results loop
        while True:
            horse_id = simpledialog.askstring("Horse ID", "Enter horse ID (leave blank to finish):", parent=parent)
            if not horse_id:
                break
            result = simpledialog.askstring("Result", "Enter result (e.g., first):", parent=parent) or ''
            prize = simpledialog.askstring("Prize", "Enter prize amount:", parent=parent) or '0'
            cursor.execute("INSERT INTO RaceResults (raceId, horseId, results, prize) VALUES (%s,%s,%s,%s);",
                           (race_id, horse_id, result, prize))
            conn.commit()

        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Race and results added successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_owner_and_related_data_gui(parent):
    owner_id = simpledialog.askstring("Owner ID", "Enter owner ID to delete:", parent=parent)
    if not owner_id:
        return
    if not messagebox.askyesno("Confirm", f"Delete owner {owner_id} and all related data?"):
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        cursor.execute("""
            DELETE FROM RaceResults
            WHERE horseId IN (
              SELECT horseId FROM Owns WHERE ownerId = %s
            );
        """, (owner_id,))
        cursor.execute("DELETE FROM Owns WHERE ownerId = %s;", (owner_id,))
        cursor.execute("""
            DELETE FROM Horse
            WHERE horseId NOT IN (SELECT horseId FROM Owns);
        """)
        cursor.execute("DELETE FROM Owner WHERE ownerId = %s;", (owner_id,))
        cursor.execute("SET SQL_SAFE_UPDATES = 1;")
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Owner and related data deleted successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def transfer_horse_between_stables_gui(parent):
    horse_id = simpledialog.askstring("Horse ID", "Enter horse ID to transfer:", parent=parent)
    if not horse_id:
        return
    new_stable = simpledialog.askstring("Stable ID", "Enter target stable ID:", parent=parent)
    if not new_stable:
        return
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Horse SET stableId = %s WHERE horseId = %s;", (new_stable, horse_id))
        conn.commit()
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Horse transferred successfully.")
        else:
            messagebox.showwarning("Not found", "No horse found with that ID.")
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def approve_new_trainer_gui(parent):
    trainer_id = simpledialog.askstring("Trainer ID", "Enter trainer ID:", parent=parent)
    if not trainer_id:
        return
    fname = simpledialog.askstring("First name", "Enter first name:", parent=parent) or ''
    lname = simpledialog.askstring("Last name", "Enter last name:", parent=parent) or ''
    stable_id = simpledialog.askstring("Stable ID", "Enter stable ID to join:", parent=parent) or None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Trainer (trainerId, fname, lname, stableId) VALUES (%s,%s,%s,%s);",
                       (trainer_id, fname, lname, stable_id))
        conn.commit()
        messagebox.showinfo("Success", "Trainer approved and added successfully.")
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def build_gui():
    root = tk.Tk()
    root.title("Horse Racing Manager")
    root.geometry('1000x600')

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Admin tab
    admin_frame = ttk.Frame(notebook)
    notebook.add(admin_frame, text='Admin')

    ttk.Label(admin_frame, text='Admin actions').pack(pady=10)
    btn_frame = ttk.Frame(admin_frame)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text='Add race with results', command=lambda: add_race_with_results_gui(root)).grid(row=0, column=0, padx=8, pady=6)
    ttk.Button(btn_frame, text='Delete owner and related data', command=lambda: delete_owner_and_related_data_gui(root)).grid(row=0, column=1, padx=8, pady=6)
    ttk.Button(btn_frame, text='Transfer horse between stables', command=lambda: transfer_horse_between_stables_gui(root)).grid(row=0, column=2, padx=8, pady=6)
    ttk.Button(btn_frame, text='Approve new trainer', command=lambda: approve_new_trainer_gui(root)).grid(row=0, column=3, padx=8, pady=6)

    # User tab with vertical scrolling and centered contents
    user_frame = ttk.Frame(notebook)
    notebook.add(user_frame, text='User')

    # Create canvas + scrollbar to make the user tab scrollable
    user_canvas = tk.Canvas(user_frame)
    vsb = ttk.Scrollbar(user_frame, orient='vertical', command=user_canvas.yview)
    user_canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    user_canvas.pack(side='left', fill='both', expand=True)

    scrollable_user = ttk.Frame(user_canvas)
    user_canvas.create_window((0, 0), window=scrollable_user, anchor='nw')

    def _on_frame_config(event):
        user_canvas.configure(scrollregion=user_canvas.bbox('all'))

    scrollable_user.bind('<Configure>', _on_frame_config)

    # Bind mousewheel for Windows (and others)
    def _on_mousewheel(event):
        # event.delta is multiples of 120 on Windows; divide to get reasonable scroll
        user_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    user_canvas.bind_all('<MouseWheel>', _on_mousewheel)

    # Helper to center a LabelFrame and its inner content
    def make_centered_section(parent, title):
        container = ttk.Frame(parent)
        container.pack(fill='x', pady=6)
        lf = ttk.LabelFrame(container, text=title)
        lf.pack(anchor='center', padx=10)
        return lf

    # Section: horses by owner last name
    frame1 = make_centered_section(scrollable_user, "Horses by Owner's Last Name")
    inner1 = ttk.Frame(frame1)
    inner1.pack(padx=10, pady=6)
    ttk.Label(inner1, text="Owner last name:").grid(row=0, column=0, padx=6, pady=6)
    entry_owner_last = ttk.Entry(inner1)
    entry_owner_last.grid(row=0, column=1, padx=6, pady=6)
    ttk.Button(inner1, text='Show', command=lambda: on_horses_by_owner()).grid(row=0, column=2, padx=6)
    tree1 = ttk.Treeview(frame1, columns=("Horse","Age","TrainerFirst","TrainerLast"), show='headings', height=8)
    for c in ("Horse","Age","TrainerFirst","TrainerLast"):
        tree1.heading(c, text=c)
        tree1.column(c, width=150, anchor='center')
    tree1.pack(padx=6, pady=6, fill='x')

    # Section: trainers by result
    frame2 = make_centered_section(scrollable_user, "Trainers by Result")
    inner2 = ttk.Frame(frame2)
    inner2.pack(padx=10, pady=6)
    ttk.Label(inner2, text="Result (first/second/...):").grid(row=0, column=0, padx=6)
    entry_position = ttk.Entry(inner2)
    entry_position.grid(row=0, column=1, padx=6)
    ttk.Button(inner2, text='Show', command=lambda: on_trainers_by_result()).grid(row=0, column=2, padx=6)
    tree2 = ttk.Treeview(frame2, columns=("TrainerFirst","TrainerLast","Horse","Race","Date","Location"), show='headings', height=8)
    for c in ("TrainerFirst","TrainerLast","Horse","Race","Date","Location"):
        tree2.heading(c, text=c)
        tree2.column(c, width=120, anchor='center')
    tree2.pack(padx=6, pady=6, fill='x')

    # Section: total prize winnings by trainer
    frame3 = make_centered_section(scrollable_user, "Total prize winnings by trainer")
    ttk.Button(frame3, text='Show', command=lambda: on_total_winnings()).pack(padx=6, pady=6)
    tree3 = ttk.Treeview(frame3, columns=("TrainerFirst","TrainerLast","Total"), show='headings', height=8)
    for c in ("TrainerFirst","TrainerLast","Total"):
        tree3.heading(c, text=c)
        tree3.column(c, width=200, anchor='center')
    tree3.pack(padx=6, pady=6, fill='x')

    # Section: tracks with race counts
    frame4 = make_centered_section(scrollable_user, "Tracks with race counts")
    ttk.Button(frame4, text='Show', command=lambda: on_tracks_counts()).pack(padx=6, pady=6)
    tree4 = ttk.Treeview(frame4, columns=("Track","RaceCount","TotalHorses"), show='headings', height=8)
    for c in ("Track","RaceCount","TotalHorses"):
        tree4.heading(c, text=c)
        tree4.column(c, width=200, anchor='center')
    tree4.pack(padx=6, pady=6, fill='x')

    


    # --- callback implementations for user tab (use outer-scope widgets) ---
    def on_horses_by_owner():
        last = entry_owner_last.get().strip()
        if not last:
            messagebox.showwarning("Warning", "Enter owner's last name")
            return
        q = """
        SELECT H.horseName, H.age, T.fname, T.lname
        FROM Horse H
        JOIN Trainer T ON H.stableId = T.stableId
        JOIN Owns OW ON H.horseId = OW.horseId
        JOIN Owner O ON OW.ownerId = O.ownerId
        WHERE O.lName = %s;
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(q, (last,))
            rows = cur.fetchall()
            for it in tree1.get_children():
                tree1.delete(it)
            for r in rows:
                tree1.insert('', 'end', values=r)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_trainers_by_result():
        pos = entry_position.get().strip()
        if not pos:
            #messagebox.showwarning("Warning", "Enter a position")
            #return
            pos = "first"
        q = """
        SELECT T.fName, T.lName, H.horseName, R.raceName, R.raceDate, R.trackName
        FROM Trainer T
        JOIN Horse H ON T.stableId = H.stableId
        JOIN RaceResults RR ON H.horseId = RR.horseId
        JOIN Race R ON RR.raceId = R.raceId
        WHERE RR.results = %s;
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(q, (pos,))
            rows = cur.fetchall()
            for it in tree2.get_children():
                tree2.delete(it)
            for r in rows:
                tree2.insert('', 'end', values=r)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_total_winnings():
        q = """
        SELECT T.fname, T.lname, SUM(RR.prize) AS Total_Winnings
        FROM Trainer T
        JOIN Stable S ON T.stableId = S.stableId
        JOIN Horse H ON H.stableId = S.stableId
        JOIN RaceResults RR ON RR.horseId = H.horseId
        GROUP BY T.trainerId, T.fname, T.lname
        ORDER BY Total_Winnings DESC;
        """
        run_query_and_populate(tree3, q)

    def on_tracks_counts():
        q = """
         SELECT T.trackName, COUNT(DISTINCT R.raceId) AS Race_Count, COUNT(DISTINCT RR.horseId) AS Total_Horses
        FROM Track T
        JOIN Race R ON T.trackName = R.trackName
        JOIN RaceResults RR ON R.raceId = RR.raceId
        GROUP BY T.trackName;
        """
        run_query_and_populate(tree4, q)

    root.mainloop()


if __name__ == '__main__':
    build_gui()
