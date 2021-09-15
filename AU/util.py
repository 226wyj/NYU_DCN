#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request

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

def parse_request():
    """
    Parse the request arguments and return the three parts.
    
    @return: (from_addr: str, to_addr: str, message: str)
    """
    from_addr = request.args.get('from')
    to_addr = request.args.get('to')
    message = request.args.get('message')
    return (from_addr, to_addr, message)

def is_right_state(data: str, state_code: str) -> bool:
    """
    Define whether the server returns the right state code.

    @return: True/False
    """
    return data.startswith(state_code)