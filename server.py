import socket
import sys
import time
from datetime import datetime

def checkPort(port):
    if port < 1024 or port > 64000:
        print("Not in range sorry")
        sys.exit()

def createBindSocket(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
        print("Socket binding completed")
        return s

    except:
        print("Sorry failed to bind socket")
        sys.exit()

def startListening(s):
    try:
        s.listen(5)
        print("Now listening")
    except:
        print("Listen failed")
        sys.exit()

def serverLoop(s):
    while True:
        clientsocket = acceptClient(s)
        filenameLen = receiveHeader(clientsocket, s)
        fileNameInBytes = receiveFileName(clientsocket, filenameLen, s)
        sendResponce(clientsocket, fileNameInBytes, s)

def acceptClient(s):
    clientsocket, address = s.accept()
    clientsocket.settimeout(1)
    print("Connection established at {}".format(datetime.now().strftime('%H:%M:%S on %d-%m-%y')))
    print("IP address: {}\nPort Number: {}".format(address[0], address[1]))
    return clientsocket

def receiveHeader(clientsocket,s):
    try:
        information = clientsocket.recv(5)
    except socket.timeout:
        print("Sorry the connection has timed out")

    magicNum = (information[0] << 8) + information[1]
    sType = information[2]
    filenameLen = (information[3] << 8) + information[4]
    if magicNum != 0x497E or sType != 1 or filenameLen < 1 or filenameLen > 1024:
        print("Sorry the file request is erroneous")
        clientsocket.close()
        serverLoop(s)
    return filenameLen

def receiveFileName(clientsocket, filenameLen, s):
    try:
        fileNameInBytes = clientsocket.recv(1024)
    except socket.timeout:
        print("Sorry the connection has timed out")
        clietsocket.close()
        serverLoop(s)
    if len(fileNameInBytes) != filenameLen:
        print("Sorry incorrect number of bytes")
        clientsocket.close()
        serverLoop(s)
    return fileNameInBytes


def sendResponce(clientsocket, fileNameInBytes, s):
    fileName = fileNameInBytes.decode('UTF-8')
    try:
        with open(fileName, 'rb') as i:
            fileData = i.read()
    except:
        print("Sorry selected file does not exist")
        fileResponse = bytearray([0x49, 0x7e, 2, 0, 0, 0, 0, 0] )
        clientsocket.sendall(fileResponse)
        clientsocket.close()
        serverLoop(s)

    fileDataLen = len(fileData)
    byte5 = fileDataLen >> 24
    byte6 = (fileDataLen & 0x00FF0000) >> 16
    byte7 = (fileDataLen & 0x0000FF00) >> 8
    byte8 = fileDataLen & 0x000000FF
    head = bytearray([0x49, 0x7e, 2, 1, byte5, byte6, byte7, byte8] )
    fileResponse = head + fileData
    print("File sent {} bytes transfered".format(len(fileResponse)))
    clientsocket.sendall(fileResponse)
    clientsocket.close()
    

def run():
    port = int(sys.argv[1])
    checkPort(port)
    s = createBindSocket(port)
    startListening(s)
    serverLoop(s)
    s.close()
run()
