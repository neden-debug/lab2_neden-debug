#!/usr/bin/env bash

ARCHIVE_DIR="archive"
SOURCE_FILE="grades.csv"
LOG_FILE="organizer.log"

# Stop if the source file is missing, so we never archive nothing
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: '$SOURCE_FILE' was not found in $(pwd)."
    echo "Hint: run this script from the folder that contains $SOURCE_FILE."
    exit 1
fi

# Warn (but still archive) if the file is empty
if [ ! -s "$SOURCE_FILE" ]; then
    echo "Warning: '$SOURCE_FILE' is empty. Archiving it anyway."
fi

# 1. Archive directory
if [ ! -d "$ARCHIVE_DIR" ]; then
    if ! mkdir "$ARCHIVE_DIR"; then
        echo "Error: could not create the '$ARCHIVE_DIR' directory."
        exit 1
    fi
    echo "Created directory: $ARCHIVE_DIR/"
fi

# 2. Archival process: rename with timestamp and move into archive/
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

# Avoid overwriting if the script is run twice in the same second
if [ -e "$ARCHIVE_DIR/$ARCHIVED_NAME" ]; then
    COUNTER=1
    while [ -e "$ARCHIVE_DIR/grades_${TIMESTAMP}_${COUNTER}.csv" ]; do
        COUNTER=$((COUNTER + 1))
    done
    ARCHIVED_NAME="grades_${TIMESTAMP}_${COUNTER}.csv"
fi

if ! mv "$SOURCE_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME"; then
    echo "Error: could not move '$SOURCE_FILE' to '$ARCHIVE_DIR/$ARCHIVED_NAME'."
    exit 1
fi
echo "Archived: $SOURCE_FILE -> $ARCHIVE_DIR/$ARCHIVED_NAME"

# 3. Workspace reset: fresh empty grades.csv
if ! touch "$SOURCE_FILE"; then
    echo "Error: could not create a new empty '$SOURCE_FILE'."
    exit 1
fi
echo "Created new empty: $SOURCE_FILE"

# 4. Logging (>> appends, so entries accumulate across runs)
echo "[$TIMESTAMP] Original: $SOURCE_FILE | Archived as: $ARCHIVE_DIR/$ARCHIVED_NAME" >> "$LOG_FILE"
echo "Logged to: $LOG_FILE"
