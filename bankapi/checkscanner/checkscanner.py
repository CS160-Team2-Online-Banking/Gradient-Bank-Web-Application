try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

# convert the image of the check to grayscale
# run it through tesseract OCR to generate a string
# retrieve the output of the OCR and retrieve the account and routing number
#


pytesseract.pytesseract.tesseract_cmd = r'tesseract-4.0.0-alpha/tesseract.exe'

def get_check_data(img):
    gray_scale = img.convert('LA')
