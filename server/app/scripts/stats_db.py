import sqlite3
import os
import json

from .config import EXPORT_PATH

# Convert the stats from the inputs folder to an sqlite3 database for easier querying in the frontend
# Create DB

def CreateStatsDB(export_path):

    sql_statements = [ 
    """CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY,
            pg_id INTEGER,
            date DATE, 
            bpsDropped INTEGER,
            ppsDropped INTEGER,
            ppsPassed INTEGER,
            bpsPassed INTEGER
        );
        """,
        """DELETE FROM traffic;""",
    ]

    try:
        with sqlite3.connect(os.path.join(export_path, "stats.db")) as conn:
            # create a cursor
            cursor = conn.cursor()

            # execute statements
            for statement in sql_statements:
                cursor.execute(statement)

            # commit the changes
            conn.commit()

            print("Tables created successfully.")
            return True
    except sqlite3.OperationalError as e:
        print("Failed to create tables:", e)
        return False

def InsertTrafficStats(export_path):
    print("Inserting traffic stats into DB...")
    conn_stats = sqlite3.connect(os.path.join(export_path, "stats.db"))
    cur_stats = conn_stats.cursor()

    basepath = os.path.abspath(os.path.join(export_path, "inputs", "stats", 'traffic'))
    if not os.path.exists(basepath):
        print(f"Stats folder not found in {basepath}")
        return {'success': False, 'message': 'Stats folder not found'}


    # add_stat = ("INSERT INTO traffic (pg_id, date, bpsDropped, ppsDropped, ppsPassed, bpsPassed) VALUES (%(pg_id)s, %(date)s, %(bpsDropped)s, %(ppsDropped)s, %(ppsPassed)s, %(bpsPassed)s)")
    # sql = "INSERT INTO traffic (pg_id, date, bpsDropped, ppsDropped, ppsPassed, bpsPassed) VALUES (%s, %s, %s, %s, %s, %s)"
    sql = "INSERT INTO traffic (pg_id, date, bpsDropped, ppsDropped, ppsPassed, bpsPassed) VALUES (?, ?, ?, ?, ?, ?)"

    print(f"Looking for traffic stats in {basepath}...")
    for filename in os.listdir(basepath):
        if filename.endswith(f".json"):
            pg_id = filename.split('_')[0]

        print(f"Processing stats for PG {pg_id} from file {filename}...")
        
        with open(os.path.join(basepath, filename), 'r') as f:
            data = json.load(f)

        for index, item in enumerate(data['timeseries-data'][0]['times']):

            val = (
                pg_id, 
                item[0], 
                data['timeseries-data'][0]['bpsDropped'][index], 
                data['timeseries-data'][0]['ppsDropped'][index], 
                data['timeseries-data'][0]['ppsPassed'][index], 
                data['timeseries-data'][0]['bpsPassed'][index]
            )
            cur_stats.execute(sql, val)
            conn_stats.commit()
            # print(f"Inserting stats for PG {pg_id} at date {entry[0]}")

    # Select count from DB to check
    cur_stats.execute("SELECT COUNT(*) FROM traffic;")
    count = cur_stats.fetchone()[0]
    print(f"Total rows in traffic table: {count}")

    cur_stats.close()
    conn_stats.close()

    return True