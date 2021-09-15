#!/usr/bin/env python
# -*- coding: utf-8 -*-

def parse_address(s):
    """
    parse the IP:PORT formed string into 
    ip address and coressponding port.

    @return (ip: str, port: int)
    """
    ip_address = s.split(":")[0]
    port = int(s.split(":")[1])
    return (ip_address, port)


def fetch_data(s, send_msg):
    """
    s is a socket object, s will send the send_msg to 
    target server, and then return the received message.
    
    @return: str
    """
    s.send(send_msg)
    return s.recv(1024).decode()


def is_right_state(data, state_code):
    """
    Define whether the server returns the right state code.

    @return: True/False
    """
    return data.startswith(state_code)
