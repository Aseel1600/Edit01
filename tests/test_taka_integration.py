"""End-to-end test for ported taka-tales modules in OpenMontage:
- Vietnamese text normalization (vietnamese_text_formatter)
- Edge-TTS & OmniVoice TTS tools
- Subtitle Engine (faster-whisper alignment, ASS karaoke generation, Remotion captions)
"""

import sys
import pathlib

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.tool_registry import registry
from tools.audio.vietnamese_text_formatter import format_for_voice, number_to_vietnamese


def test_vietnamese_formatter():
    print("=== Testing Vietnamese Formatter ===")
    assert number_to_vietnamese(400) == "bốn trăm"
    assert number_to_vietnamese(2024) == "hai nghìn không trăm hai mươi tư"
    
    raw = "Mặt Trời lớn gấp 400x Mặt Trăng, cách xa 150 triệu km, nhiệt độ 5500°C vào ngày 8 tháng 4 năm 2024."
    formatted = format_for_voice(raw)
    print("Raw text:", raw)
    print("Formatted text:", formatted)
    assert "bốn trăm" in formatted
    assert "hai nghìn không trăm hai mươi tư" in formatted
    print(" Vietnamese Formatter Test Passed!\n")


def test_edge_tts_and_subtitles():
    print("=== Testing Edge-TTS & Subtitle Engine ===")
    registry.ensure_discovered()
    
    edge_tool = registry.get("edge_tts")
    assert edge_tool is not None
    
    out_audio = pathlib.Path("scratch/test_taka_voice.mp3")
    sample_script = "Chào mừng bạn đến với hệ sinh thái OpenMontage cùng công nghệ phụ đề Karaoke thông minh."
    
    res = edge_tool.execute({
        "text": sample_script,
        "language": "vi",
        "output_path": str(out_audio)
    })
    
    assert res.success, f"Edge TTS failed: {res.error}"
    assert out_audio.exists() and out_audio.stat().st_size > 0
    print(f" Edge-TTS generated audio: {out_audio} ({out_audio.stat().st_size} bytes)")
    
    # Test Subtitle Engine
    sub_tool = registry.get("subtitle_engine")
    assert sub_tool is not None
    
    out_ass = pathlib.Path("scratch/test_taka_voice.ass")
    sub_res = sub_tool.execute({
        "audio_path": str(out_audio),
        "transcript": sample_script,
        "preset": "viral-bold-yellow",
        "canvas_width": 1920,
        "canvas_height": 1080,
        "output_ass_path": str(out_ass)
    })
    
    assert sub_res.success, f"Subtitle Engine failed: {sub_res.error}"
    assert out_ass.exists() and out_ass.stat().st_size > 0
    print(f" Subtitle Engine generated ASS: {out_ass} ({out_ass.stat().st_size} bytes)")
    
    metadata = sub_res.data
    print(f"   - Captions count: {metadata['caption_count']}")
    print(f"   - Words count: {metadata['word_count']}")
    print(" Subtitle Engine Test Passed!\n")


if __name__ == "__main__":
    test_vietnamese_formatter()
    test_edge_tts_and_subtitles()
    print("ALL TAKA-TALES INTEGRATION TESTS PASSED SUCCESSFULLY!")
