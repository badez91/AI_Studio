"""Video composition using FFmpeg — creates animated video with Ken Burns effect."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def compose_video(
    scenes: list[dict[str, Any]],
    output_path: str,
    fps: int = 30,
) -> str:
    """Compose a video from scene images and audio with Ken Burns (pan/zoom) animation.
    
    Each scene dict should have:
        - image_path: str — path to the scene image (.png)
        - audio_path: str — path to the narration audio (.mp3)
        - duration: float — scene duration in seconds
    
    Args:
        scenes: List of scene dictionaries.
        output_path: Path where the final .mp4 will be saved.
        fps: Frames per second for the output video.
    
    Returns:
        The output video file path.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    if not scenes:
        raise ValueError("No scenes provided for video composition.")

    temp_dir = Path(output_path).parent / "_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    segment_files = []

    for idx, scene in enumerate(scenes):
        image_path = str(Path(scene["image_path"]).resolve())
        audio_path = str(Path(scene["audio_path"]).resolve())
        duration = scene.get("duration", 5)
        
        segment_path = str(temp_dir / f"segment_{idx:03d}.mp4")
        
        # Ken Burns effect: alternate between zoom-in and pan
        # zoompan filter creates smooth animation from a still image
        if idx % 3 == 0:
            # Slow zoom in
            zp = f"zoompan=z='min(zoom+0.002,1.3)':d={duration * fps}:s=1280x720:fps={fps}"
        elif idx % 3 == 1:
            # Slow zoom out
            zp = f"zoompan=z='if(eq(on,1),1.3,max(zoom-0.002,1.0))':d={duration * fps}:s=1280x720:fps={fps}"
        else:
            # Slow pan left to right
            zp = f"zoompan=z='1.1':x='iw/2-(iw/zoom/2)+((iw/zoom)*on/{duration * fps}*0.3)':d={duration * fps}:s=1280x720:fps={fps}"

        cmd = [
            "ffmpeg", "-y",
            "-i", image_path,
            "-i", audio_path,
            "-filter_complex",
            f"[0:v]{zp},fade=t=in:st=0:d=0.5,fade=t=out:st={max(duration-0.5, 0.1)}:d=0.5[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-t", str(duration),
            segment_path,
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg segment {idx} failed: {result.stderr[:500]}")
        
        segment_files.append(segment_path)

    # Concatenate all segments with crossfade transitions
    if len(segment_files) == 1:
        # Single segment, just copy
        import shutil
        shutil.copy2(segment_files[0], output_path)
    else:
        # Concatenate with brief crossfade between segments
        concat_list_path = str(temp_dir / "concat.txt")
        with open(concat_list_path, "w") as f:
            for seg in segment_files:
                abs_seg = str(Path(seg).resolve())
                f.write(f"file '{abs_seg}'\n")

        abs_output = str(Path(output_path).resolve())
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "128k",
            abs_output,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg concat failed (exit {result.returncode}): {result.stderr[:500]}")

    # Clean up temp files
    for seg in segment_files:
        Path(seg).unlink(missing_ok=True)
    concat_txt = temp_dir / "concat.txt"
    if concat_txt.exists():
        concat_txt.unlink()
    try:
        temp_dir.rmdir()
    except OSError:
        pass

    return output_path
