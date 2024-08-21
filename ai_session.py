import time
import sys
sys.path.insert(0, "E:\\Dropbox\\PE and Alpha Python\\Classes\\AI Text Handling Classes")
from ai_working_text import AIWorkingText
from datetime import datetime
import os
import pickle

class AISession(AIWorkingText):
    def __init__(self, session_name, project_name="Attribute Not Used", user_name = "Attribute Not Used", print_file_folder_path="", print_file_name="default_print.txt", error_log_file_name="openai_errors.txt", date_time_stamp_folder_path = 1):
        super().__init__()
        self.session_name = session_name
        self.project_name = project_name
        self.user_name = user_name
        self.total_money_spent = 0
        self.open_ai_error_log_file_name = error_log_file_name
        self.print_file_folder_path = print_file_folder_path
        self.print_file_name = print_file_name
        self.start_time = time.time()
        self.date_time = datetime.now().strftime('%Y_%m_%d___%H_%M_%S')
        if date_time_stamp_folder_path:
            self.print_file_folder_path = os.path.join(self.print_file_folder_path, self.date_time)
        if not os.path.exists(self.print_file_folder_path):
            # os.makedirs(self.print_file_folder_path)      
            pass  
        self.print_file_path = os.path.join(self.print_file_folder_path, self.print_file_name)        
        self.runtime = "--- %.2f minutes ---" % ((time.time() - self.start_time) / 60)
        self.total_variations_count = 0
        log_general_input = f"----> BEGIN RUN -- Date_Time: {self.date_time}, session_name: {session_name}"
        self.log_general(log_general_input)

    def __str__(self):
        return f"Session Name: {self.session_name}, Date_Time: {self.date_time}, Runtime: {self.runtime}, Total Money Spent: {self.total_money_spent}, Total Variations: {self.total_variations_count}"
    
    def log(self, message):
        print(f"[AISession Log]: {message}")

    def log_end_session(self, document_name=""):
        self.runtime_update()
        log_general_input = f"END RUN -- Date_Time: {self.date_time}, self.document_name: {document_name}, total_money_spent: {self.total_money_spent}, Runtime: {self.runtime}; Variation Number: {self.total_variations_count}"
        self.log_general(log_general_input)

    def add_to_total_cost_from_string(self, texty, llm="gpt-3.5-turbo-16k", is_input=True):
        num_tokens = super().num_tokens_from_string(texty)
        cost_to_add = self.cost_of_tokens(num_tokens, llm, is_input)
        self.total_money_spent += cost_to_add
        return cost_to_add

    def cost_of_tokens(self, token_count, llm="gpt-3.5-turbo-16k", is_input=True):
        costs = {
            "gpt-3.5-turbo-16k": {True: token_count * .003 / 1000, False: token_count * .004 / 1000},
            "gpt-4-0613": {True: token_count * .03 / 1000, False: token_count * .06 / 1000},
            "gpt-4": {True: token_count * .03 / 1000, False: token_count * .06 / 1000},
            "text-embedding-ada-002": {True: token_count * .0001 / 1000, False: token_count * .0001 / 1000}
        }
        return costs.get(llm, {}).get(is_input, 0)

    def log_openai_error(self, error_msg):
        current_datetime = datetime.now()
        text_datetime = current_datetime.strftime("%Y-%m-%d, %H-%M-%S")
        log_text = f"{text_datetime}, {os.path.basename(__file__)} ==> {error_msg}\n----------------------\n"
        # Assuming log_errors is a function somewhere in your code or you can replace this with your own logging mechanism
        self.print_to_file(f"OpenAI Error: {log_text}", "open_ai_errors_log.txt")
        # with open(self.open_ai_error_log_file_name, "a", encoding="utf-8") as f:
        #     f.write(log_text)

    def print_to_file(self, string, file_path=None, retries=2, delay=1):
        # #print(f"1 -- Printing to file_path: {file_path}")
        # if not file_path:
        #     file_path = self.print_file_path
        #     #print(f"1.5 -- Printing to self.print_file_path: {self.print_file_path}")        
        # string = f"{string}\n\n"
        # #print(f"2 -- Printing to file_path: {file_path}")
        
        # for _ in range(retries):
        #     try:
        #         with open(file_path, "a", encoding="utf-8") as log_file:
        #             log_file.write(string)
        #             #print(f"File path successfully written: {file_path}")
        #             return
        #     except PermissionError as e:
        #         print(f"Permission denied: Cannot write to {file_path}. Retrying...")
        #         print(f"Error details: {e}")
        #         time.sleep(delay)
        #     except Exception as e:
        #         print(f"Error writing to {file_path}. Error message: {e}")
        #         return
        # print(f"Failed to write to {file_path} after {retries} retries.")
        pass

    def date_time_update(self):
        self.date_time = datetime.now().strftime('%Y_%m_%d___%H_%M_%S')

    def runtime_update(self):
        self.runtime = "--- %.2f minutes ---" % (
            (time.time() - self.start_time) / 60)
    def save_ai_session_to_file(self, file_path):
        try:
            with open(file_path, 'wb') as file:
                pickle.dump(self, file)
            self.print_to_file(f"AISession successfully saved to {file_path}.")
        except Exception as e:
            print(f"Failed to save AISession to {file_path}. Error message: {e}")
            self.log_openai_error(f"Failed to save AISession to {file_path}. Error: {e}")

    def log_general(self, string_to_log, sub_folder_path=""):
        
        final_folder_path = self.print_file_folder_path
        if sub_folder_path != "":
            final_folder_path = os.path.join(final_folder_path, sub_folder_path)
        general_log_file_name = "Log General.txt"
        general_log_full_file_path = os.path.join(final_folder_path, general_log_file_name)
        string_to_log = "LOG_GENERAL: \n" + string_to_log
        #with open(general_log_full_file_path, "a", encoding="utf-8") as log_file:
        #    log_file.write(string_to_log + "\n")
        self.print_to_file(string_to_log, general_log_full_file_path)
    
    @staticmethod
    def load_ai_session_from_file(file_path):
        try:
            with open(file_path, 'rb') as file:
                loaded_session = pickle.load(file)
            return loaded_session
        except Exception as e:
            print(f"Failed to load AISession from {file_path}. Error message: {e}")
            # Assuming log_errors is defined or replace it with an appropriate logging method
            # log_errors(f"Failed to load AISession from {file_path}. Error: {e}")
            #   
    
    def print_runtime(self):
	    self.print_to_file("--- %.2f minutes ---" % ((time.time() - self.start_time) / 60))
