import re

import requests
from openai import OpenAI

OLLAMA_API = "http://localhost:11434/api/chat"


def request_query_method(message, model):
    headers = {"Content-Type": "application/json"}
    payload = {"model": model, "messages": message, "stream": False}

    response = requests.post(OLLAMA_API, json=payload, headers=headers)

    parsed_response = response.json()
    message_content = parsed_response["message"]["content"]

    # Distinguish thinking from final answer in Deepseek-R1
    if "<think>" in message_content:
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
    else:
        print("Response:", message_content, sep="\n")


def open_ai_query_method(message, model):
    ollama_via_openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    response = ollama_via_openai.chat.completions.create(model=model, messages=message)

    print(response.choices[0].message.content)


if __name__ == "__main__":
    print("Querying through Request:")
    llm = "deepseek-r1:1.5b"
    query = [
        {
            "role": "user",
            "content": "Describe some of the business applications of Generative AI",
        }
    ]
    print(f"Querying model {llm} ...")
    request_query_method(query, llm)

    print("Querying through OpenAI package:")
    llm = "gemma3:4b"
    query = [
        {
            "role": "user",
            "content": "Describe some of the business applications of Generative AI",
        }
    ]
    print(f"Querying model {llm} ...")
    open_ai_query_method(query, llm)
