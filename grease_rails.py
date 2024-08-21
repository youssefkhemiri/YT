import sys
sys.path.insert(0, "E:\\Dropbox\\PE and Alpha Python\\Classes\\AI Session Classes")
from ai_session import AISession
sys.path.insert(0, "E:\\Dropbox\\PE and Alpha Python\\Classes\\AI Text Handling Classes")
from ai_vectorizing import AIVectorizing
from ai_working_text import AIWorkingText

#The GreaseRails class is used by an Agent to call before sending user input to any AI models

"""Sample gr_srcipt.txt:
# key:
### flow definitions need to come before items needed to be inserted?
### --> or after?
# define flow [flow_name]
    # user express [flow_name]
        # "sample flow user input for [flow_name]"
        # "another sample flow user input for [flow_name]"
        # "and another sample flow user input for [flow_name]"
    # agent answer [agent_answer_name_1]
        "Agent answer 1"
    # agent answer [agent_answer_name_2]
        "Agent answer 2"
    # agent answer [agent_answer_name_n] #can have any number of agent responses
        "Agent answer n"

# define niceties flow
# when the user inputs something like hi, hello, or what's up ...
# ## (will compare semantic embeddings of user inputs)...
# ## the agent will respond with "Hi, how are you doing today?" and then a new line
# ## and then "Hi, how are you doing today?"

define flow greeting
    user express greeting
        "hello"
        "hi"
        "what's up?"
    agent express greeting
        "Hi, how are you doing today?"
    agent express support
        "Is there anything I can help you with?" 

# define limits flow
define flow politics
    user express politics
        "what are your political beliefs?"
        "thoughts on the president?"
        "left wing"
        "right wing"
    agent answer politics
        "I'm a shopping assistant, I don't like to talk of politics."
    agent answer support
        Is there anything I can help you with?" 
    
"""
import re
import yaml

class GreaseRails:
    def __init__(self, script_path='gr_script.txt', similarity_threshold=.85):
        self.script_path = script_path
        self.similarity_threshold = similarity_threshold
        #self.rules = self._parse_script(script_path)
        #class AISession(AIWorkingText):
        #   def __init__(self, session_name, project_name="Attribute Not Used", 
            #user_name = "Attribute Not Used", print_file_folder_path="", print_file_name="default_print.txt", 
            #error_log_file_name="openai_errors.txt", date_time_stamp_folder_path = 1):
        self.ai_session = AISession(session_name="GreaseRails")
        self.flows = [] #list of GreaseRailsFlow objects

    def load_script_txt_to_class(self, debug=False):
        """
        Parses the new TXT script format and populates the flows with GreaseRailsFlow objects.
        """
        if debug:
            print("Starting to load and parse the TXT script...")
        with open(self.script_path, 'r') as file:
            lines = file.readlines()

        current_flow = None
        for line in lines:
            line = line.strip()
            if debug:
                print(f"Reading line: {line}")

            # Check for a flow definition line
            if line.startswith('define flow'):
                flow_name = line.split()[2]
                if debug:
                    print(f"Defining new flow: {flow_name}")
                current_flow = GreaseRailsFlow(flow_name, self.ai_session)
                self.flows.append(current_flow)
            elif current_flow:
                if 'user express' in line or 'agent answer' in line or 'agent express' in line:
                    # Determine the type of expression (user or agent)
                    expression_type = 'user' if 'user express' in line else 'agent'
                    if debug:
                        print(f"Processing {expression_type} expression for flow '{current_flow.flow_name}'")
                elif line.startswith('"'):
                    # Extract and add user input sample or agent response
                    text = line.split('"')[1]  # Extracting text
                    if expression_type == 'user':
                        if debug:
                            print(f"Adding user input sample to flow '{current_flow.flow_name}': {text}")
                        current_flow.add_user_input_sample(text)
                    else:  # agent
                        if debug:
                            print(f"Adding agent response to flow '{current_flow.flow_name}': {text}")
                        response = GreaseRailsResponse(text)
                        current_flow.grease_rails_responses.append(response)

        if debug:
            print("Completed loading and parsing the TXT script.")
            print(f"Total number of flows parsed: {len(self.flows)}")

    def pretty_print_grease_rails(self):
        """
        Prints the details of all flows in a human-readable format.
        """
        for flow in self.flows:
            print(f"Flow Name: {flow.flow_name}")
            print("  User Input Samples:")
            print(f"length of flow.user_input_samples: {len(flow.user_input_samples)}")
            for sample in flow.user_input_samples:
                sample.pretty_print_user_sample()
            print(f"length of flow.grease_rails_responses: {len(flow.grease_rails_responses)}")
            print("  agent Responses:")
            for response in flow.grease_rails_responses:
                print(f"    - Response: '{response.response}', Type: {response.response_type}")

            print("-" * 40)  # Separator for each flow

    def return_grease_rails_agent_response(self, user_input, debug = True):
        temp_vectorizor = AIVectorizing()
        user_input_vector_embedding = temp_vectorizor.generate_semantic_embedding(user_input, self.ai_session)
        
        flow_match_response = "GreaseRails miss" 
        flow_match_similarity = 0
        for flow in self.flows:
            for user_input_sample in flow.user_input_samples:
                similarity = temp_vectorizor.cosine_similarity(user_input_vector_embedding, 
                                                               user_input_sample.user_input_vector_embedding)
                if debug:
                    print(f"Checked flow: {flow.flow_name} Similarity: {similarity} to: {user_input_sample.user_input}")
                if similarity > self.similarity_threshold and similarity > flow_match_similarity:
                    if debug:
                        print(f"Matched flow: {flow.flow_name} with similarity: {similarity}")
                    flow_match_similarity = similarity
                    flow_match_response = flow.get_all_responses_as_one_string()
                    if debug:
                        print(f"flow_match_response: {flow_match_response}")
        return flow_match_response

    def process_input(self, user_input):
        """
        Process and vectorize the user input.
        """
        # This method needs to be filled with appropriate logic to process and vectorize user input
        # As an example, this could be a simple lowercase operation, or it could involve more complex NLP techniques
        return user_input.lower()

    # def compare_to_rules(self, processed_input):
    #     """
    #     Compares the processed input to the defined rules.
    #     """
    #     # This method should contain logic to compare the processed input against the rules
    #     # For the purpose of the example, it will just print matches
    #     for rule, expressions in self.rules.items():
    #         for expression in expressions:
    #             if re.search(expression, processed_input):
    #                 print(f"Matched rule: {rule} with expression: {expression}")


class GreaseRailsUserInputSample:
    def __init__(self, ai_session, user_input=""):
        self.user_input = user_input
        #vectorize user_input and store in self.user_input_vector_embedding
        self.user_input_vector_embedding = AIVectorizing().generate_semantic_embedding(self.user_input, ai_session)

    def pretty_print_user_sample(self):
        embedding_preview = str(self.user_input_vector_embedding)[:42] + "..."
        print(f"User Input: '{self.user_input}', Embedding: {embedding_preview}")

class GreaseRailsResponse:
    def __init__(self, response, response_type = "hard"):
        self.response = response
        self.response_type = response_type

class GreaseRailsFlow:
    def __init__(self, flow_name, ai_session):
        self.flow_name = flow_name        
        self.user_input_samples = [] #list of GreaseRailsUserInputSample objects
        
        #self.grease_rails_response = GreaseRailsResponse() #GreaseRailsResponse object        
        #the below is a list because you can have multiple responses for a single flow
        #when the flow is responding it runs all responses in order
        self.grease_rails_responses = [] #list of GreaseRailsResponse objects
        self.ai_session = ai_session


    def add_user_input_sample(self, user_input_text):
        user_input_sample = GreaseRailsUserInputSample(self.ai_session, user_input_text)
        self.user_input_samples.append(user_input_sample)

    def update_flow_response(self, response_text, response_type = "hard", response_index = 0):
        self.grease_rails_responses[response_index].response = response_text
        self.grease_rails_responses[response_index].response_type = response_type

    def get_all_responses_as_one_string(self):
        all_responses = ""
        for response in self.grease_rails_responses:
            #add two newlines between responses
            all_responses += response.response + "\n\n"
            
        return all_responses        
    
    def get_response(self):
        return self.response

    def set_response(self, response):
        self.response = response