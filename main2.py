import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk

def show_trainers_by_result():
    result_position = entry_position.get().strip()

    if not result_position:
        messagebox.showwarning("Warning", "Please enter a position (first/second/third)")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="horse_racing"
        )
        cursor = conn.cursor()

        query = """
        SELECT 
          T.fName AS Trainer_FirstName,
          T.lName AS Trainer_LastName,
          H.horseName AS Winning_Horse,
          R.raceName AS Race_Name,
          R.raceDate AS Race_Date,
          R.trackName AS Race_Location
        FROM 
          Trainer T
        JOIN 
          Horse H ON T.stableId = H.stableId
        JOIN 
          RaceResults RR ON H.horseId = RR.horseId
        JOIN 
          Race R ON RR.raceId = R.raceId
        WHERE 
          RR.results = %s;
        """
        cursor.execute(query, (result_position,))
        rows = cursor.fetchall()

        # تنظيف الجدول قبل عرض النتائج الجديدة
        for row in tree.get_children():
            tree.delete(row)

        # عرض النتائج في الجدول
        for row in rows:
            tree.insert("", "end", values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# إنشاء النافذة
root = tk.Tk()
root.title("Horse Racing Database")
root.geometry("800x400")

# إدخال النتيجة
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Enter position (first/second/third):").grid(row=0, column=0, padx=5)
entry_position = tk.Entry(frame)
entry_position.grid(row=0, column=1, padx=5)

tk.Button(frame, text="Show Results", command=show_trainers_by_result).grid(row=0, column=2, padx=5)

# جدول لعرض النتائج
columns = ("Trainer_FirstName", "Trainer_LastName", "Winning_Horse", "Race_Name", "Race_Date", "Race_Location")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(expand=True, fill="both", pady=10)

root.mainloop()
