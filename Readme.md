$ python3 grade-evaluator.py
Enter the name of the CSV file to process (e.g., grades.csv): grades.csv
--- Processing Grades ---
Grade validation:  OK (all scores between 0 and 100)
Weight validation: OK (Formative = 60, Summative = 40, Total = 100)

=================================================================================
Assignment                           Category     Grade (%)   Weight Final weight
---------------------------------------------------------------------------------
Quiz                                 Formative           85       20           17
Group Exercise                       Formative           40       20            8
Functions and Debugging Lab          Formative           45       20            9
Midterm Project - Simple Calculator  Summative           70       20           14
Final Project - Text-Based Game      Summative           60       20           12
---------------------------------------------------------------------------------
Formatives (60)                                                                34
Summatives (40)                                                                26
Total Grade (100)                                                              60
GPA                                                                             3
=================================================================================

Formative category: 56.67% (needs >= 50%)
Summative category: 65.00% (needs >= 50%)

Status: PASSED
Available for resubmission: Group Exercise, Functions and Debugging Lab