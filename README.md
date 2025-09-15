# Word Multiplier Simulation (Booth's Algorithm) with Pygame UI

## Setup
1. Create a virtualenv (optional but recommended):
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

2. Install requirements:
   pip install -r requirements.txt

## Run
python gui.py

## Usage (GUI)
- Enter multiplicand and multiplier as decimal integers (signed allowed).
- Select bit width (8, 16, 32) using the dropdown.
- Click "Reset" to apply inputs.
- Click "Step" to run one Booth iteration (visualizes ADD/SUB/None).
- Click "Run" to complete the algorithm.
- The final product (signed and unsigned) is shown.

This simulates registers A (n bits), Q (n bits), Q-1 (1 bit) and performs Booth's algorithm for `n` iterations.

