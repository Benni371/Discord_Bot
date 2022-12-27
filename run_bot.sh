#!/usr/bin/bash
pkill -f manager.py && pkill -f commands.py
python3 manager.py &
python3 commands.py &
