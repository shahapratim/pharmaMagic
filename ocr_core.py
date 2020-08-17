# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 13:29:59 2020

@author: Pratim
"""

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

def ocr_core(filename):

    
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    TESSDATA_PREFIX ="C:\\Program Files\\Tesseract-OCR"
    text = pytesseract.image_to_string(Image.open(filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text
