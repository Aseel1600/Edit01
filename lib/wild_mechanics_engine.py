"""
wild_mechanics_engine.py
Core engine helpers for the Wild Mechanics Master Production Pipeline.
Includes:
- 4:5 Ghost Blur Filtergraph with Zero Watermarks & OLED color punch
- Smart Trimming with Whisper Sentence Boundaries & 0.8s Black Fade
- Word-Level Kinetic Karaoke Subtitles (ASS \\k tags, #FFFF00 active yellow)
- YouTube Shorts Safe-Zone Subtitle Alignment (MarginV=460)
- Top Header Branding & Curiosity Hook Titles (Y=105 / Y=165)
- Dynamic Outro CTA Generator with ElevenLabs Voice & Mixed Background Music Bed (volume=0.35)
"""

import os
import re
import json
import asyncio
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

def is_bbc_source(file_path: Path | str) -> bool:
    """Detects if a media file is from BBC based on filename prefix/tag."""
    name = Path(file_path).name.lower()
    return "bbc" in name or name.startswith("bbc_")

def get_target_durations(file_path: Path | str, requested_target: Optional[float] = None) -> tuple[float, float, float]:
    """
    Returns (hook_target_s, story_target_s, cta_target_s) matching channel benchmarks (1:01 minute):
    - BBC Source: Hook = 3.0s, Story = 55.5s, CTA = 2.5s (Total = 61.0s - 61.2s, exactly 1:01 on YouTube)
    - Non-BBC Source: Hook = 3.0s, Story = 90.0s, CTA = 2.5s (Total = 95.5s)
    """
    hook_s = 3.0
    cta_s = 2.5
    if is_bbc_source(file_path):
        story_s = 55.5 if requested_target is None or requested_target > 58.0 else requested_target
    else:
        story_s = 90.0 if requested_target is None else requested_target
    return hook_s, story_s, cta_s


def generate_cold_hook_clip(
    doc_source: Path,
    hook_title_text: str,
    output_clip_path: Path,
    hook_cut_start: float = 35.0,
    hook_cut_duration: float = 3.00,
    pitch_factor: float = 0.97
) -> Path:
    """
    Renders Act 1: Cold Action Teaser Hook (0.0s - 3.0s):
    - High-intensity clash / strike action shot extracted from footage
    - Authentic documentary roaring / river audio with pitch modulation (NO AI TTS on hook!)
    - Top branding header + Electric Yellow curiosity hook title
    - 4:5 Ghost Blur framing
    """
    temp_dir = output_clip_path.parent / "temp_hook"
    temp_dir.mkdir(parents=True, exist_ok=True)
    hook_raw = temp_dir / "hook_raw.mp4"
    hook_ass = temp_dir / "hook.ass"
    
    # 1. Cut Climax Action Snippet with Authentic Audio & Pitch Modulation
    cmd_cut = [
        "ffmpeg", "-y",
        "-ss", str(hook_cut_start),
        "-t", str(hook_cut_duration),
        "-i", str(doc_source),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-filter:a", f"asetrate=48000*{pitch_factor},atempo=1/{pitch_factor},loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "320k",
        str(hook_raw)
    ]
    subprocess.run(cmd_cut, check=True)
    
    # 2. Subtitles / Top Header
    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopBrand,Arial,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,3,0,1,3,2,8,20,20,105,1
Style: TopTitle,Impact,52,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,3,8,20,20,165,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,0:00:03.00,TopBrand,,0,0,0,,{{\\fad(100,100)}}WILD MECHANICS
Dialogue: 1,0:00:00.00,0:00:03.00,TopTitle,,0,0,0,,{{\\fad(100,100)}}{hook_title_text.upper()}
"""
    hook_ass.write_text(ass_content, encoding="utf-8")
    
    hook_filter = ghost_blur_filter(ass_file=str(hook_ass))
    cmd_render = [
        "ffmpeg", "-y",
        "-i", str(hook_raw),
        "-filter_complex", hook_filter,
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "320k",
        str(output_clip_path)
    ]
    subprocess.run(cmd_render, check=True, cwd=str(temp_dir))
    return output_clip_path
    
    return output_clip_path


def extract_high_ctr_thumbnail(video_path: Path, output_thumb_path: Path, timestamp_s: float = 1.5) -> Path:
    """
    Extracts a high-CTR 1080x1920 thumbnail from the Cold Hook frame:
    - High contrast (+12%) & saturation (+28%) boost for vivid colors
    - Unsharp mask filter for crisp detail on mobile feeds
    - High JPEG quality
    """
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp_s),
        "-i", str(video_path),
        "-vf", "scale=1080:1920,eq=contrast=1.12:saturation=1.28:brightness=-0.02,unsharp=5:5:1.0:5:5:0.0",
        "-vframes", "1",
        "-q:v", "2",
        str(output_thumb_path)
    ]
    subprocess.run(cmd, check=True)
    return output_thumb_path

# -------------------------------------------------------------
# 1. 4:5 GHOST BLUR FILTERGRAPH
# -------------------------------------------------------------
def ghost_blur_filter(ass_file: Optional[str] = None, fade_out_start: Optional[float] = None, fade_duration: float = 0.8) -> str:
    """
    Generates the official Wild Mechanics 4:5 Ghost Blur FFmpeg filtergraph.
    - Background: 1080x1920 ambient blur (boxblur=30:5, brightness=-0.08, saturation=1.15).
    - Foreground: 1080x1350 (4:5) centered at Y=285 (saturation=1.12, contrast=1.04).
    - Eliminates 100% of broadcaster corner watermarks.
    - Appends ASS subtitles and optional black fade-out.
    """
    filter_chain = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5,eq=brightness=-0.08:saturation=1.15[bgblur];"
        "[fg]scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350:(iw-1080)/2:(ih-1350)/2,eq=saturation=1.12:contrast=1.04:brightness=-0.02[fg45];"
        "[bgblur][fg45]overlay=0:285[base]"
    )
    
    post_filters = []
    if ass_file:
        escaped_ass = Path(ass_file).name.replace("'", "\\'")
        post_filters.append(f"ass='{escaped_ass}'")
        
    if fade_out_start is not None and fade_out_start > 0:
        post_filters.append(f"fade=t=out:st={fade_out_start:.2f}:d={fade_duration:.2f}")
        
    if post_filters:
        filter_chain += f";[base]{','.join(post_filters)}[v]"
    else:
        filter_chain += ";[base]copy[v]"
        
    return filter_chain


# -------------------------------------------------------------
# 2. AUDIO PITCH & FADE FILTER
# -------------------------------------------------------------
def audio_pitch_and_fade_filter(fade_out_start: Optional[float] = None, fade_duration: float = 0.8, pitch_factor: float = 0.97) -> str:
    """
    Applies subtle pitch modulation (anti-Content-ID) and optional audio fade out.
    """
    atempo = 1.0 / pitch_factor
    f = f"asetrate=48000*{pitch_factor:.3f},atempo={atempo:.3f},highpass=f=60,lowpass=f=16000"
    if fade_out_start is not None and fade_out_start > 0:
        f += f",afade=t=out:st={fade_out_start:.2f}:d={fade_duration:.2f}"
    f += ",loudnorm=I=-14:TP=-1.5:LRA=11"
    return f


# -------------------------------------------------------------
# 3. ASS KINETIC KARAOKE & HEADER GENERATOR
# -------------------------------------------------------------
def build_ass_subtitles(
    segments: List[Any],
    output_path: Path,
    title_hook: str,
    action_badges: Optional[List[Dict[str, Any]]] = None,
    max_duration: Optional[float] = None,
) -> Path:
    """
    Builds the official Wild Mechanics ASS subtitle file:
    - TopBrand: WILD MECHANICS (Diamond White, Y=105)
    - TopTitle: Curiosity Hook (Electric Yellow, Y=165)
    - BottomKaraoke: Word-level kinetic karaoke (\k tags, #FFFF00 active) at Safe Zone (MarginV=460 / Y~1460)
    - MidBadge: Action badges timed to peak moments
    """
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopBrand,Arial,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,3,0,1,3,2,8,20,20,105,1
Style: TopTitle,Impact,52,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,3,8,20,20,165,1
Style: MidBadge,Impact,64,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,5,20,20,0,1
Style: BottomKaraoke,Impact,58,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,40,40,460,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    
    # End time for persistent headers
    end_s = max_duration if max_duration else 95.0
    end_h = int(end_s // 3600)
    end_m = int((end_s % 3600) // 60)
    end_sec = int(end_s % 60)
    end_cs = int((end_s - int(end_s)) * 100)
    end_time_str = f"{end_h}:{end_m:02d}:{end_sec:02d}.{end_cs:02d}"
    
    events.append(f"Dialogue: 1,0:00:00.00,{end_time_str},TopBrand,,0,0,0,,{{\\fad(200,400)}}WILD MECHANICS")
    events.append(f"Dialogue: 1,0:00:00.00,{end_time_str},TopTitle,,0,0,0,,{{\\fad(200,400)}}{title_hook}")
    
    # Action Badges
    if action_badges:
        for badge in action_badges:
            b_text = badge["text"]
            b_st = badge["start"]
            b_en = badge["end"]
            st_str = format_ass_time(b_st)
            en_str = format_ass_time(b_en)
            events.append(f"Dialogue: 2,{st_str},{en_str},MidBadge,,0,0,0,,{{\\fad(300,300)}}{b_text}")
            
    # Word-level karaoke chunks
    for seg in segments:
        words = seg.words if hasattr(seg, "words") and seg.words else []
        if not words:
            continue
        chunk_size = 5
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i+chunk_size]
            if not chunk:
                continue
            c_start = chunk[0].start
            c_end = chunk[-1].end
            if max_duration and c_start >= max_duration - 0.5:
                continue
            if max_duration:
                c_end = min(max_duration - 0.5, c_end)
                
            k_text = ""
            for w in chunk:
                dur_cs = max(1, int(round((w.end - w.start) * 100)))
                clean_w = w.word.strip().upper()
                k_text += f"{{\\k{dur_cs}}}{clean_w} "
                
            start_str = format_ass_time(c_start)
            end_str = format_ass_time(c_end)
            events.append(f"Dialogue: 0,{start_str},{end_str},BottomKaraoke,,0,0,0,,{k_text.strip()}")
            
    output_path.write_text(ass_header + "\n".join(events) + "\n", encoding="utf-8")
    return output_path


def format_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


# -------------------------------------------------------------
# 4. DYNAMIC OUTRO CTA SYNTHESIS (ELEVENLABS + BOOSTED BGM)
# -------------------------------------------------------------
def generate_dynamic_cta_clip(
    animal_name: str,
    stock_bg_video: Path,
    output_clip_path: Path,
    bgm_track: Optional[Path] = None,
    whisper_model: Any = None,
    bgm_volume: float = 0.35,  # Increased volume for punchy background presence
) -> Path:
    """
    Renders the official dynamic Outro CTA:
    - ElevenLabs channel voice from .env (Voice ID: 3zYzgGucDBahVReFU64R)
    - Mixed background music bed (volume=0.35 / -13dB with smooth fade-in/out)
    - Centered bold Electric Yellow kinetic text bursts (FOLLOW -> WILD MECHANICS -> FOR MORE)
    """
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    eleven_voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "3zYzgGucDBahVReFU64R")
    
    cta_script = "Nature is full of hidden biological superpowers, just like this one. Follow Wild Mechanics for more."
    temp_dir = output_clip_path.parent / "temp_cta"
    temp_dir.mkdir(parents=True, exist_ok=True)
    voice_audio = temp_dir / f"cta_voice_{animal_name}.mp3"
    
    # 1. Voice Synthesis (ElevenLabs -> Speechify Fallback)
    headers = {"xi-api-key": eleven_key, "Content-Type": "application/json"}
    data = {
        "text": cta_script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{eleven_voice_id}", json=data, headers=headers)
    if res.status_code == 200:
        voice_audio.write_bytes(res.content)
    else:
        print(f"[CTA] ElevenLabs status {res.status_code}. Using Speechify fallback...")
        speechify_key = os.environ.get("SPEECHIFY_API_KEY")
        speechify_voice = os.environ.get("SPEECHIFY_VOICE_ID", "beatrice_32")
        s_headers = {"Authorization": f"Bearer {speechify_key}", "Content-Type": "application/json"}
        s_data = {"input": f"<speak>{cta_script}</speak>", "voice_id": speechify_voice, "audio_format": "mp3"}
        s_res = requests.post("https://api.sws.speechify.com/v1/audio/speech", json=s_data, headers=s_headers)
        if s_res.status_code == 200:
            voice_audio.write_bytes(s_res.json().get("audio_data", b""))
            
    # 2. Subtitle Burst Generation
    from faster_whisper import WhisperModel
    if whisper_model is None:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        
    cta_segments, _ = whisper_model.transcribe(str(voice_audio), word_timestamps=True)
    cta_ass = temp_dir / "cta_burst.ass"
    
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CenterWord,Impact,72,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,3,5,40,40,0,1
Style: WhiteWord,Impact,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    cta_events = []
    for seg in cta_segments:
        words = seg.words if hasattr(seg, "words") and seg.words else []
        chunk_size = 2
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i+chunk_size]
            if not chunk:
                continue
            c_start = chunk[0].start
            c_end = chunk[-1].end
            txt = " ".join([w.word.strip().upper() for w in chunk])
            style = "CenterWord" if any(k in txt for k in ["WILD", "MECHANICS", "SUPERPOWERS", "MORE"]) else "WhiteWord"
            start_str = format_ass_time(c_start)
            end_str = format_ass_time(c_end)
            cta_events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{txt}")
            
    cta_ass.write_text(ass_header + "\n".join(cta_events) + "\n", encoding="utf-8")
    
    # 3. Render with BGM
    if bgm_track is None or not Path(bgm_track).exists():
        bgm_track = ROOT_DIR / "assets" / "audio" / "bgm" / "nature_suspense_bgm.wav"
        
    escaped_ass = cta_ass.name.replace("'", "\\'")
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fade=t=in:st=0.0:d=0.3,eq=brightness=-0.10:contrast=1.05:saturation=1.12[bg];"
        f"[bg]ass='{escaped_ass}'[v];"
        f"[2:a]volume={bgm_volume:.2f},afade=t=in:st=0.0:d=0.3,afade=t=out:st=2.5:d=0.5[bgm];"
        "[1:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0.5",
        "-i", str(stock_bg_video),
        "-i", str(voice_audio),
        "-i", str(bgm_track),
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "320k",
        "-shortest",
        str(output_clip_path)
    ]
    subprocess.run(cmd, check=True, cwd=str(temp_dir))
    return output_clip_path
