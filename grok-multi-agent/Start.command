#!/bin/bash
cd "$(dirname "$0")"
.venv/bin/python main.py "$@"
echo
read -r -p "Enter drücken zum Schließen..."
