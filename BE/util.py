#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import os

def save_emails(file_path, emails):
    with open(file_path, 'wb') as f:
        pickle.dump(emails, f)


def read_emails(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data
    else:
        return []

def fetch_data(s, send_msg):
    """
    s is a socket object, s will send the send_msg to 
    target server, and then return the received message.
    
    @return: str
    """
    s.send(send_msg)
    return s.recv(1024).decode()

def is_right_state(data: str, state_code: str) -> bool:
    """
    Define whether the server returns the right state code.

    @return: True/False
    """
    return data.startswith(state_code)

def is_right_cmd(data: str, cmd: str) -> bool:
    return data == cmd