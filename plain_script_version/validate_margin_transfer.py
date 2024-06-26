import sqlite3
import logging
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import credentials

# Setup logging
logging.basicConfig(filename='../margin_validation.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %('
                                                                                     'message)s')


def fetch_margins(conn, table_name, report_date, report_time=None):
    """Fetch rows from the specified table given the report date and (optionally) report time.
       RETURN TYPE: List of Tuples"""
    cursor = conn.cursor()
    if report_time:
        cursor.execute(
            f'SELECT date, time_of_day, clearing_member, account, margin_type, margin FROM {table_name} WHERE date = '
            f'? AND time_of_day = ?',
            (report_date, report_time))
    else:
        cursor.execute(f"SELECT date, clearing_member, account, margin_type, margin FROM {table_name} WHERE date = ?",
                       (report_date,))
    margins_list = cursor.fetchall()
    return margins_list


def get_min_time_of_day(conn, table_name, report_date):
    """Get the minimal time of day for a given date from the specified table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT MIN(time_of_day) FROM {table_name} WHERE date = ?", (report_date,))
    min_time = cursor.fetchone()[0]
    return min_time


def get_max_time_of_day(conn, table_name, report_date):
    """Get the maximal time of day for a given date from the specified table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX(time_of_day) FROM {table_name} WHERE date = ?", (report_date,))
    max_time = cursor.fetchone()[0]
    return max_time


def validate_elements_of_list1_in_list2(list1, list2):
    """
    Check for two lists of tuples if all the first lists elements are found in list two.
    For the comparison irrelevant columns date and (optionally) time_of_day are sliced of.
    """

    # note: only the four last columns are relevant to compare cc050_data and ci050_data, respectively.
    #       we keep columns date, time_of_day for error message / logging.
    discrepancies = []
    for list1_row in list1:
        list1_relevant_rows = list1_row[-4:]
        found_match = False
        for list2_row in list2:
            list2_relevant_rows = list2_row[-4:]
            if list1_relevant_rows == list2_relevant_rows:
                found_match = True
                break
        if not found_match:
            discrepancies.append(f"Margin missing: {list1_row}")
    return discrepancies


def send_email(subject, body):
    """Sends an alert email when validation failed."""

    # email credentials NOT shared in public repo. get them from credentials file
    sender_email = credentials.sender_email
    sender_email_pw = credentials.sender_email_pw
    receiver_email = credentials.receiver_email

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
    message["Subject"] = subject

    # Structure email, add body to email
    message.attach(MIMEText(body, "plain"))

    # Convert the message to a string and send it
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(sender_email, sender_email_pw)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)


def main():
    conn = sqlite3.connect('../LZDB_dummy.db')

    # we suppose the checks are run at 10am on
    today = '2020-05-12'
    # therefore...
    yesterday = '2020-05-11'

    # CHECK 1: Check, if the end-of-day values of the previous day are the same as the first intraday values.

    cc050_yesterday = fetch_margins(conn, 'CC050', yesterday)
    ci050_today_first = fetch_margins(conn, 'CI050', today,
                                      report_time=get_min_time_of_day(conn, 'CI050', today))

    # Validate that yesterdays eod cc margins are found in today's first ci margin. And vice versa.
    missing_cc050 = validate_elements_of_list1_in_list2(cc050_yesterday, ci050_today_first)
    missing_ci050 = validate_elements_of_list1_in_list2(ci050_today_first, cc050_yesterday)

    # CHECK 2: Check if the end-of-day values are the same as the last intraday values.

    ci050_yesterday_last = fetch_margins(conn, 'CI050', yesterday,
                                         report_time=get_max_time_of_day(conn, 'CI050', yesterday))

    missing_cc050 += validate_elements_of_list1_in_list2(cc050_yesterday, ci050_yesterday_last)
    missing_ci050 += validate_elements_of_list1_in_list2(ci050_yesterday_last, cc050_yesterday)

    # Remove duplicates
    missing_cc050 = list(set(missing_cc050))
    missing_ci050 = list(set(missing_ci050))

    # If check1 or check2 failed write error messages, add them to the log file and send alert emails
    if not missing_cc050 and not missing_ci050:
        print("Margins validation successful. No discrepancies found.\n")
    if missing_cc050:
        error_message = "\nValidation failed! Missing margins in CC050:\n"
        for error in missing_cc050:
            error_message += error + '\n'
        print(error_message)
        logging.error(error_message)
        send_email("Validation Alert: Missing Margins in CC050", error_message)
    if missing_ci050:
        error_message = "\nValidation failed! Missing margins in CI050:\n"
        for error in missing_ci050:
            error_message += error + '\n'
        print(error_message)
        logging.error(error_message)
        send_email("Validation Alert: Missing Margins in CI050", error_message)

    conn.close()


if __name__ == '__main__':
    main()
