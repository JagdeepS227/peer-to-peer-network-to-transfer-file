import sys
import socket
import csv
import threading
import struct
import os
import random


auglist=sys.argv
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind(('0.0.0.0', int(auglist[1])))
serv.listen(5)




frame = struct.Struct('8s8s2I1000sI')            #struct template for frame out
ack = struct.Struct('2I')                   #struct for ack frame
frame_number = 1
frame_size=1    

prev_frame_num=0
curr_frame_num=1
end=0

table = open('routing.rtl', 'r')
data = table.readlines()
row0 = data[0].split('|')
row1 = data[1].split('|')
row2 = data[2].split('|')
#row3 = data[3].split('|')


def handle_client_connection(client_socket,address):     

        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client1.connect((row0[1], int(row0[2].strip())))
        from_server1 = client1.recv(4096).decode()

        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2.connect((row1[1], int(row1[2].strip())))
        from_server2 = client2.recv(4096).decode()

        client3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client3.connect((row2[1], int(row2[2].strip())))
        from_server3 = client3.recv(4096).decode()

      



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
        

        def bac(s):
            s=(s>>16)+(s & 0xffff);
            s=~s & 0xffff
            return s
        def abc(data,s,w):
            for i in range(0,len(data),1):
                x=str(data[i])
                w=(ord(x))
                s=s+w
            s=bac(s)
            return s
        
        def crc161(data,checksum_initia):
            s=checksum_initia
            w=0
            s=abc(data,s,w)
            return s

    
        def data_check( frame_in_num , data, checksum_client ,frame_size,m): #checks data
            global prev_frame_num                              #takes in last accpeted frame number
            if m==0:
                prev_frame_num=0
                return (0,prev_frame_num)
            checksum_server = crc161(data,checksum_client)       #generates new checksum
            #print('server = ', checksum_server , 'client = ', checksum_client)
            #print("********",prev_frame_num,"**********",frame_in_num)
            if frame_in_num == prev_frame_num+1 and checksum_server==0 :  #checks for correct frame number and correct checksum
                prev_frame_num += 1                             #if correct, updates last accpeted frame
                return (1,prev_frame_num)                                      #returns 1 for ack, 0 for nak
            else:
                return (0,prev_frame_num)


        frame_number=1
        frame_size=1
        prev_frame_num=0
        curr_frame_num=1
        end=0
        data_check(0,'',0,0,0)



        #client_socket.send(" ** Connection Established ** ".encode())
        # print ('Accepted connection from {}:{}'.format(address[0], address[1]))    
        username = client_socket.recv(4096).decode()
        if(username=="exit"):
            print("ID" + str(address) + ": " + "Disconected****************************************")    
            client_socket.close()
            exit()
        #print(username, 'username')
        client_socket.send(" ** message recieved at server ** ".encode())
        client1.send(str.encode(username))
        data1 = client1.recv(4096).decode()
       # print('1')
        client2.send(str.encode(username))
       # print('2send')
        data2 = client2.recv(4096).decode()
        #print('2')
        
        client3.send(str.encode(username))
        data3 = client3.recv(4096).decode()
       # print('3')
        

       # print('send')

       
        if(data1=="found"):
            print("User found in A")
            client_socket.send("found".encode()) 
        elif(data2=="found"):
            print("User found in B")
            client_socket.send("found".encode()) 
        elif(data3=="found"):
            print("User found in C")
            client_socket.send("found".encode())         
        else:
            client_socket.send("notfound".encode()) 
            print("User not found")

        flag=0
        flag2=0
        if(data1=="found"):
            flag=1
        elif(data2=="found"):
            flag=2
        elif(data3=="found"):
            flag=3
        
        pswd = client_socket.recv(4096).decode()
        client_socket.send(" ** message recieved at server ** ".encode())

        if(flag==1):
            client1.send(str.encode(pswd))
        elif(flag==2):
            client2.send(str.encode(pswd))
        elif(flag==3):
            client3.send(str.encode(pswd))
        
            
        p1 = ''
        p2 = ''
        p3 = ''
        fg=0
        if(flag==1):                        
            p1=client1.recv(4096).decode()
            if(p1=="passwordmatched"):          # success with server_a
                client_socket.send("match found in A".encode('utf-8',errors="ignore"))    #notifying to client
                num=0
                #file = open("recv.txt", "wb") 
                while end==0:
                    num+=1
                    RecvData =recvall(client_socket)
                    print(RecvData)
                    if len(RecvData)==0:
                        end=1
                        break
                    client1.sendall(RecvData)                   #sending recieved data directly to server_a
                    acknowledgment=recvall2(client1)
                    client_socket.sendall(acknowledgment)

                #file.close()


                print(num,"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
   
                fg=1
        if(flag==2):
            p2=client2.recv(4096).decode()
            if(p2=="passwordmatched"):
                client_socket.send("match found in B".encode('utf-8',errors="ignore"))    #notifying to client
                num=0
                #file = open("recv.txt", "wb") 
                while end==0:
                    num+=1
                    RecvData =recvall(client_socket)
                    if len(RecvData)==0:
                        end=1
                        break
                    client2.sendall(RecvData)                   #sending recieved data directly to server_a
                    acknowledgment=recvall2(client2)
                    client_socket.sendall(acknowledgment)
                print(num,"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")

                fg=1
        if(flag==3):
            p3=client3.recv(4096).decode()
            if(p3=="passwordmatched"):
                client_socket.send("match found in C".encode())    #notifying to client
                num=0
                #file = open("recv.txt", "wb") 
                while end==0:
                    num+=1
                    RecvData =recvall(client_socket)
                    if len(RecvData)==0:
                        end=1
                        break
                    client3.sendall(RecvData)                   #sending recieved data directly to server_a
                    acknowledgment=recvall2(client3)
                    client_socket.sendall(acknowledgment) 
                print(num,"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
                fg=1
       # print(fg)
        if(fg==0):
            client_socket.send("wp".encode())


        



while(1):
    client_sock, address = serv.accept()
    client_sock.send(" ** Connection Established ** ".encode())
    print ('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,address[1],)  
    )
    client_handler.start()