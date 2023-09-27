#!/bin/bash

delay=5
command='python main.py'

log() {
    echo -e "\e[35m[\e[33m$(date +%d/%m/%Y-%T)\e[35m]\e[37m $@"; 
}

while true;
do 
    log $command;
    eval "$command";
    stat=$?;
    log "Exit code $stat. Restarting in $delay seconds."
    sleep $delay;
done
