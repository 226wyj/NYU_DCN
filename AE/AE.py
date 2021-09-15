#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
from util import parse_address, fetch_data, is_right_state
from Protocol import SMTP

smtp = SMTP()

def send_email_to_be(from_address, to_address, msg):

    # Establish a TCP connection with BE.
    (to_host, to_port) = parse_address(to_address)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((to_host, to_port))

    s.send(("SMTP\r\n").encode())
    send_success = False

    data = s.recv(1024).decode()

    # If 220 service ready, send HELO cmd to BE.
    if is_right_state(data, smtp.code_service_ready):
        helo_msg = ("{} {}\r\n".format(smtp.cmd_helo, from_address)).encode()
        data = fetch_data(s, helo_msg)

        # If 250 action ok, send MAIL FROM cmd to BE.
        if is_right_state(data, smtp.code_action_ok):
            
            from_msg = \
                ("{}: <{}>\r\n".format(smtp.cmd_mail_from, from_address)).encode()
            data = fetch_data(s, from_msg)
            
            # If 250 action ok, send RCPT TO cmd to BE.
            if is_right_state(data, smtp.code_action_ok):
                to_msg = \
                    ("{}: <{}>\r\n".format(smtp.cmd_rcpt_to, to_address)).encode()
                
                data = fetch_data(s, to_msg)
                
                # If 250 action ok, send DATA cmd to BE.
                if is_right_state(data, smtp.code_action_ok):
                    data_msg = ("{}\r\n".format(smtp.cmd_data)).encode()
                    data = fetch_data(s, data_msg)

                    # If 354 email input, send the message to BE.
                    if is_right_state(data, smtp.code_mail_input):
                        s.send(("{}\r\n".format(msg)).encode())
                        time.sleep(0.1)

                        end_msg = ("\r\n{}\r\n".format(smtp.cmd_end)).encode()
                        data = fetch_data(s, end_msg)

                        # If 250 action ok, send QUIT cmd to BE.
                        if is_right_state(data, smtp.code_action_ok):

                            quit_msg = ("{}\r\n".format(smtp.cmd_quit)).encode()
                            data = fetch_data(s, quit_msg)

                            # If 221 sercive close, close the connection with BE.
                            # Then return a success message to AU.
                            if is_right_state(data, smtp.code_service_close):
                                s.close()
                                send_success = True
    return send_success

if __name__ == '__main__':
    ip_address = '0.0.0.0'
    port = 6000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_address, port))
    s.listen(5)
    print("AE Server is running at {}:{}".format(ip_address, port))

    while True:
        (conn, addr) = s.accept()

        # 220 service ready, return standard code to AU
        ready_msg = ("{} {}:{}\r\n".format(smtp.code_service_ready, ip_address, port)).encode()
        data = fetch_data(conn, ready_msg)

        # Receive HELO cmd from AU, then send 250(action ok) standard code to AU.
        if is_right_state(data, smtp.cmd_helo): 

            # 250 action ok
            ok_msg = ("{} Hello AU, pleased to meet you.\r\n".format(smtp.code_action_ok)).encode()
            data = fetch_data(conn, ok_msg)

            # Receive MAIL FROM cmd from AU, then send 250(action ok) standard code to AU.
            if is_right_state(data, smtp.cmd_mail_from):
                from_sever = data.split('<')[1][:-3]
                ok_msg = "{} {} ... Sender OK.\r\n".format(smtp.code_action_ok, from_sever).encode()
                data = fetch_data(conn, ok_msg)

                # Receive RCPT TO cmd from AU, then send 250(action ok) standard code to AU.
                if is_right_state(data, smtp.cmd_rcpt_to): 
                    to_sever = data.split('<')[1][:-3]
                    ok_msg = "{} {} ... Recipient OK\r\n".format(smtp.code_action_ok, to_sever).encode()
                    data = fetch_data(conn, ok_msg)

                    # Receive DATA cmd from AU, then send 354(mail input) standard code to AU.
                    if is_right_state(data, smtp.cmd_data):
                        return_msg = "{} Enter email, end with '.' on a line by itself.\r\n".format(smtp.code_mail_input)
                        conn.send(return_msg.encode())
                        msg = ""
                        # Continously receive email content until read a '.'
                        while True:
                            data = conn.recv(1024).decode()
                            if data == "\r\n{}\r\n".format(smtp.cmd_end):
                                break
                            else:
                                msg += data[:-2]
                        
                        # Accept all contents, send 250(action ok) to AU
                        delivery_msg = "{} Message accepted for delivery\r\n".format(smtp.code_action_ok)
                        conn.send(delivery_msg.encode())
                        data = conn.recv(1024).decode()

                        # Receive QUIT cmd from AU, then send the message to BE.
                        # If BE successfully receives the message, send 221(service close) standard code to AE.
                        # Otherwise, send 554(transmission failed) to AE. 
                        # Then close the connection.
                        if is_right_state(data, smtp.cmd_quit):
                            success = send_email_to_be(from_sever, to_sever, msg)
                            if success:
                                print("AE successfully sent email to BE!")
                                close_msg = "{} AE successfully sent email to BE\r\n".format(smtp.code_service_close)
                                conn.send(close_msg.encode())
                            else:
                                print("AE failed to send email to BE! Please check AE server.")
                                fail_msg = "{} AE failed to send email to BE\r\n".format(smtp.code_trans_fail).encode()
                                conn.send(fail_msg)
                            conn.close()
        