import re

import requests
from openai import OpenAI

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
# MODEL = "deepseek-r1:1.5b"
MODEL = "ollama run gemma3:4b"
MESSAGE = [
    {
        "role": "user",
        "content": "Describe some of the business applications of Generative AI",
    }
]


def request_query_method():
    payload = {"model": MODEL, "messages": MESSAGE, "stream": False}

    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)

    parsed_response = response.json()
    message_content = parsed_response["message"]["content"]
    thinking_message = None
    thinking_match = re.search(
        r"<think>([\s\S]*?)</think>", message_content
    )  # consider r"<think>(.*?)</think>"
    if thinking_match:
        thinking_message = thinking_match.group(1)
    final_message = None
    final_message_match = re.search(r"</think>([\s\S]*?)$", message_content)
    if final_message_match:
        final_message = final_message_match.group(1)
    print("Thinking process:", thinking_message, sep="\n")
    print("Final message:", final_message, sep="\n")
    pass


def open_ai_query_method():
    ollama_via_openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    response = ollama_via_openai.chat.completions.create(model=MODEL, messages=MESSAGE)

    print(response.choices[0].message.content)


if __name__ == "__main__":
    # request_query_method()
    open_ai_query_method()
