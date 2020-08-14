import sys
import socket
import struct
import random

auglist=sys.argv
x=1

client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client1.connect((auglist[1], int(auglist[2])))
from_server = client1.recv(4096).decode()
print( from_server)


client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client2.connect((auglist[3], int(auglist[4])))
from_server = client2.recv(4096).decode()
print( from_server)


frame_in_num=0

frame = struct.Struct('8s8s2I1000sI')            #struct template for frame out
ack = struct.Struct('2I')                   #struct for ack frame
frame_num = 0
frame_size=0    
end=0


def recvall2(sock):
    BUFF_SIZE=64
    data=b''
    while True:
        part=sock.recv(BUFF_SIZE)
        data=data+part
        if(len(part)<BUFF_SIZE):
            break
    return data



def recvall(sock):
    BUFF_SIZE=8224
    data=b''
    while True:
        part=sock.recv(BUFF_SIZE)
        data=data+part
        if(len(part)<BUFF_SIZE):
            break
    return data




def crc161(data,checksum_initia):
            s=checksum_initia
            w=0
            for i in range(0,len(data),1):
                x=str(data[i])
                w=(ord(x))
                s=s+w
            s=(s>>16)+(s & 0xffff);
            s=~s & 0xffff
            return s



message=''
print("Enter username for login (enter 'exit' to close this program ):")
message = input()
if(message=="exit"):
    client1.send(str.encode(message))
    client2.send(str.encode(message))
    #client.close()
    exit(1)    
client1.send(str.encode(message))
client2.send(str.encode(message))

from_server = client1.recv(4096).decode()
print(from_server, 'dasfafasg')
from_server = client2.recv(4096).decode()
print(from_server, 'dasfafasg')

fnd1 = client1.recv(4096).decode()
fnd2 = client2.recv(4096).decode()
#print(fnd, 'fnd')
pswd=''
if(fnd1=="found" and fnd2=="found"):
    print("Enter password :")
    pswd=input()
    client1.send(str.encode(pswd))
    client2.send(str.encode(pswd))
    asdd1 = client1.recv(4096).decode()
    asdd2 = client2.recv(4096).decode()
    print(asdd1,"pp")
    print(asdd2,"pp")

   # print(dasdd)
    asd1 = client1.recv(4096).decode()
    asd2 = client2.recv(4096).decode()
    #print(asd)
    if(asd1=="wp" and asd2=="wp"):
        print("Wrong Password !! program to be closed for security")
        client1.send(str.encode("exit"))
        client2.send(str.encode("exit"))
        exit(1)
    else:
        #xc=client.recv(4096).decode()               #recieves text match found in A,B or C
        print(asd1,'\n',asd2)
        print("Successfully Logged in !!! ")
        print("Enter probability to corrupt frames")
        prob=input()
        file = open("sample.txt", "rb")


        #starts sending file
        while end==0:
            if frame_in_num == frame_num :  
                frame_num += 1
                #print(frame_num,"@frame_num Increment")
            #print(frame_in_num,"#frame num from server")
            SendData = file.read(1000)
            read_last=SendData
            if len(SendData)==0:
                break
            

            checksum_pre_gremlin = crc161(SendData.decode('utf-8',errors="ignore"),0)
            checksum=checksum_pre_gremlin
            frame_size=len(SendData)
            random_number=random.randrange(100)
            xc=''
            
            if int(prob) > random_number:
                xc=SendData.decode('utf-8',errors="ignore")        
                #print(xc)
                xc1=list(xc)
                xc1[1]='$'
                xc=''.join(xc1)
                SendData=xc.encode('utf-8',errors="ignore")
        
            values = (str.encode("0.0.0.0"),str.encode("0.0.0.0"),frame_num, frame_size, SendData, checksum)
            #print(frame_num,"frame_num")
            
            frame_out = frame.pack(*values)             #pack data in frame
            print(len(frame_out))
            if frame_num%2==0:
                client1.sendall(frame_out)                   #output data
                acknowledgment=recvall2(client1)
            else:
                client2.sendall(frame_out)                   #output data
                acknowledgment=recvall2(client2)
            #print(acknowledgment,"ack ******")            
            frame_in_num,frame_in_ack=ack.unpack(acknowledgment)

            while frame_in_ack == 0:                    #while wrong frame
                SendData=read_last
                values = (str.encode("0.0.0.0"),str.encode("0.0.0.0"),frame_num, frame_size, SendData, checksum)
                #print(frame_num,"frame num in  loop")
                frame_out = frame.pack(*values)
                if frame_num%2==0:
                    client1.sendall(frame_out)            #send new frame
                    acknowledgment=recvall2(client1)
                else:
                    client2.sendall(frame_out)            #send new frame
                    acknowledgment=recvall2(client2)
                frame_in_num,frame_in_ack=ack.unpack(acknowledgment)

        file.close()

        #print(xc)
        print("Successfully Logged in !!! ")
        
        exit(1)

else:
    print("Wrong username !! Or Server is not responding")
    client1.send(str.encode("exit"))
    client2.send(str.encode("exit"))
    #client.close()
    exit(1)      
client1.close()
client2.close()
