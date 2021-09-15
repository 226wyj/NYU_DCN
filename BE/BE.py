#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
from util import save_emails, read_emails, fetch_data, is_right_state, is_right_cmd 
from Protocol import SMTP, POP3

FILE_PATH = "emails"
smtp = SMTP()
pop3 = POP3()


def receive_email_from_ae(conn, host, port):
    '''
    Using SMTP to receive email from AE server.
    '''
    # 220 service ready
    ready_msg = "{} BE is running at {}:{}\r\n".format(smtp.code_service_ready, host, port).encode()
    data = fetch_data(conn, ready_msg)
    
    # Receive HELO cmd from AE, then send 250.
    if is_right_state(data, smtp.cmd_helo):
        ae_address = data.split(' ')[1][:-2]
        ok_msg = "{} Hello {}, pleased to meet you\r\n".format(smtp.code_action_ok, ae_address).encode()
        data = fetch_data(conn, ok_msg)

        # Receive MAIL FROM cmd from AE, then send 250.
        if is_right_state(data, smtp.cmd_mail_from):
            from_server = data.split('<')[1][:-3] 
            ok_msg = "{} {} ... Sender ok".format(smtp.code_action_ok, from_server).encode()
            data = fetch_data(conn, ok_msg)
            
            # Receive RCPT TO cmd from AE, then send 250.
            if is_right_state(data, smtp.cmd_rcpt_to):
                to_server = data.split('<')[1][:-3]
                ok_msg = "{} {} ... Recipient ok".format(smtp.code_action_ok, to_server).encode()
                data = fetch_data(conn, ok_msg)
                
                # Receive DATA cmd from AE, then send 354.
                if is_right_state(data, smtp.cmd_data):
                    
                    input_msg = "{} Enter email, end with '.' on a line by itself\r\n" \
                        .format(smtp.code_mail_input).encode()

                    conn.send(input_msg)
                    msg = ""
                    while True:
                        data = conn.recv(1024).decode()
                        if data == "\r\n{}\r\n".format(smtp.cmd_end):
                            break
                        else:
                            msg += data[:-2]
                    
                    ok_msg = "{} Message accepted for delivery".format(smtp.code_action_ok).encode()
                    data = fetch_data(conn, ok_msg)
                    
                    # Receive QUIT cmd, then send 221.
                    if is_right_state(data, smtp.cmd_quit):
                        close_msg = "{} BE closing connection".format(smtp.code_service_close).encode()
                        conn.send(close_msg)
                        print("Received -> from <{}> to <{}>".format(from_server, to_server))
                        print("Message: {}".format(msg))

                        # Save the message to a local file.
                        emails = read_emails(FILE_PATH)
                        emails.append((from_server, to_server, msg))
                        save_emails(FILE_PATH, emails)
                        conn.close()

def send_email_to_bu(conn):
    '''
    Using POP3 to send email to BU server.
    '''
    POP3_END = "\r\n{}\r\n".format(pop3.cmd_end)
    POP3_ERR = "{}\r\n".format(pop3.resp_err)
    POP3_OK = "{}\r\n".format(pop3.resp_ok)

    conn.send(POP3_OK.encode())

    emails = read_emails(FILE_PATH)
    delete_index = set()
    while True:
        data = conn.recv(1024).decode()
        cmd = data[:-2]
        print("receive cmd: {}".format(cmd))
        
        # list
        if is_right_cmd(cmd, pop3.cmd_list):
            for i, email in enumerate(emails):
                conn.send("{} {}\r\n".format(i, email[0]).encode())
                time.sleep(0.05)
            
            conn.send(POP3_END.encode())

        # retr
        elif is_right_state(cmd, pop3.cmd_retr):

            cmd_splits = cmd.split(" ")
            if len(cmd_splits) == 1:
                conn.send("")
                conn.send(POP3_ERR.encode())
                continue
            index = cmd.split(" ")[1]
            if not index.isnumeric():
                conn.send(POP3_ERR.encode())
                continue
            index = int(index)
            if index < 0 or index >= len(emails):
                
                conn.send(POP3_ERR.encode())
                continue
            email = emails[index]
            msg = email[2]
            conn.send("{}\r\n".format(msg).encode())
            time.sleep(0.05)

            conn.send(POP3_END.encode())
        
        # dele
        elif is_right_state(cmd, pop3.cmd_dele):
            cmd_splits = cmd.split(" ")
            if len(cmd_splits) == 1:
                conn.send(POP3_ERR.encode())
                continue
            index = cmd.split(" ")[1]
            if not index.isnumeric():
                conn.send(POP3_ERR.encode())
                continue
            index = int(index)
            if index < 0 or index >= len(emails):
                conn.send(POP3_ERR.encode())
                continue
            delete_index.add(index)
            conn.send(POP3_OK.encode())
        
        # quit
        elif is_right_cmd(cmd, pop3.cmd_quit):
            ok_msg = "{} POP3 server signing off".format(POP3_OK)
            conn.send(ok_msg.encode())
            conn.close()
            to_delete = list(delete_index)
            to_delete.sort(reverse=True)
            for i in to_delete:
                del emails[i]
            save_emails(FILE_PATH, emails)
            break
        else:
            conn.send(POP3_ERR.encode())


if __name__ == '__main__':
    ip_3 = '0.0.0.0'
    port_3 = 7000
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_3, port_3))
    s.listen(5)
    print("BE server is running at {}:{}...".format(ip_3, port_3))

    POP3_ERR = "{}\r\n".format(pop3.resp_err)

    print("Server start at {}:{}".format(ip_3, port_3))
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024).decode()
        print("\nProtocal: {}".format(data[:-2]))

        if data[:-2] == 'SMTP':
            receive_email_from_ae(conn, ip_3, port_3)
        elif data[:-2] == "POP3":
            send_email_to_bu(conn)
        else:
            print("Sorry, you can only use SMTP or POP3.")
            conn.send(POP3_ERR.encode())
            conn.close()
            break