import constants  # Import custom constants module for configurations
import psycopg2 as db_connect  # PostgreSQL database adapter
from datetime import date, timedelta  # For handling dates
import smtplib, ssl  # For sending emails securely
from email.message import EmailMessage  # For constructing email messages
from pymarc import Record  # For parsing MARC records to extract book titles

# Get today's date
today = date.today()

# Calculate the date three days from now
three_days_from_now = today + timedelta(days=3)

# Get the current day of the month as an integer (used for scheduling)
day_of_month = int(today.strftime("%d"))

def send_email(receiver_email, message):
    """
    Sends an email to the specified receiver with the given message.

    Parameters:
    - receiver_email (str): The email address of the recipient.
    - message (str): The content of the email to be sent.
    """
    email_msg = EmailMessage()  # Create a new email message object
    email_msg.set_content(message)  # Set the body of the email
    email_msg['Subject'] = ''  # Set the email subject
    email_msg['To'] = receiver_email  # Set the recipient of the email

    # Email server configuration from constants
    port = constants.PORT  # SMTP port number
    smtp_server = constants.SMTP_SERVER  # SMTP server address
    sender_email = constants.SENDER_EMAIL  # Sender's email address
    password = constants.EMAIL_PASSWORD  # Sender's email password

    # Create a secure SSL context for the connection
    context = ssl.create_default_context()

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)  # Upgrade the connection to secure TLS
        server.login(sender_email, password)  # Log in to the SMTP server
        server.sendmail(sender_email, receiver_email, email_msg.as_string())  # Send the email

def get_book_title(iso2709):
    """
    Extracts the book title from an ISO 2709 MARC record.

    Parameters:
    - iso2709 (str): The ISO 2709 MARC record data.

    Returns:
    - title (str): The title of the book.
    """
    # Create a Record object by decoding the ISO 2709 data
    record = Record(data=iso2709.encode())
    # Extract the title field and remove trailing characters (e.g., " /")
    title = record.title[0:-2]
    return title

def get_overdue_loans():
    """
    Retrieves loans that are overdue (expected return date is before today).

    Returns:
    - list: A list of overdue loans.
    """
    return get_loans('<', today)

def get_loans_due_in_three_days():
    """
    Retrieves loans that are due in exactly three days from today.

    Returns:
    - list: A list of loans due in three days.
    """
    return get_loans('=', three_days_from_now)

def get_loans_due_today():
    """
    Retrieves loans that are due today.

    Returns:
    - list: A list of loans due today.
    """
    return get_loans('=', today)

def get_loans(operator, due_date):
    """
    Retrieves loans from the database based on the expected return date and operator.

    Parameters:
    - operator (str): Comparison operator (e.g., '<', '=', '>').
    - due_date (date): The date to compare the expected return date against.

    Returns:
    - list: A list of loans matching the criteria.
    """
    # Database connection parameters from constants
    host_name = constants.DB_HOST
    db_user = constants.DB_USER
    db_password = constants.DB_PASSWORD
    db_name = constants.DB_NAME

    # Connect to the PostgreSQL database
    with db_connect.connect(host=host_name, user=db_user, password=db_password, database=db_name) as connection:
        # Create a cursor for executing queries
        with connection.cursor() as cursor:
            # SQL query to retrieve loans based on the specified criteria
            query = f''' # You must consult your own table for the data.
  '''
            cursor.execute(query)  # Execute the query
            results = cursor.fetchall()  # Fetch all matching records
            return results

def process_loans(loans, message):
    """
    Processes a list of loans by sending email notifications to borrowers.

    Parameters:
    - loans (list): A list of loans to process.
    - message (str): The email message template to use.
    """
    for loan in loans:
        name = loan[1]  # Borrower's name
        email_addr = loan[2]  # Borrower's email address
        book_title = get_book_title(loan[3])  # Extract the book title
        expiration_date = loan[4]  # Expected return date
        # Calculate the number of days late (if overdue)
        days_late = today - expiration_date.date()
        # Format the email message with the borrower's details
        email_message = message.format(
            name=name,
            email_addr=email_addr,
            book_title=book_title,
            expiration_date=expiration_date.strftime('%d/%m/%Y'),
            days_late=days_late.days
        )
        send_email(email_addr, email_message)  # Send the email notification
        # print(email_message)  # Optionally print the message for debugging

# Retrieve overdue loans
overdue_loans = get_overdue_loans()

# Email message template for overdue loans
overdue_message = f"""\ # Message
"""

# Send overdue notifications only on the 1st and 15th of the month
if (day_of_month == 1 or day_of_month == 15):
    process_loans(overdue_loans, overdue_message)

# Retrieve loans that are due in three days
loans_due_in_three_days = get_loans_due_in_three_days()

# Email message template for loans due in three days
due_in_three_days_message = f"""\ # Message
"""

# Send notifications for loans due in three days
process_loans(loans_due_in_three_days, due_in_three_days_message)

# Retrieve loans that are due today
loans_due_today = get_loans_due_today()

# Email message template for loans due today
due_today_message = f"""\ # Message
"""

# Send notifications for loans due today
process_loans(loans_due_today, due_today_message)