#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, abort
from util import parse_address, fetch_data
from Protocol import POP3
import socket
import json

app = Flask(__name__)
pop3 = POP3()

@app.route('/email')
def email():
    from_sever = request.args.get('from')
    (ip_3, port_3) = parse_address(from_sever)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_3, port_3))

    pop3_msg = ("POP3\r\n").encode()
    data = fetch_data(s, pop3_msg)

    # list
    if data[:-2] == pop3.resp_ok:
        s.send("{}\r\n".format(pop3.cmd_list).encode())
        
        email_indexes = []
        while True:
            msg = s.recv(1024).decode()
            if msg == "\r\n{}\r\n".format(pop3.cmd_end):
                break
            index = msg.split(' ')[0]
            email_indexes.append(int(index))

        # retr index
        email_msgs = []
        for index in email_indexes:
            s.send(("{} {}\r\n".format(pop3.cmd_retr, index)).encode())
            message = ""
            while True:
                data = s.recv(1024).decode()
                if data == "\r\n{}\r\n".format(pop3.cmd_end):
                    break
                message += data[:-2]
            email_msgs.append(message)
        
        s.send("{}\r\n".format(pop3.cmd_quit).encode())
        s.close()
        return json.dumps(email_msgs)
    else:
        s.close()
        abort(400)

if __name__ == '__main__':
    print("BU server is running...")
    app.run(host='0.0.0.0', port=53533, debug=True)