from socket import *
import _thread as thd
import sys
import time
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

'''
TEM UM BUG: 
- Se o usuário de um lado estiver digitando e o do outro lado enviar uma mensagem,
    o que esse usuário digitou some mas continua no buffer. Se ele pressionar
    enter, o que ele já tinha digitado é enviado.
''' 

def user_read():
    global connected
    global server_publicKey
    while 1:
        sentence = input('\033[1;33m[You]:\033[0m ')

        if not connected:
            break

        if sentence == "quit":
            connected = False
            connectionSocket.close()
        
        sentence = bytes(sentence, "utf-8")
        encoded_message = server_public_key.encrypt(sentence, 32)
        connectionSocket.send(encoded_message)
        
def server_print():
    global connected
    global key
    while 1:
        if not connected:
            break
        response = key.decrypt(connectionSocket.recv(1024).decode())

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

print("Generating and exchanging keys...")
server_publicKey = RSA.importKey(connectionSocket.recv(1024).decode()) # wait for server's public key
random_generator = Random.new().read # generate my keys
key = RSA.generate(1024, random_generator)
publickey = key.publickey()
connectionSocket.send(publickey.exportKey()) # send my public key to server
print("Done.\n")

thd.start_new_thread( user_read, () )
thd.start_new_thread( server_print, () )

while connected:
    continue