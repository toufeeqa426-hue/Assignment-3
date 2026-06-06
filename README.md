# Multithreaded Grade Processor
Implements multithreading in Python for concurrent student grade processing.

## Features
- 4 worker threads using threading.Thread
- Thread-safe writes using threading.Lock()
- Progress monitoring via queue.Queue()
- ~4x speedup over sequential processing

## How to Run
python multithreaded_grade_processor.py
