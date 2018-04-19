import socket
import os
from threading import Thread
import time
from flask import Flask
from flask import request
import signal
import sys
import smtplib
from werkzeug.utils import secure_filename

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
files_count = 1;

class ClientThread(Thread):
    def __init__(self,ip,port,conn):
        Thread.__init__(self)
        self.conn = conn
        self.running = True
        self.message = None
        print("New thread started")

    def run(self):
        while self.running:
            try:
                if self.message is not None:
                    self.conn.send(self.message.encode())
                    print("Sending : " + "{}".format(self.message))
                    self.message = None
            except:
                print("Exception in client thread.")
                break
        self.conn.close()

class ServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True

    def run(self):
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpsock.bind((TCP_IP, TCP_PORT))
        tcpsock.settimeout(5)
        self.threads = []

        while self.running:
            try:
                tcpsock.listen(4)
                print("Waiting for incoming connections...")
                (conn, (ip,port)) = tcpsock.accept()
                newthread = ClientThread(ip,port,conn)
                newthread.start()
                self.threads.append(newthread)
            except:
                print("Timeout in server thread")

        for thread in self.threads:
            thread.running = False

        for t in self.threads:
            t.join()

    def send_message(self,message):
        for thread in self.threads:
            thread.message = message


app = Flask(__name__)
server = ServerThread()
server.start()

def handler(signal, frame):
    print('CTRL-C pressed!')
    server.running = False
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

@app.route('/')
def index():
    return 'Nothing to see here.'

@app.route('/message')
def input_message():
    return """<form action="/message/params">
                  Your message to display:<br>
                  <input type="text" value="Write message here..." name="message_value"><br>
                  <input type="submit" value="Submit">
                </form>"""

@app.route('/message/<value>')
def set_custom_message(value):
    server.send_message(value)
    return "Message set!"

@app.route('/message/params')
def set_custom_message_params():
    message = request.args.get('message_value')
    server.send_message(message)
    return "Message set!"

@app.route('/photos/<name>')
def show_photo(name):
    print(name)
    result = """<img src= />"""
    return app.send_static_file('.\\uploads\\{}'.format(name))

@app.route('/ring',methods=['POST'])
def ring():
    global files_count
    file = request.files['media']
    filename = secure_filename(file.filename)
    filename_parts = filename.split(".");
    filename = "{}_{}.{}".format(filename_parts[0],files_count,filename_parts[1])
    files_count = files_count + 1
    file.save(os.path.join('.\\uploads', filename))

    socket.setdefaulttimeout(None)
    HOST = "smtp.gmail.com"
    PORT = 587
    sender= "awindlord@gmail.com"
    password = "o17wne28r"
    receiver= "michal.popek.bv@gmail.com"

    msg = """From: {}
            To: {}
            Subject: {}

            {}""".format(sender,receiver,'Subject - Hello World',
            'Someone is ringing! Take a look at him here: www.template.com. Reply to him here: {}:{}/message'.format(TCP_IP,5000))

    server = smtplib.SMTP()
    server.connect(HOST, PORT)
    server.starttls()
    server.login(sender,password)
    server.sendmail(sender,receiver, msg)
    server.close()
    return "Ring successfull!"
