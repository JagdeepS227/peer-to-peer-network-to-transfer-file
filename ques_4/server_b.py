import sys
import socket
import csv
import threading
import struct 
import os


table = open('routing.rtl', 'r')
data = table.readlines()
row = data[1].split('|')
print(row)


auglist=sys.argv
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind((row[1], int(row[2].strip())))
serv.listen(5)
print('********************connection established at port', int(row[2].strip()), 'listning started*************************')
print('\n')


prev_frame_num=0
curr_frame_num=0 

frame_number=1
frame_size=1
prev_frame_num=0
curr_frame_num=1
end=0
num=0


frame = struct.Struct('8s8s2I100000sI')            #struct template for frame out
ack = struct.Struct('2I')                   #struct for ack frame



def handle_client_connection(client_socket,address):     
    from_client = ''


    def recvall(sock):
        BUFF_SIZE=800224
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


    prev_frame_num=0
    curr_frame_num=0 
    while True:
        

        def data_check( frame_in_num , data, checksum_client ,frame_size,m,dd,prev_frame_num,curr_frame_num): #checks data
            #global prev_frame_num , curr_frame_num                             #takes in last accpeted frame number
            # if dd==1:
            #     prev_frame_num=-1
            #     curr_frame_num=1
            # if dd==2:
            #     prev_frame_num=0
            #     curr_frame_num=2
            
            checksum_server = crc161(data,checksum_client)       #generates new checksum
            #print('server = ', checksum_server , 'client = ', checksum_client)
            #print("********",prev_frame_num,"**********",frame_in_num)
            if checksum_server==0 :  #checks for correct frame number and correct checksum
                # prev_frame_num += 2                             #if correct, updates last accpeted frame
                return (1,prev_frame_num)                                      #returns 1 for ack, 0 for nak
            else:
                return (0,prev_frame_num)

        end=0
        data = client_socket.recv(4096).decode()
        print(data, ': username')
        #if not data: break
        from_client = data
        if(from_client=="exit"):
            print("ID" + str(address) + ": " + "Disconected****************************************")    
            #client_socket.close()
        else:
            #client_socket.send(" ** message recieved at server ** ".encode())
            csvfile=open('B.csv','r', newline='')
            obj=csv.reader(csvfile)
            flag=0
            for row in obj:
                if(str(from_client)==str(row[0])):
                    flag=1
            if(flag==1):
                print('User found here')
                client_socket.send("found".encode()) 
            else:
                print("ID" + str(address) + ": " + "Disconected**************************************** ")    
                client_socket.send("notfound".encode())
                exit()
            print("ID" + str(address) + ": " + str(from_client))    

            pswd = client_socket.recv(4096).decode()
            print("password recieved here")
            # client_socket.send(" ** message recieved at server ** ".encode())
            csvfile=open('B.csv','r', newline='')
            obj=csv.reader(csvfile)
            flag2=0


        
            #client_socket.send(" ** message recieved at server ** ".encode())
            for row in obj:
                #print(row[1])
                if(str(pswd)==str(row[1]) and str(from_client)==str(row[0])):
                    flag2=1


            global num        
            if(flag2==1):

                file = open("recvB.txt", "wb") 
                client_socket.sendall("passwordmatched".encode()) 
                while end==0:
                    num+=1
                    print(prev_frame_num,"---------------",curr_frame_num)
                    if prev_frame_num == curr_frame_num:                #update expexted frame number
                        curr_frame_num += 2
                    RecvData =recvall(client_socket)
                    if len(RecvData)==0:
                        end=1
                        break
                    #print(len(RecvData),"Size of packet recieved from client in bytes")
                    addr1,addr2,frame_in_num1,frame_size,data, checksum_client = frame.unpack(RecvData)   #unpack data
                    #print(data)
                    dd=0
                    if frame_in_num1==1:
                        dd=1
                    if frame_in_num1==2:
                        dd=2
                    frame_out_ack,prev_frame_num = data_check(frame_in_num1, data.decode('utf-8',errors="ignore"), checksum_client,frame_size,1,dd,prev_frame_num,curr_frame_num)  
                    if frame_out_ack == 1:    
                        data = data.split(b'\x00', 1)[0]
                        file.write(data)
                    frame_out = ack.pack(curr_frame_num , frame_out_ack)     #pack ack frame
                    client_socket.sendall(frame_out)         # sending acknowledgement
                    
                file.close()


                print("Total Number of transactcion(number of times data came to server--------- )",num)


                # with open("recvC.txt", "r+", encoding = "utf-8") as file:
                #     file.seek(0, os.SEEK_END)
                #     pos = file.tell() - 1
                #     while file.read(1) != '\n' and pos>0:
                #         pos -= 1
                #         file.seek(pos, os.SEEK_SET)
                #     file.seek(pos, os.SEEK_SET)
                #     file.truncate()
                #     file.write('\n')
                # file.close()


                print("ID" + str(address) + ": " + "Disconected** AFTER SUCCESSFULL DATA**************************************")    
                exit()
            else:
                client_socket.send("wp".encode()) 
                print("ID" + str(address) + ": " + "Disconected****************************************")    
                exit()




while True:
    client_sock, address = serv.accept()
    client_sock.send(" ** Connection Established ** ".encode())
    print ('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,address[1],)  
    )
    client_handler.start()