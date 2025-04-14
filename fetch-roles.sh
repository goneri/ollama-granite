#!/usr/bin/env bash
ansible-galaxy role search --author geerlingguy|awk '/geerlingguy/ {print $1}'|xargs -n1 ansible-galaxy role install --roles-path roles
