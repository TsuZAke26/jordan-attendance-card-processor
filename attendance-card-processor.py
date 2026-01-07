import shutil
import os
import re
import pymupdf
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import cv2  # The OpenCV library
import numpy as np # The NumPy library

NAME_REGEX = re.compile(r"[A-Za-z]+(\,|\.)\s*(Mrs?(\,|\.)|Miss)\s*[A-Za-z\s]+")

SOURCE_PATH = "./images/source"
TEMP_PATH = "./images/source-ocr"
OUTPUT_PATH = "./images/processed"

def extract_name_from_card_image(pdf_filename):
  """Attempts to determine the name contained within the PDF scan of a membership card"""
  try :
    path = os.path.join(SOURCE_PATH, pdf_filename)
    pdfFile = pymupdf.open(path)
    firstPage = pdfFile.load_page(0)
    firstPagePixmap = firstPage.get_pixmap(dpi=150, colorspace="RGB")
    
    # create temp PDF with PyMuPDF OCR processing applied
    tempFilename = "temp_" + pdf_filename
    tempPath = os.path.join(TEMP_PATH, tempFilename)
    if os.path.exists(tempPath):
      os.remove(tempPath)
    firstPagePixmap.pdfocr_save(tempPath, compress=False)
    
    ocrPdfFile = pymupdf.open(tempPath)
    ocrFirstPage = ocrPdfFile.load_page(0)
    ocrPdfText = ocrFirstPage.get_text()
    ocrPdfTextSplit = ocrPdfText.split('\n')
    
    for line in ocrPdfTextSplit:
      line = line.strip()
      matchedText = NAME_REGEX.search(line)
      if matchedText:
        return matchedText.group(0)
    
  except Exception as ex:
    print("extract_name_from_card_image(): Exception occurred in processing\n")
    print(ex)
    return None

# Method migrated over from code supplied by Mr. Jordan
def extract_name_from_pdf(pdf_path):
    """
    Tries to extract the person's name from the PDF.
    It pre-processes the image with OpenCV for better OCR
    and uses a SPECIFIC regex to find the name.
    """
    text = ""
    
    # --- METHOD 1: Try fast digital text extraction ---
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text()
    except Exception as e:
        print(f"  - Warning (pdfplumber): {e}")
        text = None

    # --- METHOD 2: Fallback to slow OCR (with Image Pre-processing) ---
    if not text:
        print("  - No digital text. Trying OCR (with OpenCV pre-processing)...")
        try:
            # For Windows, you might need to add poppler_path=POPPLER_PATH
            # images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=POPPLER_PATH)
            
            # For Mac/Linux (or if Poppler is in your PATH)
            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            
            if images:
                # --- PRE-PROCESSING WITH OPENCV ---
                pil_image = images[0]
                open_cv_image = np.array(pil_image)
                gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                _, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Send the clean image to the default Tesseract engine
                text = pytesseract.image_to_string(thresholded_image)
            else:
                print("  - Error: PDF seems to be empty or corrupted.")
                return None
        except Exception as e:
            print(f"  - ERROR: OCR process failed: {e}")
            return None

    # --- Process the text we found (either from Method 1 or 2) ---
    if not text:
        print("  - Error: No text found even after OCR.")
        return None
        
    lines = text.split('\n')
    
    # --- NEW SPECIFIC LOGIC: Search for the name pattern ---
    print("  - Searching for specific name pattern...")
    for line in lines:
        line = line.strip() # Clean up whitespace
        
        # Use .search() to find the pattern *anywhere* in the line
        match = NAME_REGEX.search(line) 
        
        if match:
            # If we find a match, extract *only* the matched part
            found_name = match.group(0)
            
            # This regex is so specific, we no longer need the
            # old "if len(found_name) > 30" cleanup code.
            
            print(f"  - Found match: '{found_name}' (in line: '{line}')")
            return found_name  # Return the *first* name found

    # If the loop finishes without finding a match
    print(f"  - Error: Could not find a line matching the name pattern.")
    return None

def main():
  for filename in os.listdir(SOURCE_PATH):
    if filename.lower().endswith('.pdf'):
      oldFilePath = os.path.join(SOURCE_PATH, filename)
      
      # Attempt to read file name from card image scan
      nameFromPdf = extract_name_from_card_image(filename)
      if not nameFromPdf:
        nameFromPdf = extract_name_from_pdf(oldFilePath)
        
      if not nameFromPdf:
        print("Name could not be extracted from card image. Continuing...")
        continue
        
      print("Name: " + nameFromPdf)
      newFilename = nameFromPdf + ".pdf"
      newFilePath = os.path.join(OUTPUT_PATH, newFilename)
      shutil.copyfile(oldFilePath, newFilePath)
    
  # Cleanup any files in temp directory once the job is done
  for filename in os.listdir(TEMP_PATH):
    tempFilePath = os.path.join(TEMP_PATH, filename)
    if os.path.isfile(tempFilePath):
      os.remove(tempFilePath)
  
if __name__ == "__main__":
  main()
