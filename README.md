# StegSleuth
Steganography Detection Framework Used For Analyzing Files i.e PDFs, Images, Videos, & Audios To Uncover Hidden Data, Gems Or Secrets.

# Install Requirements
pip install -r requirements.txt

sudo apt-get install tesseract-ocr -y

sudo apt-get install exiftool -y

sudo apt-get install pdfinfo -y

# Export PATH
export PATH="/usr/bin:$PATH"

# Start StegSleuth 
python3 stegsleuth.py

# Start StegSleuth GUI 
python3 stegsleuth_gui.py
