import shutil
import os
import re
import pymupdf

NAME_REGEX = re.compile(r"[A-Za-z]+(\,|\.)\s*(Mrs?(\,|\.)|Miss)\s*[A-Za-z\s]+")

SOURCE_PATH = "./images/source"
TEMP_PATH = "./images/source-ocr"
OUTPUT_PATH = "./images/processed"

def extract_name_from_card_image(pdf_filename):
  """Attempts to determine the name contained within the PDF scan of a tithe card"""
  try :
    path = os.path.join(SOURCE_PATH, pdf_filename)
    pdfFile = pymupdf.open(path)
    firstPage = pdfFile.load_page(0)
    firstPagePixmap = firstPage.get_pixmap(dpi=300, colorspace="RGB")
    
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
 
def main():
  for filename in os.listdir(SOURCE_PATH):
    if filename.lower().endswith('.pdf'):
      oldFilePath = os.path.join(SOURCE_PATH, filename)
      nameFromPdf = extract_name_from_card_image(filename)
      if not nameFromPdf:
        print("Name could not be extracted from card iamge. Continuing...")
        continue
        
      print("Name: " + nameFromPdf)
      newFilename = nameFromPdf + ".pdf"
      newFilePath = os.path.join(OUTPUT_PATH, newFilename)
      shutil.copyfile(oldFilePath, newFilePath)
  
if __name__ == "__main__":
    main()
