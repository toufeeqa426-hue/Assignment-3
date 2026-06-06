"""
Multithreaded Student Grade Processor
FYP / Semester Project Feature
Demonstrates threading for concurrent data processing
Compatible with Jupyter Notebook / Google Colab
"""

import threading
import time
import random
import statistics
from datetime import datetime

# ─── Shared Data Structures ──────────────────────────────────────────────────
results_lock   = threading.Lock()
processed_results = {}
progress_count = [0]          # list so threads can mutate it via closure

# ─── Simulated Student Dataset ───────────────────────────────────────────────
def generate_students(n=20):
    subjects = ["Math", "Physics", "CS", "English", "Chemistry"]
    students = []
    for i in range(1, n + 1):
        students.append({
            "id"    : f"STU{i:03d}",
            "name"  : f"Student_{i}",
            "grades": {subj: random.randint(45, 100) for subj in subjects}
        })
    return students

# ─── Grade Helper ─────────────────────────────────────────────────────────────
def grade_letter(avg):
    if avg >= 90: return "A+"
    if avg >= 80: return "A"
    if avg >= 70: return "B"
    if avg >= 60: return "C"
    if avg >= 50: return "D"
    return "F"

# ─── Worker Function (runs in each thread) ───────────────────────────────────
def process_student_batch(batch, thread_id, total_students):
    """Each thread processes its assigned batch of students concurrently."""
    thread_name = f"Thread-{thread_id}"
    print(f"  [{thread_name}] Starting — {len(batch)} students assigned")

    for student in batch:
        # Simulate processing delay (e.g. DB lookup, ML scoring)
        time.sleep(random.uniform(0.05, 0.15))

        grades   = list(student["grades"].values())
        avg      = round(statistics.mean(grades), 2)
        analysis = {
            "name"   : student["name"],
            "avg"    : avg,
            "highest": max(grades),
            "lowest" : min(grades),
            "grade"  : grade_letter(avg),
            "status" : "Pass" if avg >= 50 else "Fail",
        }

        # ── Thread-safe write to shared dict ─────────────────
        with results_lock:
            processed_results[student["id"]] = analysis
            progress_count[0] += 1
            done  = progress_count[0]
            filled = done * 20 // total_students
            bar   = "█" * filled + "░" * (20 - filled)
            print(f"  Progress: [{bar}] {done}/{total_students}", flush=True)

    print(f"  [{thread_name}] Done ✓")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    NUM_THREADS  = 4
    NUM_STUDENTS = 20

    # Reset shared state (important when re-running in Jupyter)
    processed_results.clear()
    progress_count[0] = 0

    print("=" * 55)
    print("  Multithreaded Student Grade Processor")
    print(f"  Threads: {NUM_THREADS}  |  Students: {NUM_STUDENTS}")
    print("=" * 55)

    students = generate_students(NUM_STUDENTS)
    # Partition students across threads (round-robin)
    batches  = [students[i::NUM_THREADS] for i in range(NUM_THREADS)]

    # ── Sequential Baseline ──────────────────────────────────
    print("\n[1] Sequential Processing (baseline)...")
    seq_start = time.time()
    for student in students:
        time.sleep(random.uniform(0.05, 0.15))   # simulate same work
    seq_time = time.time() - seq_start
    print(f"    Sequential time : {seq_time:.2f}s")

    # ── Multithreaded Processing ─────────────────────────────
    print(f"\n[2] Multithreaded Processing ({NUM_THREADS} threads)...")
    threads  = []
    mt_start = time.time()

    for i, batch in enumerate(batches):
        t = threading.Thread(
            target=process_student_batch,
            args=(batch, i + 1, NUM_STUDENTS),
            name=f"Worker-{i+1}"
        )
        threads.append(t)
        t.start()

    # Wait for all worker threads to finish
    for t in threads:
        t.join()

    mt_time = time.time() - mt_start

    # ── Results Summary ──────────────────────────────────────
    print("\n" + "=" * 55)
    print("  RESULTS SUMMARY")
    print("=" * 55)
    print(f"  {'ID':<10} {'Name':<14} {'Avg':>6} {'Grade':>6} {'Status'}")
    print("  " + "-" * 50)

    for sid, data in sorted(processed_results.items()):
        print(f"  {sid:<10} {data['name']:<14} "
              f"{data['avg']:>6}  {data['grade']:>5}  {data['status']}")

    avgs   = [d["avg"] for d in processed_results.values()]
    passes = sum(1 for d in processed_results.values() if d["status"] == "Pass")

    print("\n" + "=" * 55)
    print(f"  Class Average : {statistics.mean(avgs):.2f}")
    print(f"  Pass Rate     : {passes}/{NUM_STUDENTS} "
          f"({passes/NUM_STUDENTS*100:.0f}%)")
    print(f"  Sequential    : {seq_time:.2f}s")
    print(f"  Multithreaded : {mt_time:.2f}s")
    print(f"  Speedup       : {seq_time/mt_time:.2f}x faster")
    print("=" * 55)
    print(f"\n  Completed at {datetime.now().strftime('%H:%M:%S')}")

main()
