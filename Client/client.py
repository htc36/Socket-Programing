import socket
import sys
import os.path

def argumentGetter():
    if len(sys.argv) != 4:
        print("Sorry incorrect number of arguments")
        sys.exit()
    ip = sys.argv[1]
    port = int(sys.argv[2])
    fileName = sys.argv[3]
    return ip, port, fileName


def checkIp(ip, port):
    try:
        portIp = socket.getaddrinfo(ip, port)[1][-1]
        print("Correct IP")
    except:
        print("Sorry there is an error with the IP address")
        sys.exit()
    return portIp

def checkPortandfile(port, fileName):
    if port < 1024 or port > 64000:
        print("Sorry port number is out of range")
        sys.exit()

    if os.path.isfile(fileName):
        print("Sorry file already exists")
        sys.exit()

def createConnect(portIp):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Sorry creating socket has failed")
    s.settimeout(1)
    try:
        s.connect(portIp)
    except:
        print("Sorry socket has failed to connect")
    return s 

def makeFileRequest(fileName, s):
    byteFileName = fileName.encode('UTF-8')
    n = len(byteFileName)  
    magicNum = 0x497e
    head = bytearray([magicNum >> 8, magicNum & 0x00FF, 1, n >> 8, n & 0x00FF])
    fileRequest = head + byteFileName
    s.sendall(fileRequest)

def receiveResponse(s):
    try: 
        head = s.recv(8)
    except socket.timeout:
        print("Sorry the socket has timed out")
        sys.exit()
    except: 
        print("Sorry the response from the server is eranious")
        sys.exit()

    magicNum = (head[0] << 8) + head[1]
    sType = head[2]
    statusCode = head[3]
    fileDataLen = getFileDataLen(head)
    if magicNum != 0x497E or sType != 2 or (statusCode != 0 and statusCode != 1):
        print("Sorry the file header is eranious")
        sys.exit()
    return statusCode, fileDataLen

def getFileDataLen(head):
    first = head[4] << 24
    second = head[5] << 16
    third = head[6] << 8
    fourth = head[7]
    return first + second + third + fourth

def writeDataResponse(s, statusCode, fileName, fileDataLen):
    counter = 0
    if statusCode == 1:
        with open(fileName, 'wb') as i:
            while True:
                try:
                    information = s.recv(4096)
                except socket.timeout:
                    print("Sory the socket has timed out")
                if not information:
                    break
                counter += len(information)
                i.write(information)
            if counter != fileDataLen:
                os.remove(fileName)
                s.close()
                sys.exit()
    else:
        print("Sorry, file does not exist on the server")
        s.close()
        sys.exit()
    print("File transfer completed, have a nice day")
    s.close()
    
def run():
    ip, port, fileName = argumentGetter()
    portIp = checkIp(ip, port)
    checkPortandfile(port, fileName)
    s = createConnect(portIp)
    makeFileRequest(fileName, s)
    statusCode, fileDataLen = receiveResponse(s)
    writeDataResponse(s, statusCode, fileName, fileDataLen)
run()
