#!/usr/bin/env python3

import csv
import os
import sys

PASS_MARK = 50.0          
FORMATIVE_TARGET = 60.0    # all formative weights must add up to exactly 60
SUMMATIVE_TARGET = 40.0    # all summative weights must add up to exactly 40
TOTAL_TARGET = 100.0       # all weights must add up to exactly 100
TOLERANCE = 1e-9           # float comparison tolerance

REQUIRED_COLUMNS = ["assignment", "group", "score", "weight"]

GROUP_ALIASES = {
    "formative": "Formative",
    "fa": "Formative",
    "summative": "Summative",
    "sa": "Summative",
}



# 1. Loading the data (starter-template logic, with stronger error messages)

def load_csv_data():
    """Ask the user for a CSV file name, then read and type-convert every row."""
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if not filename:
        filename = "grades.csv"
        print("No file name entered, defaulting to 'grades.csv'.")

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found in {os.getcwd()}.")
        print("Hint: run the script from the folder that contains your CSV file.")
        sys.exit(1)

    if os.path.getsize(filename) == 0:
        print(f"Error: The file '{filename}' is empty.")
        print("Hint: if you just ran organizer.sh, your old grades were archived in ./archive/.")
        sys.exit(1)

    assignments = []
    try:
        with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            # Normalise header names (strip spaces, lower-case)
            if reader.fieldnames is None:
                print(f"Error: '{filename}' has no header row.")
                sys.exit(1)
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

            missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                print(f"Error: '{filename}' is missing the column(s): {', '.join(missing)}")
                print("Expected header example: assignment,group,score,weight")
                sys.exit(1)

            # Row 1 is the header, so data starts on line 2
            for line_number, row in enumerate(reader, start=2):
                if not any((value or "").strip() for value in row.values()):
                    continue  # skip completely blank lines

                assignments.append(parse_row(row, line_number))

    except csv.Error as error:
        print(f"Error: '{filename}' is not a valid CSV file ({error}).")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: '{filename}' could not be read as text. Is it really a CSV file?")
        sys.exit(1)

    if not assignments:
        print(f"Error: '{filename}' contains a header but no assignments.")
        sys.exit(1)

    return assignments


def parse_row(row, line_number):
    """Convert one CSV row into a dictionary with the correct data types."""
    name = (row.get("assignment") or "").strip()
    raw_group = (row.get("group") or "").strip()
    raw_score = (row.get("score") or "").strip()
    raw_weight = (row.get("weight") or "").strip()

    if not name:
        print(f"Error (line {line_number}): assignment name is empty.")
        sys.exit(1)

    group = GROUP_ALIASES.get(raw_group.lower())
    if group is None:
        print(f"Error (line {line_number}): '{name}' has an unknown group '{raw_group}'.")
        print("Use 'Formative' or 'Summative' (e.g., Formative).")
        sys.exit(1)

    try:
        score = float(raw_score)
    except ValueError:
        print(f"Error (line {line_number}): score '{raw_score}' for '{name}' is not a number.")
        print("Use a number between 0 and 100 (e.g., 85 or 72.5).")
        sys.exit(1)

    try:
        weight = float(raw_weight)
    except ValueError:
        print(f"Error (line {line_number}): weight '{raw_weight}' for '{name}' is not a number.")
        print("Use a positive number (e.g., 15).")
        sys.exit(1)

    return {"assignment": name, "group": group, "score": score, "weight": weight}



# 2. Validation

def validate_grades(data):
    """Every score must be within 0-100. Returns a list of error messages."""
    errors = []
    for item in data:
        if not (0 <= item["score"] <= 100):
            errors.append(
                f"'{item['assignment']}' has score {fmt(item['score'])}, "
                "but scores must be between 0 and 100."
            )
    return errors


def validate_weights(data):
    """Total weight = 100, Summative = 40, Formative = 60. Returns error messages."""
    errors = []

    for item in data:
        if item["weight"] <= 0:
            errors.append(f"'{item['assignment']}' has weight {fmt(item['weight'])}; weights must be positive.")

    total = sum(item["weight"] for item in data)
    formative = sum(item["weight"] for item in data if item["group"] == "Formative")
    summative = sum(item["weight"] for item in data if item["group"] == "Summative")

    if abs(total - TOTAL_TARGET) > TOLERANCE:
        errors.append(f"Total weight is {fmt(total)}, but it must be exactly {fmt(TOTAL_TARGET)}.")
    if abs(formative - FORMATIVE_TARGET) > TOLERANCE:
        errors.append(f"Formative weights add up to {fmt(formative)}, but must be exactly {fmt(FORMATIVE_TARGET)}.")
    if abs(summative - SUMMATIVE_TARGET) > TOLERANCE:
        errors.append(f"Summative weights add up to {fmt(summative)}, but must be exactly {fmt(SUMMATIVE_TARGET)}.")

    return errors



# 3. Calculations

def weighted_score(item):
    """Final weight of one assignment = (grade * weight) / 100."""
    return item["score"] * item["weight"] / 100


def category_total(data, group):
    return sum(weighted_score(item) for item in data if item["group"] == group)


def calculate_gpa(total_grade):
    """GPA = (Total Grade / 100) * 5.0"""
    return (total_grade / 100) * 5.0


def find_resubmissions(data):
    """
    Failed formative assignments (score < 50) that carry the HIGHEST weight
    among the failed formatives. Ties are all returned.
    """
    failed_formatives = [
        item for item in data
        if item["group"] == "Formative" and item["score"] < PASS_MARK
    ]
    if not failed_formatives:
        return []

    highest_weight = max(item["weight"] for item in failed_formatives)
    return [item for item in failed_formatives if abs(item["weight"] - highest_weight) <= TOLERANCE]



# 4. Report

def fmt(number):
    """Print 30.0 as 30 and 6.75 as 6.75 (matches the transcript layout)."""
    return f"{number:.4f}".rstrip("0").rstrip(".")


def evaluate_grades(data):
    print("\n--- Processing Grades ---")

    # Validation first: stop with clear messages if the data is wrong
    grade_errors = validate_grades(data)
    weight_errors = validate_weights(data)

    if grade_errors or weight_errors:
        print("\nValidation FAILED. Fix the following in your CSV and run again:")
        for message in grade_errors + weight_errors:
            print(f"  - {message}")
        sys.exit(1)

    print("Grade validation:  OK (all scores between 0 and 100)")
    print("Weight validation: OK (Formative = 60, Summative = 40, Total = 100)")

    # Transcript table
    print("\n" + "=" * 72)
    print(f"{'Assignment':<28}{'Category':<12}{'Grade (%)':>10}{'Weight':>9}{'Final weight':>13}")
    print("-" * 72)
    for item in data:
        print(
            f"{item['assignment']:<28}{item['group']:<12}"
            f"{fmt(item['score']):>10}{fmt(item['weight']):>9}{fmt(weighted_score(item)):>13}"
        )
    print("-" * 72)

    formative_total = category_total(data, "Formative")
    summative_total = category_total(data, "Summative")
    total_grade = formative_total + summative_total
    gpa = calculate_gpa(total_grade)

    formative_pct = formative_total / FORMATIVE_TARGET * 100
    summative_pct = summative_total / SUMMATIVE_TARGET * 100

    print(f"{'Formatives (60)':<59}{fmt(formative_total):>13}")
    print(f"{'Summatives (40)':<59}{fmt(summative_total):>13}")
    print(f"{'Total Grade (100)':<59}{fmt(total_grade):>13}")
    print(f"{'GPA':<59}{fmt(gpa):>13}")
    print("=" * 72)

    print(f"\nFormative category: {formative_pct:.2f}% (needs >= {fmt(PASS_MARK)}%)")
    print(f"Summative category: {summative_pct:.2f}% (needs >= {fmt(PASS_MARK)}%)")

    # Pass only if BOTH categories are at or above 50%
    passed = formative_pct >= PASS_MARK and summative_pct >= PASS_MARK
    status = "PASSED" if passed else "FAILED"

    resubmissions = find_resubmissions(data)
    resubmit_text = ", ".join(item["assignment"] for item in resubmissions) if resubmissions else "None"

    print(f"\nStatus: {status}")
    print(f"Available for resubmission: {resubmit_text}")

    return {
        "formative_total": formative_total,
        "summative_total": summative_total,
        "gpa": gpa,
        "status": status,
        "resubmissions": [item["assignment"] for item in resubmissions],
    }


if __name__ == "__main__":
    try:
        course_data = load_csv_data()
        evaluate_grades(course_data)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(1)