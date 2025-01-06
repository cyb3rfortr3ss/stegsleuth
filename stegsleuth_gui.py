# stegsleuth - a steganography detection framework 
# author - @cyb3rf034r3ss
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import wave
from moviepy import VideoFileClip


class AssetManager:
    def __init__(self, asset_folder='assets'):
        self.asset_folder = asset_folder
        self.assets = []

    def list_assets(self):
        self.assets = [f for f in os.listdir(self.asset_folder) if os.path.isfile(os.path.join(self.asset_folder, f))]
        return self.assets

    def upload_asset(self, source_path):
        if os.path.isfile(source_path):
            destination_path = os.path.join(self.asset_folder, os.path.basename(source_path))
            shutil.copy(source_path, destination_path)
            return True
        else:
            return False

    def select_asset(self, asset_number):
        if 0 < asset_number <= len(self.assets):
            return self.assets[asset_number - 1]
        else:
            return None


class SteganographyDetect:
    @staticmethod
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

    @staticmethod
    def detect_audio_steganography(audio_path):
        audio = wave.open(audio_path, 'rb')
        frames = audio.readframes(audio.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)

        anomalies = np.where(audio_data % 2 != 0)[0]
        return anomalies

    @staticmethod
    def detect_video_steganography(video_path):
        video = VideoFileClip(video_path)
        frame_data = []

        for frame in video.iter_frames(fps=1, dtype="uint8"):
            frame_data.append(frame.sum())

        return frame_data


class StegSleuthGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("StegSleuth - Steganography Detection")
        self.root.geometry("600x400")
        self.asset_manager = AssetManager()
        self.selected_asset = None
        self.selected_asset_type = None

        self.create_widgets()

    def create_widgets(self):
        
        self.list_button = tk.Button(self.root, text="List Assets", command=self.list_assets)
        self.list_button.pack(pady=10)

        
        self.upload_button = tk.Button(self.root, text="Upload Asset", command=self.upload_asset)
        self.upload_button.pack(pady=10)

        
        self.asset_label = tk.Label(self.root, text="Select Asset")
        self.asset_label.pack()

        self.asset_dropdown = tk.StringVar()
        self.asset_dropdown.set("Select Asset")
        self.asset_menu = tk.OptionMenu(self.root, self.asset_dropdown, [])
        self.asset_menu.pack(pady=10)

        
        self.analyze_button = tk.Button(self.root, text="Analyze Selected Asset", command=self.analyze_asset)
        self.analyze_button.pack(pady=10)

        
        self.result_text = tk.Text(self.root, height=10, width=60)
        self.result_text.pack(pady=10)

    def list_assets(self):
        assets = self.asset_manager.list_assets()
        if not assets:
            self.show_message("No assets found in the 'assets' folder.")
        else:
            self.asset_dropdown.set("Select Asset")
            self.asset_menu['menu'].delete(0, 'end')
            for asset in assets:
                self.asset_menu['menu'].add_command(label=asset, command=tk._setit(self.asset_dropdown, asset))

    def upload_asset(self):
        file_path = filedialog.askopenfilename(title="Select a File to Upload")
        if file_path:
            if self.asset_manager.upload_asset(file_path):
                self.show_message(f"File uploaded successfully: {file_path}")
            else:
                self.show_message(f"Failed to upload: {file_path}")

    def analyze_asset(self):
        asset_name = self.asset_dropdown.get()
        if asset_name == "Select Asset":
            self.show_message("Please select an asset first.")
            return

        asset_path = os.path.join(self.asset_manager.asset_folder, asset_name)

      
        self.selected_asset_type = self.detect_asset_type(asset_name)

        if self.selected_asset_type == "image":
            self.analyze_image(asset_path)
        elif self.selected_asset_type == "audio":
            self.analyze_audio(asset_path)
        elif self.selected_asset_type == "video":
            self.analyze_video(asset_path)
        else:
            self.show_message("Unsupported file type.")

    def analyze_image(self, image_file):
        self.result_text.delete(1.0, tk.END)
        hidden_message = SteganographyDetect.detect_lsb_steganography(image_file)
        if hidden_message:
            self.result_text.insert(tk.END, f"Hidden data detected in image: {hidden_message[:100]}...\n")
        else:
            self.result_text.insert(tk.END, "No hidden data detected in the image.\n")

    def analyze_audio(self, audio_file):
        self.result_text.delete(1.0, tk.END)
        anomalies = SteganographyDetect.detect_audio_steganography(audio_file)
        if anomalies.size > 0:
            self.result_text.insert(tk.END, f"Frequency anomalies detected in audio: {anomalies[:10]}...\n")
        else:
            self.result_text.insert(tk.END, "No hidden data detected in the audio.\n")

    def analyze_video(self, video_file):
        self.result_text.delete(1.0, tk.END)
        frame_data = SteganographyDetect.detect_video_steganography(video_file)
        if frame_data:
            self.result_text.insert(tk.END, f"Possible hidden data detected in video frames: {frame_data[:10]}...\n")
        else:
            self.result_text.insert(tk.END, "No hidden data detected in the video.\n")

    def detect_asset_type(self, asset_name):
        if asset_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return 'image'
        elif asset_name.lower().endswith(('.wav', '.mp3')):
            return 'audio'
        elif asset_name.lower().endswith(('.mp4', '.avi')):
            return 'video'
        else:
            return 'unknown'

    def show_message(self, message):
        messagebox.showinfo("StegSleuth", message)



if __name__ == "__main__":
    root = tk.Tk()
    gui = StegSleuthGUI(root)
    root.mainloop()
