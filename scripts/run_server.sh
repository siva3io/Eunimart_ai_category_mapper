#!/bin/bash

cd /home/ubuntu/service_repo    #relace service_repowith  your repo name 

git stash

git pull origin master

python3 serve.py



