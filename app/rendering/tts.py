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
    from gtts import gTTS

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # gTTS doesn't handle empty strings well
    if not text or not text.strip():
        text = "..."

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)
    return output_path
