import os
import tiktoken
from bs4 import BeautifulSoup
#import sys
#sys.path.insert(0, "E:\\Dropbox\\PE and Alpha Python\\Classes\\Prompt Stack Classes")
#from prompt_stack import PromptStack

class AIWorkingText:
    def __init__(self, max_chunk_tokens=1000, chunk_tokens_overlap=50, max_no_chunk_size=3000):
        #self.tokenizer = Tokenizer()  # Initialising the Tokenizer from tiktoken
        self.tokenizer_encoding = tiktoken.get_encoding("cl100k_base")
        self.max_chunk_tokens = max_chunk_tokens
        self.chunk_tokens_overlap = chunk_tokens_overlap
        self.max_no_chunk_size = max_no_chunk_size
        self.document_paragraphs_as_chunks = []

    def num_tokens_from_string(self, string_input):
        return len(self.tokenizer_encoding.encode(string_input))

    def join_relevant_snippets(self, relevant_snippets):
        stringified_snippets = []
        for item in relevant_snippets:
            if isinstance(item, tuple) or isinstance(item, list):
                # If it's a tuple or list, join its items into a string
                snippet_string = " ".join(map(str, item))
                stringified_snippets.append(snippet_string)
            elif isinstance(item, str):
                # If it's already a string, just append
                stringified_snippets.append(item)
            else:
                # Optionally handle other data types or raise an error if unexpected types are encountered
                raise TypeError(f"Unexpected data type in relevant_snippets: {type(item)}")

        # Now, join all the stringified snippets into one string
        relevant_snippets_as_string = " ".join(stringified_snippets)
        return relevant_snippets_as_string

    def chunk_text_by_paragraphs(self, text):
        paragraphs = text.split('\n\n')
        # Remove leading and trailing whitespace from each paragraph
        paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
        return paragraphs

    def chunk_text_by_sentences(self, text):
        sentences = text.split('.')
        return sentences
    
    def chunk_text_by_multiple_sentences(self, text, num_sentences_per_chunk, sentence_overlap=0):
        sentences = text.split('.')
        chunks = []
        start = 0
        while start < len(sentences):
            end = start + num_sentences_per_chunk
            chunk = " ".join(sentences[start:end])
            chunks.append(chunk)
            start = end - sentence_overlap
        return chunks

    def chunk_html_by_paragraphs(self, html_content, ai_session = None):
        soup = BeautifulSoup(html_content, 'html.parser')
        if ai_session:
            ai_session.print_to_file(f"soup: {soup}")
        # Extracting all paragraphs and heading tags from the parsed HTML content
        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        if ai_session:
            ai_session.print_to_file(f"elements: {elements}")
        # Variable to store combined text of heading and paragraph
        combined_text = ""
        self.document_paragraphs_as_chunks = []
        # Looping through each element and extracting text
        for index, elem in enumerate(elements):
            # Extracting the text from the element
            text = elem.text
            if ai_session:
                ai_session.print_to_file(f"3737 -- text: {text}")
            # If the element is a heading, add the text to the combined_text variable
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if text == "References":
                    break
                combined_text += text + ":\n"
            # If the element is a paragraph, add the text to the combined_text variable and print it
            elif elem.name == 'p':
                combined_text += text
                self.document_paragraphs_as_chunks.append(combined_text)
                #print(f"Chunk {index + 1}:\n{combined_text}\n-------- ooooooooo ---------- oooooooooo --------\n")
                # Resetting the combined_text variable for the next chunk
                if ai_session:
                    ai_session.print_to_file(f"combined_text: {combined_text}")
                combined_text = ""  
        return self.document_paragraphs_as_chunks  
        

    def chunk_text_by_tokens(self, text):
        chunks = []
        start = 0

        while start < len(text):
            if self.num_tokens_from_string(text[start:]) <= self.max_no_chunk_size:
                chunks.append(text[start:])
                break

            low, high = start, len(text)
            while low <= high:
                mid = (low + high) // 2
                segment = text[start:mid]
                token_count = self.num_tokens_from_string(segment)

                if token_count == self.max_chunk_tokens:
                    end = mid
                    break
                elif token_count < self.max_chunk_tokens:
                    low = mid + 1
                else:
                    high = mid - 1
            else:
                end = low

            chunks.append(text[start:end])
            start = end - self.chunk_tokens_overlap

        return chunks
    
    def summarize_text_with_llm(self, text, prompt_stack, ai_session, llm="gpt-3.5-turbo-16k", max_chunk_size=12000, max_summary_length_in_word_count=200, depth=0, max_depth=5):
        if depth >= max_depth:
            return text  # or return the current summarization_text
        num_tokens_in_text = self.num_tokens_from_string(text)
        if num_tokens_in_text > max_chunk_size:
            self.max_chunk_tokens = max_chunk_size
            chunks = self.chunk_text_by_tokens(text)
            print(f"3 -- len(chunks): {len(chunks)}\n")
            summarization_text = ""
            for chunk in chunks:
                #recursively summarize each chunk
                summary = self.summarize_text_with_llm(chunk, ai_session, llm=llm, max_chunk_size=max_chunk_size)
                #add the summary to the summarization_text with a new line character between each
                summarization_text += summary + "\n"            
        else:
            summarization_text = text 
        
        #if word count of summarization_text is greater than max_summary_length_in_word_count, then:
        if len(summarization_text.split()) > max_summary_length_in_word_count:  
            instructions = "Please summarize the following text down to {max_summary_length_in_word_count} words or less:\n\n"
            prompt = instructions + summarization_text
            response = prompt_stack.make_openai_request(ai_session, prompt , def_llm=llm)
            final_summary = prompt_stack.response_to_string(response)
        else:
            final_summary = summarization_text
        
        if len(final_summary.split()) > max_summary_length_in_word_count:
            print(f"4 -- final_summary): {final_summary}\n")
            final_summary = self.summarize_text_with_llm(final_summary, prompt_stack, ai_session, llm=llm, max_chunk_size=max_chunk_size, max_summary_length_in_word_count=max_summary_length_in_word_count, depth=depth+1, max_depth=max_depth)
        return final_summary


    @staticmethod
    def beautiful_html_soup_to_cleaned_html_string(soup):
        for style_tag in soup.find_all('style'):
            style_tag.decompose()

        for tag in soup():
            del tag['style']
            del tag['class']

        return str(soup)

    def html_file_path_to_scrubbed_html_string(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            policy_html_soup = BeautifulSoup(file, 'html.parser')
        return self.beautiful_html_soup_to_cleaned_html_string(policy_html_soup)

    @staticmethod
    def string_array_from_txt_files_in_folder(directory_path):
        string_array = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt"):
                full_file_path = os.path.join(directory_path, filename)
                with open(full_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    string_array.append(content)
        return string_array

    @staticmethod
    def remove_first_three_chars(strings):
        return [s[3:] for s in strings]

    
