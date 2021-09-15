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
        self.code_trans_fail = "554"
        # standard SMTP commands
        self.cmd_helo = "HELO"
        self.cmd_mail_from = "MAIL FROM"
        self.cmd_rcpt_to = "RCPT TO"
        self.cmd_data = "DATA"
        self.cmd_end = "."
        self.cmd_quit = "QUIT"