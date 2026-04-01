import sys

class MyException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_error(error_message, error_detail)

    def get_detailed_error(self, error_message, error_detail: sys):
        _, _, exc_tb = error_detail.exc_info()

        while exc_tb.tb_next is not None:
            exc_tb = exc_tb.tb_next

        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno

        return f"Error in [{file_name}] at line [{line_number}] : {error_message}"
    
    def __str__(self):
        return str(self.error_message)   # ✅ always string