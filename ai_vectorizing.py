import os
import numpy as np
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
from openai import OpenAI
from bs4 import BeautifulSoup
from ai_working_text import AIWorkingText
import sys
sys.path.insert(0, "E:\\Dropbox\\PE and Alpha Python\\Classes\\AI Session Classes")
from ai_session import AISession

class AIVectorizing(AIWorkingText):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cosine_similarities = []
        self.total_money_spent = 0
        self.max_chunk_tokens = 6000 #max_embedding_chunk_size_tokens
        self.default_embedding_llm = "text-embedding-ada-002"
        #openai.api_key = os.getenv("OPENAI_API_KEY")
        openai_api_key = ""
        self.openai_client = OpenAI(api_key=openai_api_key)
        #print(f"openai.api_key: {openai.api_key}")

    def sum_embeddings(self, embeddings):
        total_embedding = np.zeros_like(embeddings[0])
        for embedding in embeddings:
            total_embedding += embedding
        return total_embedding

    def average_embeddings(self, embeddings):
        stacked_embeddings = np.vstack(embeddings)
        average_embedding = np.mean(stacked_embeddings, axis=0)
        return average_embedding

    def generate_semantic_embedding(self, text_to_be_embedded, ai_session):
        num_tokens = self.num_tokens_from_string(text_to_be_embedded)
        if num_tokens > self.max_chunk_tokens:
            chunk_embeddings = []
            chunks = self.chunk_text_by_tokens(text_to_be_embedded)
            for chunk in chunks:
                single_chunk_embedding = self.generate_semantic_embedding(chunk, ai_session)
                chunk_embeddings.append(single_chunk_embedding)
            embeddings = self.average_embeddings(chunk_embeddings)
        else:
            response = self.openai_client.embeddings.create(
                input=text_to_be_embedded,
                model=self.default_embedding_llm  # Ensure this is defined elsewhere or passed appropriately
            )
            #embeddings = response['data'][0]['embedding']
            embeddings = response.data[0].embedding
            ai_session.total_money_spent += ai_session.cost_of_tokens(response.usage.total_tokens, self.default_embedding_llm)  # Adjust the method as necessary
        return embeddings

    def cosine_similarity(self, vector1, vector2):
        distance = cosine(vector1, vector2)
        similarity = 1 - distance
        return similarity

    def on_pick(self, event):
        ind = event.ind[0]
        similarity_value = self.cosine_similarities[ind]
        self.print_to_file(f"Index: {ind}, Cosine Similarity: {similarity_value:.3f}")  # Adjust the method as necessary
        plt.title(f"Index: {ind}, Cosine Similarity: {similarity_value:.3f}")

    def display_1d_embeddings(self, embeddings_array, comparison_embedding):
        self.cosine_similarities = [self.cosine_similarity(vector, comparison_embedding) for vector in embeddings_array]
        fig, ax = plt.subplots()
        ax.plot(self.cosine_similarities, 'bo-', picker=True)
        ax.set_title('Cosine Similarities')
        ax.set_xlabel('Index')
        ax.set_ylabel('Similarity Value')
        fig.canvas.mpl_connect('pick_event', self.on_pick)
        plt.show()
        return self.cosine_similarities

    def generate_embeddings_from_directory(self, directory_path):
        embeddings_array = []
        x = 0
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt"):
                full_file_path = os.path.join(directory_path, filename)
                with open(full_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    im_sorry_response = self.is_unable_response(content)  # Adjust the method as necessary
                    x += 1
                    print("ai_vectorizing.generate_embeddings_from_directory")
                    self.print_to_file(f" -------------> Index: {x} <-------------")  # Adjust the method as necessary
                    self.print_to_file(f"Content: {content[:42]}")  # Adjust the method as necessary
                    self.print_to_file(f" -------------> im_sorry_response: {im_sorry_response} <-------------")  # Adjust the method as necessary
                    self.print_to_file(f" -------------> content length: {len(content)} <-------------")  # Adjust the method as necessary
                    embedding = self.generate_semantic_embedding(content)
                    embeddings_array.append(embedding)
        return embeddings_array

