#!/bin/bash

NOW=$(date +"%m-%d-%Y_%r")
echo "New session: $NOW" >> src/smartnotifysms.log
echo "Starting SmartNotify SMS Discord Bot..."
nohup python3 src/SMS.py >> src/smartnotifysms.log &
echo "Log located at: src/smartnotifysms.log"
echo "Running"
