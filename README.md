This is a small Python script intended to be used to extract the name printed on a scanned index card in PDF format, and then use that found name to rename the file it was contained in. The intent is to look for text strings in one fo the following formats:

- lastName, Mr. firstName
- lastName, Mrs. firstName
- lastName, Miss firstName

(in OCR processing, sometimes the period that would follow the title would be interpreted as a comma, so the regex present in the script also accounts for that)

How to use

1. Clone the repository. Add the source PDF scans to the `/images/source` folder.
2. If not already, install Python on your computer.
3. Setup your Python virtual environment by installing the following libraries via `pip`:

`python -m pip install --upgrade pymupdf pdfplumber pytesseract pdf2image opency-python numpy`

4. Run the script by opening a command terminal and navigate to the project root directory (e.g. on Windows, holding Shift and right-clicking in the project directory should accomplish this). Once open, type "./attendance-card-processor.py" and the script should run.
5. Watch the magic unfurl. If a name is successfully found in a file, it will be copied over to the `/images/processed` directory with the new filename.
