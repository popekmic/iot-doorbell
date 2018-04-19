from threading import Thread
from time import sleep
import requests

class MessageNotifyThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.message = None
        self.running = True

    def run(self):
        while self.running:
            url = 'http://{}/message/value'.format(TCP_IP)
            response = requests.get(url)
            self.message = response.text
            sleep(5)

TCP_IP = 'popekmic.pythonanywhere.com'

button_pressed = True

message_thread = MessageNotifyThread()
message_thread.start()


def get_message():
    res = message_thread.message
    message_thread.message = None
    return res

def is_button_pressed():
    #todo at school
    global button_pressed
    res = button_pressed
    button_pressed = False
    return res

def show_message(message):
    #todo at school
    print(message)

def get_image_from_camera():
    #todo at school
    return open("ring.jpg",'rb')

def send_ring():
    image = get_image_from_camera()
    url = 'http://{}/ring'.format(TCP_IP)
    files = {'media': image}
    requests.post(url,files = files)
    image.close()

def main_loop():
    try:
        while True:
            if is_button_pressed():
                send_ring()
            new_message = get_message()
            if new_message is not None:
                show_message(new_message)
            sleep(0.05)
    except KeyboardInterrupt:
        print('Interrupting.')
        message_thread.running = False

if __name__ == '__main__':
    main_loop()
