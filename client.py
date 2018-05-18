from socket import *
import _thread as thd
import sys
import time

'''
TEM UM BUG: 
- Se o usuário de um lado estiver digitando e o do outro lado enviar uma mensagem,
    o que esse usuário digitou some mas continua no buffer. Se ele pressionar
    enter, o que ele já tinha digitado é enviado.
''' 

def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

def user_read():
    global connected
    while 1:
        print("\033[1;33m[You]:\033[0m ")
        sentence = ""
        nch = _find_getch()
        while(nch != "\n") {
            sentence += nch
            nch = _find_getch()
        }

        if not connected:
            break

        if sentence == "quit":
            connected = False
            connectionSocket.close()
        
        encoded_message = bytes(sentence, "utf-8")
        connectionSocket.send(encoded_message)
        
def server_print():
    global connected
    while 1:
        if not connected:
            break
        response = connectionSocket.recv(1024).decode()

        if response == "":
            continue

        print("\r\033[1;31m[Server]:\033[0m ", response, "\n\033[1;33m[You]:\033[0m", end='')

serverName = input("Server: ")
serverPort = int(input("Port: "))
connectionSocket = socket(AF_INET, SOCK_STREAM)
connected = False
typed_message = ""
print("Waiting for server (",serverName,":",serverPort,")...")

while not connected:
    try:
        connectionSocket.connect((serverName,serverPort))
        connected = True
    except Exception as e:
        pass

print("Connection established with ", serverName)
thd.start_new_thread( user_read, () )
thd.start_new_thread( server_print, () )

while connected:
    continue