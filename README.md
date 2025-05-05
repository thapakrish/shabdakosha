## Shabdakosha

This project aims to create a clean, searchable dictionary database from OCR results of scanned pages. We need your help to correct errors in the automatically generated text!

### How to Contribute

The main way to contribute is by correcting the OCR text files located in the `data/ocr_results/` directory. These files often contain errors from the optical character recognition process.

1.  **Fork** this repository to your own GitHub account.
2.  **Clone** your fork to your local machine.
3.  Navigate to the `data/ocr_results/` directory. Inside, you'll find subdirectories (like `100`, `101`, etc.) containing the individual `.txt` files (e.g., `data/ocr_results/100/kosha_25_26.txt`).
4.  **Edit** the `.txt` files to correct any mistakes in the words, parts of speech, or definitions. Ensure the format (`word --- part_of_speech --- definition` or `word --- definition`) is maintained.
    - **Important:** Please compare the text in the `.txt` file with the original source PDF located at `data/source/Sabdakosh10th.pdf`. The numbers in the filename correspond to the page numbers in the PDF (e.g., `kosha_25_26.txt` contains text from pages 25-26 of the PDF).
5.  **Commit** your changes with clear messages describing what you fixed (e.g., "Corrected typos on page 25").
6.  **Push** the changes back to your fork on GitHub.
7.  Submit a **Pull Request** (PR) from your fork back to this main repository.

Alternatively, if you find an error but don't have time to fix it yourself, please **File an Issue**! Describe the error, the file it's in (e.g., `data/ocr_results/100/kosha_25_26.txt`), and the page number in the PDF (`data/source/Sabdakosh10th.pdf`) if possible. Suggestions for improvements are also welcome via issues.

We'll review your changes and merge them. Thank you for helping improve this resource!

### Running the Database Creation Script

After corrections are made and merged, you can regenerate the database using the provided script.

- Run the script: `python create_db.py`
- This will generate or update the `data/dictionary.db` file.

## Database Structure

The `create_db.py` script generates a SQLite database file located at `data/dictionary.db`. This database contains a single table named `entries` with the following structure:

| Column Name      | Data Type | Description                                                               |
| ---------------- | --------- | ------------------------------------------------------------------------- |
| `words`          | TEXT      | The dictionary word or term extracted from the OCR results.               |
| `part_of_speech` | TEXT      | The part of speech (e.g., noun, verb), if identified in the OCR results.  |
| `definition`     | TEXT      | The definition or explanation of the word extracted from the OCR results. |

**Notes:**

- The script attempts to parse lines from the `.txt` files in `data/ocr_results/` using `---` as a delimiter.
- If a line has three or more parts separated by `---`, it assumes the format `word --- part_of_speech --- definition`.
- If a line has exactly two parts, it assumes the format `word --- definition`, and the `part_of_speech` field will be empty (NULL) in the database for that entry.
