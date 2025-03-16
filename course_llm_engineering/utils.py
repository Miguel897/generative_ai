import json

from openai import OpenAI


def query_trough_openai(
    user_prompt, model, system_prompt=None, ollama=False, optional_arguments=None
):
    if ollama:
        openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    else:
        openai = OpenAI()

    messages = [{"role": "user", "content": user_prompt}]
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    response = openai.chat.completions.create(
        model=model, messages=messages, **optional_arguments
    )
    result = response.choices[0].message.content
    return json.loads(result)
