import customtkinter as ctk
from tkinter import filedialog
import vlc
import whisper
import threading
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

# init vlc 
instance = vlc.Instance('--aout=pulse')
player = instance.media_player_new()

# app settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

song_path = ""
song_length = 0
paused = False
segments = []  # whisper timestamp segments

def get_duration(path):
    try:
        if path.endswith(".mp3"):
            return MP3(path).info.length
        else:
            return WAVE(path).info.length
    except:
        return 0

def format_time(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def load_song():
    global song_path, song_length, paused, segments
    path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if path:
        song_path = path
        paused = False
        segments = []
        song_length = get_duration(path)
        media = instance.media_new(path)
        player.set_media(media)
        song_label.configure(text=path.split("/")[-1])
        progress_bar.set(0)
        time_label.configure(text=f"00:00 / {format_time(song_length)}")
        lyrics_box._textbox.delete("1.0", "end")

def play_song():
    global paused
    if song_path == "":
        return
    if paused:
        player.pause()  # vlc pause toggles
        paused = False
    else:
        player.play()

def pause_song():
    global paused
    if player.is_playing():
        player.pause()
        paused = True

def stop_song():
    global paused
    player.stop()
    paused = False
    progress_bar.set(0)
    time_label.configure(text=f"00:00 / {format_time(song_length)}")

# update progress bar and karaoke highlight every second
def update_progress():
    if player.is_playing():
        pos_ms = player.get_time()
        length_ms = player.get_length()
        if length_ms > 0:
            pos_sec = pos_ms / 1000
            progress_bar.set(pos_ms / length_ms)
            time_label.configure(text=f"{format_time(pos_sec)} / {format_time(length_ms / 1000)}")
            highlight_lyric(pos_sec)
    app.after(1000, update_progress)

def highlight_lyric(pos_sec):
    if not segments:
        return
    tb = lyrics_box._textbox  # underlying tk Text widget
    tb.tag_config("active", foreground="#1DB954", font=("Helvetica", 13, "bold"))
    tb.tag_config("inactive", foreground="#AAAAAA", font=("Helvetica", 12))
    tb.tag_remove("active", "1.0", "end")
    tb.tag_remove("inactive", "1.0", "end")

    for i, seg in enumerate(segments):
        line = f"{i + 1}.0"
        line_end = f"{i + 1}.end"
        if seg["start"] <= pos_sec <= seg["end"]:
            tb.tag_add("active", line, line_end)
            tb.see(line)  # scroll to active line
        else:
            tb.tag_add("inactive", line, line_end)

# whisper transcription in background thread
def transcribe_thread():
    if song_path == "":
        return
    btn_lyrics.configure(state="disabled")
    lyrics_box._textbox.delete("1.0", "end")
    lyrics_box._textbox.insert("1.0", "Generating... please wait")

    def run():
        global segments
        model = whisper.load_model("small")
        result = model.transcribe(song_path)
        segments = [
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in result["segments"]
        ]
        app.after(0, display_lyrics)

    threading.Thread(target=run, daemon=True).start()

def display_lyrics():
    tb = lyrics_box._textbox
    tb.delete("1.0", "end")
    for seg in segments:
        tb.insert("end", seg["text"] + "\n")
    btn_lyrics.configure(state="normal")

# ── init window ──────────────────────────────────────────────
app = ctk.CTk()
app.title("Music Player")
app.geometry("900x520")
app.resizable(True, True)

# ── left frame ───────────────────────────────────────────────
left_frame = ctk.CTkFrame(app, width=280, corner_radius=12)
left_frame.pack(side="left", fill="y", padx=(14, 6), pady=14)
left_frame.pack_propagate(False)

# song title
song_label = ctk.CTkLabel(
    left_frame, text="No song loaded",
    font=("Helvetica", 13, "bold"),
    wraplength=240, justify="center"
)
song_label.pack(pady=(24, 16))

# progress bar
progress_bar = ctk.CTkProgressBar(left_frame, width=240, height=8, corner_radius=4)
progress_bar.set(0)
progress_bar.pack(pady=(0, 6))

# time label
time_label = ctk.CTkLabel(left_frame, text="00:00 / 00:00", font=("Helvetica", 11))
time_label.pack(pady=(0, 20))

# control buttons
btn_cfg = {"width": 200, "height": 36, "corner_radius": 8, "font": ("Helvetica", 12, "bold")}

btn_load = ctk.CTkButton(left_frame, text="⏏  Load", command=load_song, **btn_cfg)
btn_load.pack(pady=6)

btn_play = ctk.CTkButton(left_frame, text="▶  Play", command=play_song, **btn_cfg)
btn_play.pack(pady=6)

btn_pause = ctk.CTkButton(left_frame, text="⏸  Pause", command=pause_song, **btn_cfg)
btn_pause.pack(pady=6)

btn_stop = ctk.CTkButton(
    left_frame, text="⏹  Stop", command=stop_song,
    fg_color="#C0392B", hover_color="#922B21", **btn_cfg
)
btn_stop.pack(pady=6)

btn_lyrics = ctk.CTkButton(
    left_frame, text="🎤  Generate Lyrics", command=transcribe_thread,
    fg_color="#1A6B3A", hover_color="#145229", **btn_cfg
)
btn_lyrics.pack(pady=(16, 6))

# ── right frame ───────────────────────────────────────────────
right_frame = ctk.CTkFrame(app, corner_radius=12)
right_frame.pack(side="right", fill="both", expand=True, padx=(6, 14), pady=14)

lyrics_title = ctk.CTkLabel(
    right_frame, text="Lyrics",
    font=("Helvetica", 14, "bold")
)
lyrics_title.pack(pady=(12, 4))

lyrics_box = ctk.CTkTextbox(
    right_frame,
    font=("Helvetica", 12),
    corner_radius=8,
    wrap="word",
    activate_scrollbars=True
)
lyrics_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

# start progress loop
update_progress()

app.mainloop()