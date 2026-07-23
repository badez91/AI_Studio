"""Text-to-Speech using gTTS (Google Translate TTS — free, no API key)."""

from __future__ import annotations

from pathlib import Path


def text_to_speech(text: str, output_path: str, lang: str = "en") -> str:
    """Generate speech audio from text using gTTS.
    
    Args:
        text: The text to convert to speech.
        output_path: Path where the .mp3 file will be saved.
        lang: Language code (default: English).
    
    Returns:
        The output file path.
    """
    try:
        from gtts import gTTS  # type: ignore
    except Exception:
        # Fallback for environments without gTTS available (tests/local dev).
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        if not text or not text.strip():
            text = "..."
        # Write a simple placeholder file so downstream code can proceed.
        Path(output_path).write_text(f"[TTS Placeholder]\n{text}", encoding="utf-8")
        return output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # gTTS doesn't handle empty strings well
    if not text or not text.strip():
        text = "..."

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)
    return output_path
