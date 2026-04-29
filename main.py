import customtkinter as ctk
from tkinter import filedialog
import pygame

# init pygame mixer
pygame.mixer.init()

# app settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

song_path = ""
paused = False

def load_song():
    global song_path, paused
    path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if path:
        song_path = path
        paused = False
        song_label.configure(text=path.split("/")[-1])
        pygame.mixer.music.load(path)

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

# init window
app = ctk.CTk()
app.title("Music Player")
app.geometry("800x400")

# left frame - controls
left_frame = ctk.CTkFrame(app, width=300)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

song_label = ctk.CTkLabel(left_frame, text="No song loaded", wraplength=260)
song_label.pack(pady=20)

btn_load = ctk.CTkButton(left_frame, text="Load", command=load_song)
btn_load.pack(pady=8)

btn_play = ctk.CTkButton(left_frame, text="Play", command=play_song)
btn_play.pack(pady=8)

btn_pause = ctk.CTkButton(left_frame, text="Pause", command=pause_song)
btn_pause.pack(pady=8)

btn_stop = ctk.CTkButton(left_frame, text="Stop", command=stop_song)
btn_stop.pack(pady=8)

# right frame - lyrics box
right_frame = ctk.CTkFrame(app)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

lyrics_box = ctk.CTkTextbox(right_frame)
lyrics_box.pack(fill="both", expand=True, padx=10, pady=10)

app.mainloop()