#!/usr/bin/env python
# -*- coding: utf-8 -*-

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