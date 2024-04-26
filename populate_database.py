import sqlite3


def create_tables(conn):
    """Create tables CC050 and CI050 in the SQLite database."""
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS CC050 (
                    date TEXT,
                    clearing_member TEXT,
                    account TEXT,
                    margin_type TEXT,
                    margin REAL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS CI050 (
                    date TEXT,
                    time_of_day TEXT,
                    clearing_member TEXT,
                    account TEXT,
                    margin_type TEXT,
                    margin REAL
                    )''')

    conn.commit()


def insert_data_cc050(conn, data):
    """Insert example data provided into the CC050 table."""
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO CC050 VALUES (?, ?, ?, ?, ?)", data)
    conn.commit()


def insert_data_ci050(conn, data):
    """Insert example data provided into the CI050 table."""
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO CI050 VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()


def populate_database(database_path, cc050_exp_data, ci050_exp_data):
    """Populate the SQLite database with example data provided."""
    conn = sqlite3.connect(database_path)

    create_tables(conn)

    insert_data_cc050(conn, cc050_exp_data)

    insert_data_ci050(conn, ci050_exp_data)

    conn.close()


# Example data from specific_example.txt file for EoD (end of day) reports CC050 table
cc050_data = [
    ('2020-05-11', 'Bank 1', 'A1', 'SPAN', 3212.2),
    ('2020-05-11', 'Bank 1', 'A1', 'IMSM', 837.1),
    ('2020-05-11', 'Bank 1', 'A2', 'SPAN', 8963.3),
    ('2020-05-11', 'Bank 1', 'A2', 'IMSM', 76687.9),
    ('2020-05-11', 'Bank 2', 'A1', 'SPAN', 821.4),
    ('2020-05-11', 'Bank 2', 'A1', 'SPAN', 8766.4),
]

# Same for Intraday reports CI050 table
ci050_data = [
    ('2020-05-11', '18:00:00', 'Bank 1', 'A1', 'SPAN', 2882.2),
    ('2020-05-11', '18:00:00', 'Bank 1', 'A1', 'IMSM', 988.1),
    ('2020-05-11', '18:00:00', 'Bank 1', 'A2', 'SPAN', 788.3),
    ('2020-05-11', '18:00:00', 'Bank 1', 'A2', 'IMSM', 908.9),
    ('2020-05-11', '18:00:00', 'Bank 2', 'A1', 'SPAN', 123.4),
    ('2020-05-11', '18:00:00', 'Bank 2', 'A1', 'IMSM', 8326.4),
    ('2020-05-11', '19:00:00', 'Bank 1', 'A1', 'SPAN', 3212.2),
    ('2020-05-11', '19:00:00', 'Bank 1', 'A1', 'IMSM', 837.1),
    ('2020-05-11', '19:00:00', 'Bank 1', 'A2', 'SPAN', 8963.3),
    ('2020-05-11', '19:00:00', 'Bank 1', 'A2', 'IMSM', 76687.9),
    ('2020-05-11', '19:00:00', 'Bank 2', 'A1', 'SPAN', 821.4),
    ('2020-05-11', '19:00:00', 'Bank 2', 'A1', 'IMSM', 8766.4),
    ('2020-05-12', '08:00:00', 'Bank 1', 'A1', 'SPAN', 3212.2),
    ('2020-05-12', '08:00:00', 'Bank 1', 'A1', 'IMSM', 837.1),
    ('2020-05-12', '08:00:00', 'Bank 1', 'A2', 'SPAN', 8963.3),
    ('2020-05-12', '08:00:00', 'Bank 1', 'A2', 'IMSM', 76687.9),
    ('2020-05-12', '08:00:00', 'Bank 2', 'A1', 'SPAN', 821.4),
    ('2020-05-12', '08:00:00', 'Bank 2', 'A1', 'IMSM', 8766.4),
    ('2020-05-12', '09:00:00', 'Bank 1', 'A1', 'SPAN', 3133.9),
    ('2020-05-12', '09:00:00', 'Bank 1', 'A1', 'IMSM', 137.1),
    ('2020-05-12', '09:00:00', 'Bank 1', 'A2', 'SPAN', 2963.3),
    ('2020-05-12', '09:00:00', 'Bank 1', 'A2', 'IMSM', 74687.9),
    ('2020-05-12', '09:00:00', 'Bank 2', 'A1', 'SPAN', 811.4),
    ('2020-05-12', '09:00:00', 'Bank 2', 'A1', 'IMSM', 8366.4),
]

populate_database("LZDB_dummy.db", cc050_data, ci050_data)
