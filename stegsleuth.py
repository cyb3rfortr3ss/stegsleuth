# stegsleuth - a steganography detection framework 
# author - @cyb3rf034r3ss
import os
import readline
import sys
import shutil
from PIL import Image
import pytesseract
import numpy as np
import wave
import subprocess
from moviepy import VideoFileClip
from colorama import init, Fore, Back, Style
import art

if os.name == 'posix':
   os.system('clear')
else:
   exit()

init(autoreset=True)

print(art.text2art("StegSleuth"))

class AssetManager:
    def __init__(self, asset_folder='assets'):
        self.asset_folder = asset_folder
        self.assets = []

    def list_assets(self):
        self.assets = [f for f in os.listdir(self.asset_folder) if os.path.isfile(os.path.join(self.asset_folder, f))]
        return self.assets

    def select_asset(self, asset_number):
        if 0 < asset_number <= len(self.assets):
            return self.assets[asset_number - 1]
        else:
            print(Fore.RED + "\nInvalid selection.\n")
            return None

    def upload_asset(self, source_path):
        # Copy the file to the assets folder
        if os.path.isfile(source_path):
            destination_path = os.path.join(self.asset_folder, os.path.basename(source_path))
            shutil.copy(source_path, destination_path)
            print(Fore.GREEN + f"\n[*] File '{source_path}' uploaded successfully to '{self.asset_folder}'.\n")
        else:
            print(Fore.RED + f"\nInvalid file path: {source_path}. Upload failed.\n")

def detect_lsb_steganography(image_path):
    image = Image.open(image_path)
    image_array = np.array(image)
    hidden_data = []

    for row in image_array:
        for pixel in row:
            hidden_data.append(pixel[0] & 1)
            hidden_data.append(pixel[1] & 1)
            hidden_data.append(pixel[2] & 1)

    hidden_message = ''.join(map(str, hidden_data))
    return hidden_message

def detect_audio_steganography(audio_path):
    audio = wave.open(audio_path, 'rb')
    frames = audio.readframes(audio.getnframes())
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    anomalies = np.where(audio_data % 2 != 0)[0]
    return anomalies

def detect_video_steganography(video_path):
    video = VideoFileClip(video_path)
    frame_data = []

    for frame in video.iter_frames(fps=1, dtype="uint8"):
        frame_data.append(frame.sum())
    
    return frame_data

class SteganographyConsole:
    def __init__(self):
        self.asset_manager = AssetManager()
        self.selected_asset = None
        self.selected_asset_type = None

    def run(self):
        print(Fore.GREEN + "[Author] @cyb3rf034r3ss")
        print(Fore.GREEN + "[StegSleuth] Steganography Detection Framework!")
        print()
        while True:
            command = input(Fore.YELLOW + "[StegSleuth] > ").strip()

            if command == 'list assets':
                self.list_assets()
            elif command.startswith('select'):
                self.select_asset(command)
            elif command == 'analyze':
                self.analyze_selected_file()
            elif command == 'help':
                self.display_help()
            elif command.startswith('upload'):
                self.upload_asset(command)
            elif command == 'exit':
                print(Fore.RED + "\nExiting framework...\n")
                sys.exit()
            else:
                print(Fore.RED + "\nUnknown command. Try again.\n")

    def list_assets(self):
        assets = self.asset_manager.list_assets()
        if not assets:
            print(Fore.RED + "\nNo assets found.\n")
        else:
            print(Fore.CYAN + "\n[*] Assets in 'assets' folder:\n")
            for idx, asset in enumerate(assets, start=1):
                print(Fore.CYAN + f" {idx}. {asset}\n")

    def select_asset(self, command):
        try:
            asset_number = int(command.split()[1])
            selected_asset = self.asset_manager.select_asset(asset_number)
            if selected_asset:
                self.selected_asset = selected_asset
                self.selected_asset_type = self.detect_asset_type(selected_asset)
                print(Fore.GREEN + f"\n[*] Selected asset: {selected_asset}\n")
                print(Fore.YELLOW + f"[*] File type detected: {self.selected_asset_type}\n")
        except (IndexError, ValueError):
            print(Fore.RED + "\nUsage: select <asset number>\n")

    def detect_asset_type(self, asset):
        if asset.lower().endswith(('.png', '.jpg', '.jpeg')):
            return 'image'
        elif asset.lower().endswith(('.wav', '.mp3')):
            return 'audio'
        elif asset.lower().endswith(('.mp4', '.avi')):
            return 'video'
        elif asset.lower().endswith('.pdf'):
            return 'pdf'
        else:
            return 'unknown'

    def analyze_selected_file(self):
        if not self.selected_asset:
            print(Fore.RED + "\nNo asset selected. Please select a file first.\n")
            return

        asset_path = os.path.join(self.asset_manager.asset_folder, self.selected_asset)

        if self.selected_asset_type == 'image':
            self.analyze_image(asset_path)
        elif self.selected_asset_type == 'audio':
            self.analyze_audio(asset_path)
        elif self.selected_asset_type == 'video':
            self.analyze_video(asset_path)
        elif self.selected_asset_type == 'pdf':
            self.analyze_pdf(asset_path)
        else:
            print(Fore.RED + "\nUnsupported file type.\n")

    def analyze_image(self, image_file):
        print(Fore.GREEN + f"\n[*] Running image analysis on {image_file}...\n")
        hidden_message = detect_lsb_steganography(image_file)
        if hidden_message:
            print(Fore.YELLOW + f"Hidden data detected in image: {hidden_message[:100]}...\n")
        else:
            print(Fore.RED + "\nNo hidden data detected in the image.\n")
        print(Fore.GREEN + f"[*] Exif Data\n")
        exif_data = subprocess.check_output(f'exiftool {image_file}', shell=True)
        print(exif_data.decode())
        image = Image.open(image_file)

        text = pytesseract.image_to_string(image)

        print(Fore.GREEN + f"[*] Extracted Text From Image\n")
        print(text)

    def analyze_audio(self, audio_file):
        print(Fore.GREEN + f"[*] Running audio analysis on {audio_file}...")
        anomalies = detect_audio_steganography(audio_file)
        if anomalies.size > 0:
            print(Fore.YELLOW + f"Frequency anomalies detected in audio: {anomalies[:10]}...") 
        else:
            print(Fore.RED + "No hidden data detected in the audio.")

    def analyze_video(self, video_file):
        print(Fore.GREEN + f"[*] Running video analysis on {video_file}...")
        frame_data = detect_video_steganography(video_file)
        if frame_data:
            print(Fore.YELLOW + f"Possible hidden data detected in video frames: {frame_data[:10]}...") 
        else:
            print(Fore.RED + "No hidden data detected in the video.")

    def analyze_pdf(self, pdf_file):
        print(Fore.GREEN + f"\n[*] Running PDF analysis on {pdf_file}...\n")
        try:
            
            pdf_info = subprocess.check_output(f'pdfinfo {pdf_file}', shell=True)
            print(Fore.YELLOW + f"PDF Metadata:\n{pdf_info.decode()}")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error extracting PDF metadata: {e}\n")

    def display_help(self):
        print(Fore.CYAN + "\nHelp Menu:")
        print(Fore.GREEN + "list assets     - Lists all assets in the 'assets' folder")
        print(Fore.GREEN + "select <number> - Selects an asset by its number")
        print(Fore.GREEN + "analyze         - Analyzes the selected asset for hidden data")
        print(Fore.GREEN + "help            - Displays this help menu")
        print(Fore.GREEN + "upload <path>   - Uploads a file to the 'assets' folder")
        print(Fore.GREEN + "exit            - Exits the framework")
        print()
    
    def upload_asset(self, command):
        try:
            file_path = command.split()[1]
            self.asset_manager.upload_asset(file_path)
        except IndexError:
            print(Fore.RED + "\nUsage: upload <path to file>\n")


def main():
    console = SteganographyConsole()
    console.run()


if __name__ == '__main__':
    main()
