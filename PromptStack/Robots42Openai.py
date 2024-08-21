from openai import OpenAI
import time
import tiktoken
from PromptStack.SheetsClass import GoogleSheetsHelper
import os
from datetime import datetime


class Completions:
    def __init__(self, name = None, api_key = None):
        """
        Initialize the model with the necessary API key. Leave empty defaults to os.environ.get("OPENAI_API_KEY")
        """
        self.name = name
        self.helper = GoogleSheetsHelper()

        if api_key is not None:
            self.api_key = api_key
            self.client = OpenAI(api_key = self.api_key)
        else:
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.client = OpenAI()



    def create(self, **kwargs):
        """
        Call the GPT model and save metadata.
        """
        request_datetime = datetime.now()

        print("--one--")
        start_time = time.time()
        response = self.client.chat.completions.create(
            # model=model,
            # messages=messages,
            **kwargs
        )
        end_time = time.time()

        execution_time = end_time - start_time
        print("--PromptStack Executed--")
        try:
            messages = kwargs.get('messages', 'Default')
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            try:
                num_tokens = self.num_tokens_from_messages(messages)
            except:
                num_tokens = None
            model = kwargs.get('model', 'Default')

            print("Time: ", request_datetime)
            print("Num tokens: ", num_tokens)
            print("Execution time (seconds): ", execution_time)

        
            self.save_to_sheet(self.name, model, num_tokens, request_datetime, execution_time, self.api_key[0:8]) # type: ignore
            print("Data saved to the Sheet.")
        except:
            print("Data Not saved to the Sheet.")

        return response
    


    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0613":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    def save_to_sheet(self, name, modelname, tokens, time, executiontime, api=None):
        spreadsheet_id = ""
        range_name = 'Sheet1'  # For example, writing to Sheet1 from A1 to D5
        values = [
            [str(name), str(modelname), str(tokens), str(time), str(executiontime), str(api)],
        ]

        self.helper.add_data_to_sheet(spreadsheet_id, range_name, values)
        



class Chat:
    def __init__(self, name):
        self.completions = Completions(name)

class PromptStack:
    def __init__(self, name = None):
        self.chat = Chat(name)