#!/usr/bin/env python3
import sqlite3
import os
import sys


def clean_text(text):
    """Basic cleaning for extracted text parts."""
    # Strip leading/trailing whitespace. Return None if the result is empty.
    cleaned = text.strip() if text else ""
    return cleaned if cleaned else None


def parse_and_insert(db_cursor, file_path):
    """Parses a single text file and inserts entries into the database."""
    print(f"Processing file: {file_path}")
    entries_added = 0
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                # Split the line based on the '---' separator
                parts = line.split("---")

                # We need at least a word part and a definition part
                if len(parts) < 2:
                    # print(f"  Skipping line {line_num} (not enough '---' separators): {line}")
                    continue

                word = clean_text(parts[0])
                pos = None
                definition = None

                if len(parts) >= 3:
                    # Assumes format: word --- pos --- definition
                    # The second part is treated as part_of_speech
                    pos = clean_text(parts[1])
                    # Join the rest as definition, in case '---' was in the definition
                    definition = clean_text("---".join(parts[2:]))
                elif len(parts) == 2:
                    # Assumes format: word --- definition (no explicit PoS part)
                    pos = None  # No middle part for PoS
                    definition = clean_text(parts[1])

                # Only insert if we successfully extracted at least a word and a definition
                if word and definition:
                    try:
                        db_cursor.execute(
                            """
                            INSERT INTO entries (words, part_of_speech, definition)
                            VALUES (?, ?, ?)
                        """,
                            (word, pos, definition),
                        )
                        entries_added += 1
                    except sqlite3.Error as e:
                        print(
                            f"  Error inserting line {line_num} from {file_path}: {e}",
                            file=sys.stderr,
                        )
                        print(
                            f"    Word: '{word}', PoS: '{pos}', Def: '{definition}'",
                            file=sys.stderr,
                        )
                # else:
                # Optional: Log lines skipped due to missing word/definition after parsing
                # print(f"  Skipping line {line_num} (missing word or definition after parse): {line}")

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error reading or processing file {file_path}: {e}", file=sys.stderr)

    print(f"  Added {entries_added} entries from {os.path.basename(file_path)}")
    return entries_added


def get_configuration():
    """Gets the configuration paths based on the script's location."""
    # --- Configuration ---
    # Get the absolute path of the directory where the script resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define paths relative to the script's directory
    db_path = os.path.join(script_dir, "data", "dictionary.db")
    input_dir = os.path.join(script_dir, "data", "ocr_results")

    print(f"Database path: {db_path}")
    print(f"Input directory: {input_dir}")

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    return db_path, input_dir


def setup_database(db_path):
    """Connects to the database and ensures the 'entries' table exists."""
    # Ensure the directory for the database exists
    db_dir = os.path.dirname(db_path)
    if db_dir:  # Only create if db_path includes a directory part
        os.makedirs(db_dir, exist_ok=True)

    conn = None  # Initialize connection variable
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Database connection established.")

        # Drop the table if it already exists to prevent duplicate entries on re-runs
        cursor.execute(
            """
            DROP TABLE IF EXISTS entries;
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                words TEXT,
                part_of_speech TEXT,
                definition TEXT
            );
            """
        )
        cursor.execute(
            """
           CREATE INDEX IF NOT EXISTS idx_words ON entries (words)
        """
        )
        conn.commit()  # Commit table creation
        print("Table 'entries' ensured.")
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Database setup error: {e}", file=sys.stderr)
        if conn:
            conn.close()  # Close connection if setup failed after opening
        sys.exit(1)  # Exit if DB setup fails


def process_directory(input_dir, cursor):
    """Walks the input directory, parses .txt files, and inserts data."""
    total_entries_added = 0
    print("Starting file processing...")
    # Use os.walk to recursively find all files in the input directory
    for root, dirs, files in os.walk(input_dir):
        # Sort files for consistent processing order (optional)
        files.sort()
        for filename in files:
            # Process only files ending with .txt (case-insensitive)
            if filename.lower().endswith(".txt"):
                file_path = os.path.join(root, filename)
                # Parse the file and add entries to the DB
                total_entries_added += parse_and_insert(cursor, file_path)
    return total_entries_added


def main():
    """Main execution function."""
    db_path, input_dir = get_configuration()
    conn = None
    try:
        conn, cursor = setup_database(db_path)
        total_entries_added = process_directory(input_dir, cursor)
        conn.commit()  # Commit all inserts after processing all files
        print(
            f"\nProcessing complete. Total entries added to the database: {total_entries_added}"
        )

    except sqlite3.Error as e:
        print(f"Database error occurred during processing: {e}", file=sys.stderr)
        if conn:
            conn.rollback()  # Roll back any changes if an error occurred during inserts
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}", file=sys.stderr)
    finally:
        # Ensure the database connection is closed
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
