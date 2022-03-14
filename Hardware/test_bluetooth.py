import serial
import time
import sys
import signal
def signal_handler(signal, frame):
	print("closing program")
	SerialPort.close()
	sys.exit(0)

SerialPort = serial.Serial(port = '/dev/rfcomm1', baudrate = 9600, timeout = 2)

SerialPort.write(bytes('> 0','utf-8'))
time.sleep(4)

# bin repr display
num = int(input("Enter number to encode : "))
bit_input = bin(num)[2:]

print("Enjoy the binary representation!")

for bit in bit_input:
    OutgoingData = f'> 1'
    SerialPort.write(bytes(OutgoingData,'utf-8'))
    if bit == '1':
        sleep_time = 0.6
    else:
        sleep_time = 0.04
    
    time.sleep(sleep_time)
    
    # close the bit
    SerialPort.write(bytes('> 0','utf-8'))
    time.sleep(1)
    

SerialPort.write(bytes('> 0','utf-8'))
SerialPort.close()
    
