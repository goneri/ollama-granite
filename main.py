#!/usr/bin/env python3

from pathlib import Path
from pydantic import BaseModel

from ollama import chat

workspace = Path("/var/home/goneri/git_repos/wisdom/ansible-cline-mcp/workspace")


class ModelAnswer(BaseModel):
    file_name: str
    final_answer: str|None

from ollama import Client

question = [
     {
        "role": "user",
        "content": f"What are the roles available in the directory {workspace}?",
    },

]

messages = [
    {
        "role": "system",
        "content": "You are an Ansible expert. "
        "In order to understand the user requests, "
        "you use the key `file_name` to ask the name of the file or directory you want "
        "to read. The user will then have to give you the file content. "
        "The paths must me relative and remain inside the user workspace. "
        "Keep the final_answer key set to None."
        #"Once you've a good understanding of the user context, you can pass it through the final_answer key.",
    },
]


client = Client(
    host="http://localhost:11434",
)
response = client.chat(
    model="granite3.2:8b",
    format=ModelAnswer.model_json_schema(),
    messages=messages + question,
    options={
        "num_ctx": 4096,
    })
while response:
    print(f"response={response}")
    if response.message.role != "assistant" or "file_name" not in response.message.content:
        break

    model_answer = ModelAnswer.model_validate_json(response.message.content)
    if model_answer.final_answer:
        print(model_answer.final_answer)
        break
    if not model_answer.file_name:
        break


    requested = workspace / model_answer.file_name
    print(f"requested: {requested}")
    if not requested.exists():
        content = f"'{requested}' doesnt exist\n"
    elif requested.is_dir():
        content = f"this is the content of the directory '{requested}':\n"
        for i in requested.iterdir():
            content += f"- {i}\n"
    else:
        content = f"this is the content of the file '{requested}':\n"
        content += requested.read_text()

    messages.append({"role": "assistant", "content": content})
    from pprint import pprint
    pprint(messages)
    response = client.chat(
        model="granite3.2:8b",
        format=ModelAnswer.model_json_schema(),
        messages=messages + question,
        options={
            "num_ctx": 4096,
        })
