#!/bin/bash
isort .
black -l 100 .
PYTHONDONTWRITEBYTECODE=1 python main.py