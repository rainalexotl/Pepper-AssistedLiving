import socket
import sys
import os
import datetime
import time
import platform

open('log.txt', 'w').close()

f = open('log.txt', 'a', os.O_NONBLOCK)

logString = '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * \n'
f.write(logString)
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
logString = '[' + st + '][SYSTEM] Starting new session... \n'
f.write(logString)
f.write('\n')

system = 'System: ' + platform.system() + '\n'
f.write(system)
machine = 'Machine: ' + platform.machine() + '\n'
f.write(machine)
platformString = 'Platform: ' + platform.platform() + '\n'
f.write(platformString)
version = 'Version: ' + platform.version() + '\n'
f.write(version)
MacVersion = 'MacVersion: ' + str(platform.mac_ver()) + '\n'
f.write(MacVersion)
f.write('\n')
f.flush()
f.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 3008)
print ('[CLIENT_SIMULATE] Connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    while True:
        message = raw_input("Utterance: ")
        sock.sendall(message)

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        logString = '[' + st + '][UTTERANCE] ' + message + '\n'

        f = open('log.txt', 'a', os.O_NONBLOCK)
        f.write(logString)
        f.flush()
        f.close()

finally:
    print('[CLIENT_SIMULATE] Closing socket...')
    sock.close()