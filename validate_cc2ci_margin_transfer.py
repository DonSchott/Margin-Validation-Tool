import sqlite3


def fetch_margins(conn, table_name, report_date, report_time=None):
    """Fetch margin values from the specified table for the given report date and time."""
    cursor = conn.cursor()
    if report_time:
        cursor.execute(f"SELECT margin FROM {table_name} WHERE date = ? AND time_of_day = ?", (report_date, report_time))
    else:
        cursor.execute(f"SELECT margin FROM {table_name} WHERE date = ?", (report_date,))
    return [row[0] for row in cursor.fetchall()]


# validation partly implemented
# TODO add logical complete validation logic
def validate_cc2ci(cc050_data, ci050_data):
    """Validate all eod margin values are the respective next day ci reports 08:00 margin values."""

    discrepancies = []
    for cc_row in cc050_data:
        if cc_row not in ci050_data:
            discrepancies.append(f"Margin missing in CI050: {cc_row}")
    return discrepancies


def main():
    conn = sqlite3.connect('LZDB_dummy.db')

    # Fetch margins from CC050 and CI050 for the respective business days of interest
    # TODO be more flexible regarding start of trading time. currently report_time='08:00:00' hardcoded
    cc050_data = fetch_margins(conn, 'CC050', '2020-05-11')
    ci050_data = fetch_margins(conn, 'CI050', '2020-05-12', report_time='08:00:00')

    # Validate that yesterdays eod cc margin is today's first ci margin
    discrepancies = validate_cc2ci(cc050_data, ci050_data)

    if discrepancies:
        print("Error: Margins validation failed. Please have a look! Discrepancies found:")
        for error in discrepancies:
            print(error)
    else:
        print("Margins validation successful. No discrepancies found.")

    conn.close()


if __name__ == '__main__':
    main()
