from ftplib import FTP
import os
import json
import io
import numpy as np
import cv2
import oracledb

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

config_file = "config_trigger.json"

def load_latest_id():
    with open(config_file, "r") as file:
        config = json.load(file)
    return config.get("latest_id", 4990)

def update_latest_id(latest_id):
    config = {"latest_id": latest_id}
    with open(config_file, "w") as file:
        json.dump(config, file, indent=4)

def retrieve_data():
    latest_id = load_latest_id()
    print(f"Starting from ID: {latest_id}")

    # Connect to Oracle database
    connection = oracledb.connect(
        user=config_file['user'],
        password=config_file['password'],
        sid=config_file['id'],
        host=config_file['host'],
        port=config_file['port']
        )
    cursor = connection.cursor()
    print("Connected to database")

    while True:
        sql_query = "SELECT NAME, EMPLOYEE_NO, IMAGE_PATH, TYPE, ID FROM EVENT_REGISTRATION WHERE ID > :id"

        cursor.execute(sql_query, id=latest_id)
        rows = cursor.fetchall()

        for row in rows:
            img_encoded = retrieve_image(row[2])
            email_triggering(row[0], row[1], img_encoded, row[3])
            latest_id = row[4]
            update_latest_id(latest_id)

        print("--End of program--")
        cursor.close()
        connection.close()

def retrieve_image(remote_path) :
    ftp_host = config_file['ip']
    ftp_user = config_file['user']
    ftp_password = config_file['password']
    
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)

    # Create a BytesIO object to hold the image data in memory
    image_data = io.BytesIO()

    # Retrieve the image file and store it in the BytesIO object
    ftp.retrbinary(f"RETR {remote_path}", image_data.write)

    # Move the pointer to the beginning of the BytesIO object
    image_data.seek(0)

    # Read the image into a numpy array
    file_bytes = np.asarray(bytearray(image_data.read()), dtype=np.uint8)

    # Decode the image to opencv format
    image = cv2.imencode(file_bytes, cv2.IMREAD_COLOR)
    
    # Convert to bytes
    _, img_encoded = cv2.imencode(' .jpg', image)

    return img_encoded
    
def email_triggering(info1, info2, img_encoded, info3):
    smtp_server = config_file['server']
    smtp_port = config_file['port']  # Use plaintext port
    sender_email = config_file['sender']
    sender_name = config_file['sender_name']
    receiver_email = config_file['receiver']
    subject = "New Registration"
    body = f"""
    <html>
        <body>
            <h2>New Registration for {info3}</h2>
            <p>Name: {info1}.</p>
            <p>Employee No.: {info2}.</p>
            <img src="cid=image1" alt="Embedded Image">
        </body>
    </html>
    """

    # Create an in-memory binary stream for the image
    img_bytes = io.BytesIO(img_encoded.tobytes())

    # Create a MIMEMultipart email
    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the HTML body
    msg.attach(MIMEText(body, 'html'))

    # Attach the image
    img = MIMEImage(img_bytes.read(), _subtype='png', name='image.png')
    img.add_header('Content-ID', '<image1>')    # Matches the CID in the HTML body
    msg.attach(img)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)    # Optional: enable debug output for troubleshooting
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email: {'e}")

if __name__ == "__main__":
    retrieve_data()

