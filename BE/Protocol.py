#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SMTP:
    """
    Used for storing SMTP standard codes and standard commands.
    """
    def __init__(self) -> None:
        # standard SMTP codes
        self.code_service_ready = "220"
        self.code_action_ok = "250"
        self.code_mail_input = "354"
        self.code_service_close = "221"
        # standard SMTP commands
        self.cmd_helo = "HELO"
        self.cmd_mail_from = "MAIL FROM"
        self.cmd_rcpt_to = "RCPT TO"
        self.cmd_data = "DATA"
        self.cmd_end = "."
        self.cmd_quit = "QUIT"

class POP3:
    def __init__(self) -> None:
        # standard POP3 commands
        self.cmd_list = "list"
        self.cmd_retr = "retr"
        self.cmd_dele = "dele"
        self.cmd_quit = "quit"
        self.cmd_end = "."
        # standard POP3 responses
        self.resp_ok = "+OK"
        self.resp_err = "-ERR"