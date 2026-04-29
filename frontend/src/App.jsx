import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const audioRef = useRef(null);
  const activeLyricRef = useRef(null);

  useEffect(() => {
    if (activeLyricRef.current) {
      activeLyricRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [currentTime]);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    setAudioFile(file);
    setAudioUrl(URL.createObjectURL(file));
    setSegments([]);
    setCurrentTime(0);
    setIsPlaying(false);
  }

  function togglePlay() {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  }

  function handleTimeUpdate() {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  }

  function handleLoadedMetadata(e) {
    setDuration(e.target.duration);
  }

  async function handleGenerate() {
    if (!audioFile) return;
    setLoading(true);
    setSegments([]);
    try {
      const formData = new FormData();
      formData.append("file", audioFile);
      const res = await axios.post("http://localhost:8000/api/transcribe", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSegments(res.data.segments);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;
  const activeIndex = segments.findIndex(
    (seg) => currentTime >= seg.start && currentTime <= seg.end
  );

  return (
    <div className="bg-surface-container-lowest font-inter text-on-surface h-screen w-screen overflow-hidden flex flex-col items-center justify-center pt-20">
      
      {/* fisier audio ascuns */}
      {audioUrl && (
        <audio
          ref={audioRef}
          src={audioUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
          className="hidden"
        />
      )}

      <header className="fixed top-0 w-full z-50 bg-black/80 backdrop-blur-2xl border-b border-white/5 shadow-2xl flex justify-between items-center px-8 h-20">
        <div className="text-2xl font-black tracking-tight text-primary italic">SmartMusicPlayer</div>
        <div className="flex gap-4">
          <button className="text-gray-400 hover:text-primary transition-colors p-2 flex items-center justify-center">
            <span className="material-symbols-outlined">account_circle</span>
          </button>
          <button className="text-gray-400 hover:text-primary transition-colors p-2 flex items-center justify-center">
            <span className="material-symbols-outlined">settings</span>
          </button>
        </div>
      </header>

      <main className="w-full max-w-[1440px] h-[calc(100vh-80px)] flex gap-8 p-10 mx-auto">
        <aside className="w-1/3 flex flex-col gap-8 h-full">
          
          {/* drop zone */}
          <label htmlFor="file-upload" className="bg-surface-container rounded-xl p-8 border border-dashed border-outline-variant flex flex-col items-center justify-center h-48 hover:border-primary transition-colors cursor-pointer group">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant group-hover:text-primary transition-colors mb-2">upload_file</span>
            <span className="text-xl font-medium text-on-surface">{audioFile ? audioFile.name : "Drop Audio File"}</span>
            <span className="text-sm text-on-surface-variant mt-1">MP3, WAV, FLAC</span>
            <input id="file-upload" type="file" accept="audio/*" onChange={handleFileChange} className="hidden" />
          </label>

          {/* player card */}
          <div className="bg-surface-container rounded-xl p-8 flex flex-col gap-6 glow-box relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent opacity-50 pointer-events-none"></div>
            
            <div className="flex items-center gap-4 relative z-10">
              <div className="w-16 h-16 bg-surface-container-highest rounded-lg overflow-hidden flex-shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-3xl text-primary">graphic_eq</span>
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="text-lg font-medium text-on-surface truncate">{audioFile ? audioFile.name : "No Track Loaded"}</span>
                <span className="text-sm text-on-surface-variant">Local File</span>
              </div>
            </div>

            <div className="flex flex-col gap-2 mt-2 relative z-10">
              <div className="h-[2px] w-full bg-surface-container-high rounded-full relative">
                <div className="absolute left-0 top-0 h-full bg-primary rounded-full" style={{ width: `${progressPercent}%` }}></div>
                <div className="absolute top-1/2 -translate-y-1/2 w-2 h-2 bg-primary rounded-full shadow-[0_0_8px_#0AFF9D]" style={{ left: `${progressPercent}%` }}></div>
              </div>
              <div className="flex justify-between w-full text-[13px] text-on-surface-variant">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4 mt-2 relative z-10">
              <button className="text-on-surface-variant hover:text-on-surface transition-colors">
                <span className="material-symbols-outlined text-2xl">skip_previous</span>
              </button>
              <button onClick={togglePlay} disabled={!audioUrl} className="w-12 h-12 rounded-full bg-primary text-black flex items-center justify-center hover:bg-green-400 shadow-[0_0_12px_rgba(10,255,157,0.2)] transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                <span className="material-symbols-outlined text-3xl">{isPlaying ? "pause" : "play_arrow"}</span>
              </button>
              <button className="text-on-surface-variant hover:text-on-surface transition-colors">
                <span className="material-symbols-outlined text-2xl">skip_next</span>
              </button>
            </div>
          </div>

          <button onClick={handleGenerate} disabled={!audioFile || loading} className="mt-auto w-full py-4 px-6 border border-primary text-primary rounded-lg text-sm tracking-widest hover:bg-primary/10 transition-all shadow-[0_0_12px_rgba(10,255,157,0.1)] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
            <span className="material-symbols-outlined text-lg">{loading ? "hourglass_empty" : "auto_awesome"}</span>
            {loading ? "GENERATING..." : "GENERATE LYRICS"}
          </button>
        </aside>

        <section className="w-2/3 h-full relative flex flex-col justify-center px-16">
          <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-[#0A0C10] to-transparent z-10 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-[#0A0C10] to-transparent z-10 pointer-events-none"></div>
          
          <div className="h-full overflow-y-auto hide-scrollbar flex flex-col gap-6 py-32 scroll-smooth">
            {segments.length === 0 ? (
              <p className="text-[2rem] leading-tight text-on-surface-variant/30 text-center">
                {loading ? "Se analizeaza vocea..." : "Versurile se vor incarca aici."}
              </p>
            ) : (
              segments.map((seg, i) => {
                const isActive = i === activeIndex;
                return (
                  <p
                    key={i}
                    ref={isActive ? activeLyricRef : null}
                    className={`leading-tight transition-all duration-500 origin-left ${
                      isActive
                        ? "text-[3rem] font-bold glow-active transform scale-105 my-4"
                        : "text-[2rem] text-on-surface-variant/30"
                    }`}
                  >
                    {seg.text}
                  </p>
                );
              })
            )}
          </div>
        </section>
      </main>
    </div>
  );
}