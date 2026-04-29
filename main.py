import customtkinter as ctk
from tkinter import filedialog
import pygame
import whisper
import threading
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

# init pygame mixer
pygame.mixer.init()

# app settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

song_path = ""
paused = False
song_length = 0  # total duration in seconds

def get_duration(path):
    try:
        if path.endswith(".mp3"):
            audio = MP3(path)
        else:
            audio = WAVE(path)
        return audio.info.length
    except:
        return 0

def format_time(seconds):
    seconds = int(seconds)
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

# update progress bar every second
def update_progress():
    if pygame.mixer.music.get_busy() and not paused:
        pos = pygame.mixer.music.get_pos() / 1000  # ms to seconds
        if song_length > 0:
            progress_bar.set(pos / song_length)
            time_label.configure(text=f"{format_time(pos)} / {format_time(song_length)}")
    app.after(1000, update_progress)

def load_song():
    global song_path, paused, song_length
    path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if path:
        song_path = path
        paused = False
        song_length = get_duration(path)
        song_label.configure(text=path.split("/")[-1])
        pygame.mixer.music.load(path)
        progress_bar.set(0)
        time_label.configure(text=f"00:00 / {format_time(song_length)}")

def play_song():
    global paused
    if song_path == "":
        return
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.play()

def pause_song():
    global paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        paused = True

def stop_song():
    global paused
    pygame.mixer.music.stop()
    paused = False
    progress_bar.set(0)
    time_label.configure(text=f"00:00 / {format_time(song_length)}")

# run whisper in background thread
def transcribe_thread():
    if song_path == "":
        return
    lyrics_box.delete("1.0", "end")
    lyrics_box.insert("1.0", "Generating... please wait")
    btn_lyrics.configure(state="disabled")

    def run():
        model = whisper.load_model("base")
        result = model.transcribe(song_path)
        text = result["text"].strip()
        app.after(0, lambda: update_lyrics(text))

    threading.Thread(target=run, daemon=True).start()

def update_lyrics(text):
    lyrics_box.delete("1.0", "end")
    lyrics_box.insert("1.0", text)
    btn_lyrics.configure(state="normal")

# init window
app = ctk.CTk()
app.title("Music Player")
app.geometry("800x400")

# left frame - controls
left_frame = ctk.CTkFrame(app, width=300)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

song_label = ctk.CTkLabel(left_frame, text="No song loaded", wraplength=260)
song_label.pack(pady=(20, 8))

# progress bar and time label
progress_bar = ctk.CTkProgressBar(left_frame, width=260)
progress_bar.set(0)
progress_bar.pack(pady=(0, 4))

time_label = ctk.CTkLabel(left_frame, text="00:00 / 00:00")
time_label.pack(pady=(0, 12))

btn_load = ctk.CTkButton(left_frame, text="Load", command=load_song)
btn_load.pack(pady=8)

btn_play = ctk.CTkButton(left_frame, text="Play", command=play_song)
btn_play.pack(pady=8)

btn_pause = ctk.CTkButton(left_frame, text="Pause", command=pause_song)
btn_pause.pack(pady=8)

btn_stop = ctk.CTkButton(left_frame, text="Stop", command=stop_song)
btn_stop.pack(pady=8)

btn_lyrics = ctk.CTkButton(left_frame, text="Generate Lyrics", command=transcribe_thread)
btn_lyrics.pack(pady=8)

# right frame - lyrics box
right_frame = ctk.CTkFrame(app)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

lyrics_box = ctk.CTkTextbox(right_frame)
lyrics_box.pack(fill="both", expand=True, padx=10, pady=10)

# start progress loop
update_progress()

app.mainloop()