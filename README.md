# Example of an agent that interact with Granite and gives access to the local file system

In this example, we have a bit more than 100 roles in the `roles/` directory.
We want to generate an Ansible playbook that will use the right roles to answer a user request.

During this example, we ask the model a series of questions in order to get it in the right direction and populate the context in a meaningful way.

At the end, we ask it to generate the Playbook.

[![asciicast](https://asciinema.org/a/QHQcSSeVUr3Za4FvpqKaGWngy.svg)](https://asciinema.org/a/QHQcSSeVUr3Za4FvpqKaGWngy)
