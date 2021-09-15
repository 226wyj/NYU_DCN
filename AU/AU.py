#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import parse_address, fetch_data, parse_request, is_right_state
from flask import Flask, abort
from Protocol import SMTP
import socket
import time

app = Flask(__name__)
smtp = SMTP()


@app.route('/email')
def email():

    # Get IP2:PORT2, IP3:PORT3, and message
    (from_address, to_address, message) = parse_request()
    send_success = False

    print("from = {}".format(from_address))
    print("to = {}".format(to_address))
    print("message = {}".format(message))

    
    if None in (from_address, to_address, message):
        abort(400)
    
    # Divide IP2 and PORT2
    (ip_2, port_2) = parse_address(from_address)

    # TCP Connection.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_2, port_2))

    data = s.recv(1024).decode()

    # Receive 220(service ready) standard code from AE server, then send HELO cmd.
    if is_right_state(data, smtp.code_service_ready):
    
        helo_msg = ("{} {}:{}\r\n".format(smtp.cmd_helo, ip_2, port_2)).encode()
        data = fetch_data(s, helo_msg)
        
        # Receive 250(action ok) standard code from AE server, then send MAIL FROM cmd.
        # MAIL FROM: <IP1:PORT1>\r\n
        if is_right_state(data, smtp.code_action_ok):
            
            from_msg = \
                ("{}: <{}>\r\n".format(smtp.cmd_mail_from, from_address)).encode()
            data = fetch_data(s, from_msg)
            
            # Receive 250(action ok) standard code from AE server, then send RCPT TO cmd.
            # RCPT TO: <IP2:PORT2>\r\n
            if is_right_state(data, smtp.code_action_ok):

                to_msg = \
                    ("{}: <{}>\r\n".format(smtp.cmd_rcpt_to, to_address)).encode()
                data = fetch_data(s, to_msg)

                # Receive 250(action ok), then send DATA cmd.
                # DATA\r\n
                if is_right_state(data, smtp.code_action_ok):
                    data_msg = ("{}\r\n".format(smtp.cmd_data)).encode()
                    data = fetch_data(s, data_msg)
                    
                    # Receive 354(start mail input), then send email content, and ends with '.'
                    if is_right_state(data, smtp.code_mail_input):
                        content_msg = ("{}\r\n".format(message)).encode()
                        s.send(content_msg)
                        time.sleep(0.1)
                        
                        end_msg = ("\r\n{}\r\n".format(smtp.cmd_end)).encode()
                        data = fetch_data(s, end_msg)

                        # Receive 250(action ok) from AE, then send QUIT cmd.
                        if is_right_state(data, "250"):
                            quit_msg = "{}\r\n".format(smtp.cmd_quit).encode()
                            data = fetch_data(s, quit_msg)

                            # Receive 221(service close) from AE, then close connection.
                            if is_right_state(data, smtp.code_service_close):
                                send_success = True
                                print("AE successfully sent email to BE")
                            elif is_right_state(data, smtp.code_trans_fail):
                                print("AE failed to send email to BE.")
                            s.close()
                               
    if send_success:
        return "AU successfully send email from %s to %s" % \
            (from_address, to_address), 200
    else:
        s.close()
        return "AU failed to send email from %s to %s. Please have a check." % \
            (from_address, to_address), 400


if __name__ == '__main__':
    print("AU server is running...")
    app.run(host='0.0.0.0', port=5000, debug=True)