import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="horse_racing"
    )



def admin_or_user():
    #"""عرض قائمة اختيار وضع الإدارة أو المستخدم."""
    exit1 = False
    while not exit1:
        print("\n--- Main Menu ---")
        print("1 : admin")
        print("2 : user")
        print("3 : exit")
        nmb = input("enter the number you want : ").strip()
        if nmb == "1":
            admin()
        elif nmb == "2":
            user()
        elif nmb == "3":
            exit1 = True
        else:
            print("Invalid option. Please try again.")


def admin():
   # """قوائم وإجراءات الادمن — تستدعي وظائف إدارية (stubs هنا).
   # الخيارات: إضافة سباق، حذف مالك، نقل حصان، الموافقة على مدرّب.
    
    exit1 = False
    while not exit1:
        print("\n--- Admin Menu ---")
        print("1 : Add a new race with the results of the race")
        print("2 : Delete an owner and all the related information from the database")
        print("3 : Given the horse ID, move the horse from one stable to another")
        print("4 : Approve a new trainer to join a stable")
        print("5 : exit")
        nmb = input("enter the number you want : ").strip()
        if nmb == "1":
            add_race_with_results()
        elif nmb == "2":
            delete_owner_and_related_data()
        elif nmb == "3":
            transfer_horse_between_stables()
        elif nmb == "4":
            approve_new_trainer()
        elif nmb == "5":
            exit1 = True
        else:
            print("Invalid option. Please try again.")


def user():
    #"""قوائم المستخدم للعرض فقط (reads)."""
    exit1 = False
    while not exit1:
        print("\n--- User Menu ---")
        print("1 : View horses and their trainers by owner's last name")
        print("2 : View trainers who have trained first-place winners")
        print("3 : View total prize winnings for each trainer (sorted by amount)")
        print("4 : View tracks with the number of races and participating horses")
        print("5 : exit")
        nmb = input("enter the number you want : ").strip()
        if nmb == "1":
            show_horses_and_trainers_by_owner_last_name()
        elif nmb == "2":
            show_trainers_by_result()
        elif nmb == "3":
            show_total_prize_winnings_by_trainer()
        elif nmb == "4":
            show_tracks_with_race_counts()
        elif nmb == "5":
            exit1 = True
        else:
            print("Invalid option. Please try again.")



# --- Stubs for functions referenced elsewhere but not yet implemented ---
def add_race_with_results():
    print("[admin] Adding a new race...")

    raceID = input("Enter race ID: ").strip()
    raceName = input("Enter race name: ").strip()
    trackName = input("Enter track name: ").strip()
    raceDate = input("Enter race date (YYYY-MM-DD): ").strip()
    raceTime = input("Enter race time (HH:MM): ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO Race (raceId, raceName, trackName, raceDate, raceTime)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (raceID, raceName, trackName, raceDate, raceTime))
        conn.commit()  # 🟢 مهم جدًا لحفظ التغييرات في قاعدة البيانات
        print("✅ Race added successfully.")
        add_results(raceID)
    except Exception as e:
        print(f"❌ Failed to add race: {e}")
        conn.rollback()  # 🔴 في حال صار خطأ، يرجّع الحالة السابقة
    finally:
        cursor.close()
        conn.close()


def add_results(raceID):
    
    horseID = input("Enter horse ID: ").strip()
    result = input("Enter result (e.g., first, second): ").strip()
    prize = input("Enter prize amount: ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        insert into RaceResults values(%s, %s, %s, %s);
        """
        cursor.execute(query, (raceID, horseID, result, prize))
        conn.commit()  # 🟢 مهم جدًا لحفظ التغييرات في قاعدة البيانات
        print("✅ RaceResults added successfully.")
        agin = input("Do you want to add another result? (y/n): ").strip().lower()
        if agin == 'y':
            add_results(raceID)
    except Exception as e:
        print(f"❌ Failed to add race: {e}")
        conn.rollback()  # 🔴 في حال صار خطأ، يرجّع الحالة السابقة
    finally:
        cursor.close()
        conn.close()
    

def delete_owner_and_related_data():
   # """Stub: حذف مالك وكل البيانات المرتبطة به."""
    owner_id = input("Enter owner ID to delete: ").strip()
    print(f"[stub] delete_owner_and_related_data called for owner_id={owner_id}")
    # تنفيذ الحذف في DB هنا (مع معاملات/تحقق)

    conn = get_connection()
    cursor = conn.cursor()
    try:
    # 🔹 تعطيل الوضع الآمن مؤقتًا
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")

        # 🔹 حذف نتائج السباقات المرتبطة
        cursor.execute("""
            DELETE FROM RaceResults
            WHERE horseId IN (
              SELECT horseId FROM Owns WHERE ownerId = %s
            );
        """, (owner_id,))

        # 🔹 حذف العلاقات من جدول Owns
        cursor.execute("DELETE FROM Owns WHERE ownerId = %s;", (owner_id,))

        # 🔹 حذف الخيول التي لم تعد مملوكة
        cursor.execute("""
            DELETE FROM Horse
            WHERE horseId NOT IN (SELECT horseId FROM Owns);
        """)

        # 🔹 حذف المالك نفسه
        cursor.execute("DELETE FROM Owner WHERE ownerId = %s;", (owner_id,))

        # 🔹 تفعيل الوضع الآمن من جديد
        cursor.execute("SET SQL_SAFE_UPDATES = 1;")

        conn.commit()
        print("✅ Owner and related data deleted successfully.")

    except Exception as e:
        print(f"❌ Failed to delete: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


def transfer_horse_between_stables():
    #"""Stub: نقل حصان من اسطبل إلى آخر حسب horse ID."""
    horse_id = input("Enter horse ID to transfer: ").strip()
    new_stable = input("Enter target stable ID: ").strip()
    print(f"[stub] transfer_horse_between_stables called for horse_id={horse_id}, new_stable={new_stable}")
    # تنفيذ تحديث stableId في جدول Horse
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        UPDATE Horse
        SET stableId = %s
        WHERE horseId = %s;
        """
        cursor.execute(query, (new_stable, horse_id))
        conn.commit()  # 🟢 مهم جدًا لحفظ التغييرات في قاعدة البيانات
        # ✅ التأكد من أن حصان فعلاً تم تحديثه
        if cursor.rowcount > 0:
            print("✅ Horse transferred successfully.")
        else:
            print("⚠️ No horse found with that ID. Nothing was updated.")

    except Exception as e:
        print(f"❌ Failed to transfer horse: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


def approve_new_trainer():
    #"""Stub: الموافقة على مدرّب جديد للانضمام إلى اسطبل."""
    trainer_id = input("Enter trainer ID to approve: ").strip()
    lname = input("Enter trainer last name: ").strip()
    fname = input("Enter trainer first name: ").strip()
    new_stable = input("Enter stable ID to join: ").strip()
    print(f"[stub] approve_new_trainer called for trainer_id={trainer_id}")
    # تحديث حالة الموافقة في DB
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO Trainer (trainerId, lname, fname, stableId)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (trainer_id, lname, fname, new_stable))
        conn.commit()  # 🟢 مهم جدًا لحفظ التغييرات في قاعدة البيانات
        # ✅ التأكد من أن مدرّب فعلاً تم إضافته
        if cursor.rowcount > 0:
            print("✅ Trainer approved and added successfully.")
        else:
            print("⚠️ No changes made. Please check trainer information.")

    except Exception as e:
        print(f"❌ Failed to approve trainer: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


# Stubs for view functions that were referenced but not defined
def show_horses_and_trainers_by_owner_last_name():
    last_name = input("Enter owner's last name: ").strip()
    print(f"[stub] show_horses_and_trainers_by_owner_last_name for '{last_name}'")
    #عرض المدرّبين الذين درّبوا الفائزين بالمركز الأول.
    #هذه دالة حقيقية تستخدم قاعدة بيانات (تحتاج اتصال صالح).
    
    conn = get_connection()

    cursor = conn.cursor()

    query = """
    SELECT 
      H.horseName AS Horse_Name,
      H.age AS Horse_Age,
      T.fname AS Trainer_first_Name,
      T.lname AS Trainer_last_Name
    FROM 
      Horse H
    JOIN 
      Trainer T ON H.stableId = T.stableId
    join
      owns OW ON H.horseId = OW.horseId
    JOIN 
      Owner O ON OW.ownerId = O.ownerId
    WHERE 
      O.lName = %s;  -- تقدر تغير الاسم حسب الإدخال
        """

    cursor.execute(query, (last_name,))
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()


def show_trainers_by_result():
    #"""عرض المدرّبين الذين درّبوا الفائزين بالمركز الأول.
    #هذه دالة حقيقية تستخدم قاعدة بيانات (تحتاج اتصال صالح).
    
    conn = get_connection()

    cursor = conn.cursor()
    result_position = "first"

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
    i = 0
    for row in rows:
        i+=1
        print(i,end=' : ')
        print(row)

    cursor.close()
    conn.close()


def show_total_prize_winnings_by_trainer():
    print("[stub] show_total_prize_winnings_by_trainer called")
    conn = get_connection()

    cursor = conn.cursor()
   
    query = """
    SELECT 
      T.fname AS Trainer_FirstName,
      T.lname AS Trainer_LastName,
      SUM(RR.prize) AS Total_Winnings
    FROM 
      Trainer T
    JOIN 
      Stable S ON T.stableId = S.stableId
    JOIN 
      Horse H ON H.stableId = S.stableId
    JOIN 
      RaceResults RR ON RR.horseId = H.horseId
    GROUP BY 
      T.trainerId, T.fname, T.lname
    ORDER BY 
      Total_Winnings DESC;
    """

    cursor.execute(query,)
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()


def show_tracks_with_race_counts():
    print("[stub] show_tracks_with_race_counts called")
    conn = get_connection()

    cursor = conn.cursor()
   
    query = """
     SELECT 
      T.trackName AS Track_Name,
      COUNT(DISTINCT R.raceId) AS Race_Count,
      COUNT(DISTINCT RR.horseId) AS Total_Horses
    FROM 
      Track T
    JOIN 
      Race R ON T.trackName = R.trackName
    JOIN 
      RaceResults RR ON R.raceId = RR.raceId
    GROUP BY 
      T.trackName;
    """

    cursor.execute(query,)
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()


def main():
    # ملاحظة: يتطلب mysql server وشبكة صحيحة؛ هذا المثال يفحص فقط الاتصال ويعرض القوائم.
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="horse_racing"
        )

        if connection.is_connected():
            print("Connected successfully!\n")
            connection.close()
            admin_or_user()
            print("Exiting program.")
    except Exception as e:
        print(f"Could not connect to database: {e}")


# 🔹 هذا السطر يخلي الكود ما يشتغل إلا إذا الملف هو الأساسي (مو مستورد)
if __name__ == "__main__":
    main()
