import streamlit as st
import mysql.connector
import pandas as pd


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="horse_racing"
    )


def run_query(query, params=()):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        cur.close()
        return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def execute_non_query(query, params=()):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        st.error(f"DB error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def admin_add_race():
    st.subheader("Add a new race with results")
    with st.form("add_race"):
        race_id = st.text_input("Race ID")
        race_name = st.text_input("Race name")
        track_name = st.text_input("Track name")
        race_date = st.text_input("Race date (YYYY-MM-DD)")
        race_time = st.text_input("Race time (HH:MM)")
        st.markdown("---")
        st.write("Enter race results: one per line as: horseId,result,prize")
        results_text = st.text_area("Results (one per line)")
        submitted = st.form_submit_button("Add Race")
        if submitted:
            if not race_id:
                st.warning("Race ID is required")
            else:
                q = "INSERT INTO Race (raceId, raceName, trackName, raceDate, raceTime) VALUES (%s,%s,%s,%s,%s);"
                ok = execute_non_query(q, (race_id, race_name, track_name, race_date, race_time))
                if ok:
                    # insert results
                    lines = [l.strip() for l in results_text.splitlines() if l.strip()]
                    for ln in lines:
                        parts = [p.strip() for p in ln.split(',')]
                        if len(parts) >= 3:
                            horse_id, result, prize = parts[0], parts[1], parts[2]
                            execute_non_query("INSERT INTO RaceResults (raceId, horseId, results, prize) VALUES (%s,%s,%s,%s);",
                                              (race_id, horse_id, result, prize))
                    st.success("Race and results added.")


def admin_delete_owner():
    st.subheader("Delete owner and related data")
    owner_id = st.text_input("Owner ID to delete")
    if st.button("Delete Owner"):
        if not owner_id:
            st.warning("Enter owner ID")
        else:
            if st.confirmation if False else True:
                # perform deletion sequence
                conn = None
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("SET SQL_SAFE_UPDATES = 0;")
                except Exception:
                    pass
                q1 = "DELETE FROM RaceResults WHERE horseId IN (SELECT horseId FROM Owns WHERE ownerId = %s);"
                q2 = "DELETE FROM Owns WHERE ownerId = %s;"
                q3 = "DELETE FROM Horse WHERE horseId NOT IN (SELECT horseId FROM Owns);"
                q4 = "DELETE FROM Owner WHERE ownerId = %s;"
                execute_non_query(q1, (owner_id,))
                execute_non_query(q2, (owner_id,))
                execute_non_query(q3)
                execute_non_query(q4, (owner_id,))
                st.success("Owner and related data deleted (if existed).")


def admin_transfer_horse():
    st.subheader("Transfer horse between stables")
    horse_id = st.text_input("Horse ID")
    new_stable = st.text_input("New stable ID")
    if st.button("Transfer Horse"):
        if not horse_id or not new_stable:
            st.warning("Provide both horse ID and target stable ID")
        else:
            ok = execute_non_query("UPDATE Horse SET stableId = %s WHERE horseId = %s;", (new_stable, horse_id))
            if ok:
                st.success("Transfer attempted (check DB for results).")


def admin_approve_trainer():
    st.subheader("Approve new trainer")
    trainer_id = st.text_input("Trainer ID")
    fname = st.text_input("First name")
    lname = st.text_input("Last name")
    stable_id = st.text_input("Stable ID")
    if st.button("Approve Trainer"):
        if not trainer_id:
            st.warning("Trainer ID required")
        else:
            ok = execute_non_query("INSERT INTO Trainer (trainerId, fname, lname, stableId) VALUES (%s,%s,%s,%s);",
                                   (trainer_id, fname, lname, stable_id))
            if ok:
                st.success("Trainer approved/added.")


def user_view_horses_by_owner():
    st.subheader("Horses and trainers by owner's last name")
    last = st.text_input("Owner last name")
    if st.button("Show Horses"):
        if not last:
            st.warning("Enter owner's last name")
        else:
            q = """
            SELECT H.horseName AS Horse_Name, H.age AS Horse_Age, T.fname AS Trainer_First, T.lname AS Trainer_Last
            FROM Horse H
            JOIN Trainer T ON H.stableId = T.stableId
            JOIN Owns OW ON H.horseId = OW.horseId
            JOIN Owner O ON OW.ownerId = O.ownerId
            WHERE O.lName = %s;
            """
            df = run_query(q, (last,))
            st.dataframe(df)


def user_view_trainers_by_result():
    st.subheader("Trainers who trained first-place winners (or by result)")
    pos = st.text_input("Result (default=first)", value="first")
    if st.button("Show Trainers"):
        q = """
        SELECT T.fName AS Trainer_First, T.lName AS Trainer_Last, H.horseName AS Winning_Horse, R.raceName AS Race_Name, R.raceDate AS Race_Date, R.trackName AS Race_Location
        FROM Trainer T
        JOIN Horse H ON T.stableId = H.stableId
        JOIN RaceResults RR ON H.horseId = RR.horseId
        JOIN Race R ON RR.raceId = R.raceId
        WHERE RR.results = %s;
        """
        df = run_query(q, (pos,))
        st.dataframe(df)


def user_view_total_winnings():
    st.subheader("Total prize winnings per trainer")
    if st.button("Show Totals"):
        q = """
        SELECT T.fname AS Trainer_First, T.lname AS Trainer_Last, SUM(RR.prize) AS Total_Winnings
        FROM Trainer T
        JOIN Stable S ON T.stableId = S.stableId
        JOIN Horse H ON H.stableId = S.stableId
        JOIN RaceResults RR ON RR.horseId = H.horseId
        GROUP BY T.trainerId, T.fname, T.lname
        ORDER BY Total_Winnings DESC;
        """
        df = run_query(q)
        st.dataframe(df)


def user_view_tracks_counts():
    st.subheader("Tracks with race counts and participating horses")
    if st.button("Show Tracks"):
        q = """
        SELECT T.trackName AS Track_Name, COUNT(DISTINCT R.raceId) AS Race_Count, COUNT(DISTINCT RR.horseId) AS Total_Horses
        FROM Track T
        JOIN Race R ON T.trackName = R.trackName
        JOIN RaceResults RR ON R.raceId = RR.raceId
        GROUP BY T.trackName;
        """
        df = run_query(q)
        st.dataframe(df)


def main():
    st.title("Horse Racing Manager — Streamlit UI")

    mode = st.sidebar.selectbox("Mode", ["User", "Admin"])

    if mode == "Admin":
        st.sidebar.markdown("### Admin Actions")
        action = st.sidebar.selectbox("Action", [
            "Add Race with Results",
            "Delete Owner",
            "Transfer Horse",
            "Approve Trainer"
        ])
        if action == "Add Race with Results":
            admin_add_race()
        elif action == "Delete Owner":
            admin_delete_owner()
        elif action == "Transfer Horse":
            admin_transfer_horse()
        elif action == "Approve Trainer":
            admin_approve_trainer()

    else:  # User
        st.sidebar.markdown("### User Views")
        view = st.sidebar.selectbox("View", [
            "Horses by Owner Last Name",
            "Trainers by Result",
            "Total Winnings by Trainer",
            "Tracks with Race Counts"
        ])
        if view == "Horses by Owner Last Name":
            user_view_horses_by_owner()
        elif view == "Trainers by Result":
            user_view_trainers_by_result()
        elif view == "Total Winnings by Trainer":
            user_view_total_winnings()
        elif view == "Tracks with Race Counts":
            user_view_tracks_counts()


if __name__ == '__main__':
    main()
