import requests

def youtube_agent_api(query, url = "http://54.144.77.43/ask/"):

    url = "http://localhost:8000/ask/"

    data = {"query": query}

    response = requests.post(url, json=data)

    return response


# Example usage
if __name__ == "__main__":
    #query_text = "name the people in this video https://www.youtube.com/watch?v=qYI1SY9Qyqc"
    query_text = "give me keypoints https://www.youtube.com/watch?v=g3CvsPAF3_0"
    query_text = "who is the winner of champions league 2023 https://www.youtube.com/watch?v=LNzz92Aqzuw"

    response = youtube_agent_api(query_text)

    # print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
