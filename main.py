#!/usr/bin/env python3

from pathlib import Path
from pydantic import BaseModel

from ollama import chat

workspace = Path(".")


class ModelAnswer(BaseModel):
    file_name: str
    final_answer: str | None


from ollama import Client

questions = [
    {
        "role": "user",
        "content": f"What are the roles available in the directory {workspace}?",
    },
    {
        "role": "user",
        "content": "Describe the variables to use to configure the first role in the list, remember that the roles are in the roles/ directory and you can request the file content",
    },
    {
        "role": "user",
        "content": "Describe the variables to use to configure the geerlingguy.redis role, remember that the roles are in the roles/ directory and you can request the file content",
    },
    {
        "role": "user",
        "content": "Describe the variables to use to configure the geerlingguy.docker role, remember that the roles are in the roles/ directory and you can request the file content",
    },
    {
        "role": "user",
        "content": "Prepare a playbook that uses the roles to install redis and docker on a host",
    },
]

question = questions.pop(0)

system = [
    {
        "role": "system",
        "content": "You are an Ansible expert. "
        "In order to understand the user requests, "
        "you use the key `file_name` to ask the name of the file or directory you want "
        "to read. The user will then have to give you the file content. "
        "The paths must me relative and remain inside the user workspace. "
        "Keep the final_answer key set to None.",
        # "Once you've a good understanding of the user context, you can pass it through the final_answer key.",
    },
]

client = Client(
    host="http://localhost:11434",
)


conversation = []

while True:
    response = client.chat(
        model="granite3.2:8b",
        format=ModelAnswer.model_json_schema(),
        messages=system + conversation + [question],
        options={
            "num_ctx": 4096,
        },
    )

    # print(f"response={response}")
    if (
        response.message.role != "assistant"
        or "file_name" not in response.message.content
    ):
        break
    conversation += [
        {"role": response.message.role, "content": response.message.content}
    ]

    model_answer = ModelAnswer.model_validate_json(response.message.content)
    if model_answer.final_answer:
        print("----")
        print(model_answer.final_answer)
        if questions == []:
            exit(0)
        question = questions.pop(0)
        continue

    if not model_answer.file_name:
        break

    requested = workspace / model_answer.file_name
    print(f"filesystem access requested: {requested}")
    if not requested.exists():
        content = f"'{requested}' doesnt exist\n"
    elif requested.is_dir():
        content = f"this is the content of the directory '{requested}':\n"
        for i in requested.iterdir():
            content += f"- {i}\n"
    else:
        content = f"this is the content of the file '{requested}':\n"
        content += requested.read_text()

    conversation.append({"role": "assistant", "content": content})
