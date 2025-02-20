import tkinter as tk
from tkinter import filedialog, ttk
import soundfile as sf
import numpy as np
from scipy.signal import convolve
import sounddevice as sd
import os

class ReverbPlugin:
    def __init__(self, root):
        self.root = root
        self.root.title("Reverb Plugin")
        self.root.geometry("400x300")
        
        self.audio_data = None
        self.sample_rate = None
        self.modified_audio = None
        
        # GUI Elements
        self.create_widgets()
        
    def create_widgets(self):
        # Upload button
        self.upload_btn = ttk.Button(self.root, text="Upload Audio File", command=self.upload_file)
        self.upload_btn.pack(pady=10)
        
        # File label
        self.file_label = ttk.Label(self.root, text="No file selected")
        self.file_label.pack(pady=5)
        
        # Reverb slider
        self.reverb_label = ttk.Label(self.root, text="Reverb Amount: 0")
        self.reverb_label.pack(pady=5)
        self.reverb_slider = ttk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     command=self.update_reverb_label)
        self.reverb_slider.pack(pady=5)
        
        # Playback buttons
        self.play_original_btn = ttk.Button(self.root, text="Play Original", 
                                          command=self.play_original, state='disabled')
        self.play_original_btn.pack(pady=5)
        
        self.play_preview_btn = ttk.Button(self.root, text="Preview Reverb", 
                                         command=self.play_preview, state='disabled')
        self.play_preview_btn.pack(pady=5)
        
        # Apply and Download
        self.apply_btn = ttk.Button(self.root, text="Apply Reverb", 
                                  command=self.apply_reverb, state='disabled')
        self.apply_btn.pack(pady=5)
        
        self.download_btn = ttk.Button(self.root, text="Download", 
                                     command=self.download_file, state='disabled')
        self.download_btn.pack(pady=5)
        
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3")]
        )
        if file_path:
            self.audio_data, self.sample_rate = sf.read(file_path)
            self.file_label.config(text=os.path.basename(file_path))
            self.enable_buttons()
            
    def update_reverb_label(self, value):
        self.reverb_label.config(text=f"Reverb Amount: {int(float(value))}")
        
    def create_reverb(self, audio, reverb_amount):
        # Simple reverb implementation using convolution with an impulse response
        impulse_length = int(self.sample_rate * 0.3)  # 300ms reverb tail
        impulse = np.zeros(impulse_length)
        decay = np.exp(-np.linspace(0, 5, impulse_length))
        impulse = decay * np.random.randn(impulse_length)
        impulse /= np.max(np.abs(impulse))
        
        # Scale reverb effect based on slider (0-100)
        wet_amount = reverb_amount / 100
        dry_amount = 1 - (wet_amount * 0.5)
        
        # Apply reverb
        if len(audio.shape) > 1:  # Stereo
            reverb = np.zeros_like(audio)
            for channel in range(audio.shape[1]):
                reverb[:, channel] = convolve(audio[:, channel], impulse, mode='full')[:len(audio)]
        else:  # Mono
            reverb = convolve(audio, impulse, mode='full')[:len(audio)]
            
        return dry_amount * audio + wet_amount * reverb
    
    def play_original(self):
        sd.play(self.audio_data, self.sample_rate)
        
    def play_preview(self):
        if self.audio_data is not None:
            reverb_amount = self.reverb_slider.get()
            preview_audio = self.create_reverb(self.audio_data, reverb_amount)
            sd.play(preview_audio, self.sample_rate)
            
    def apply_reverb(self):
        if self.audio_data is not None:
            reverb_amount = self.reverb_slider.get()
            self.modified_audio = self.create_reverb(self.audio_data, reverb_amount)
            self.download_btn.config(state='normal')
            
    def download_file(self):
        if self.modified_audio is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav")]
            )
            if file_path:
                sf.write(file_path, self.modified_audio, self.sample_rate)
                tk.messagebox.showinfo("Success", "File saved successfully!")
                
    def enable_buttons(self):
        self.play_original_btn.config(state='normal')
        self.play_preview_btn.config(state='normal')
        self.apply_btn.config(state='normal')

def main():
    root = tk.Tk()
    app = ReverbPlugin(root)
    root.mainloop()

if __name__ == "__main__":
    main()
