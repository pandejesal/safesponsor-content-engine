import asyncio
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import edge_tts
from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
)


async def generate_voiceover_with_timestamps(text: str, output_path: str, voice: str = "en-US-ChristopherNeural"):
    """Generate AI voiceover and return word timestamps."""
    communicate = edge_tts.Communicate(text, voice)
    word_timestamps = []
    
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_timestamps.append({
                    "text": chunk["text"],
                    "offset": chunk["offset"] / 10_000_000,
                    "duration": chunk["duration"] / 10_000_000
                })
    
    return word_timestamps


def create_fallback_timestamps(text: str, total_duration: float) -> list:
    """Create fallback timestamps by splitting text evenly across duration."""
    words = text.split()
    if not words:
        return []
    
    time_per_word = total_duration / len(words)
    timestamps = []
    
    for i, word in enumerate(words):
        timestamps.append({
            "text": word,
            "offset": i * time_per_word,
            "duration": time_per_word
        })
    
    return timestamps


def get_score_degrees(score: int) -> int:
    """Calculate degrees for score ring conic gradient."""
    return int((score / 100) * 360)


def get_risk_status(score: int) -> str:
    """Get risk status label based on score."""
    if score <= 30:
        return "SAFE"
    elif score <= 60:
        return "MODERATE"
    else:
        return "HIGH RISK"


def generate_keyword_pills(keywords: list) -> str:
    """Generate HTML for keyword pills."""
    pills_html = ""
    
    for kw in keywords[:3]:
        pills_html += f'<span class="keyword-pill">{kw}</span>'
    
    if not keywords:
        pills_html = '<span class="keyword-pill" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.4); color: #6ee7b7;">Clean</span>'
    
    return pills_html


def generate_subtitle_html(words: list, active_index: int) -> str:
    """Generate HTML for kinetic subtitles with active word highlighted."""
    html = ""
    for i, word in enumerate(words):
        if i == active_index:
            html += f'<span class="subtitle-word active">{word}</span>'
        elif i < active_index:
            html += f'<span class="subtitle-word spoken">{word}</span>'
        else:
            html += f'<span class="subtitle-word">{word}</span>'
    return html


def generate_ensotrade_reel(reel_script_data: dict, analysis_data: dict) -> dict:
    """
    Generate an EnsoTrade-style dark mode vertical video reel.
    
    Args:
        reel_script_data: Object with hook, body, cta
        analysis_data: Full analysis data for risk score display
        
    Returns:
        dict with path to generated reel
    """
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    hook = reel_script_data.get("hook", "")
    body = reel_script_data.get("body", "")
    cta = reel_script_data.get("cta", "")
    
    full_script = f"{hook} {body} {cta}"
    
    voiceover_path = str(output_dir / "safesponsor_voiceover.mp3")
    print("  Generating AI voiceover with timestamps...")
    word_timestamps = asyncio.run(
        generate_voiceover_with_timestamps(full_script, voiceover_path)
    )
    print(f"  Voiceover saved: {voiceover_path}")
    
    audio_clip = AudioFileClip(voiceover_path)
    total_duration = audio_clip.duration
    
    if not word_timestamps:
        print("  No word timestamps captured, creating fallback timestamps...")
        word_timestamps = create_fallback_timestamps(full_script, total_duration)
    
    print(f"  Using {len(word_timestamps)} word timestamps")
    
    risk_score = analysis_data.get("risk_score", 0)
    flagged_keywords = analysis_data.get("flagged_keywords", [])
    video_title = analysis_data.get("summary", "Video Analysis")[:80]
    
    score_degrees = get_score_degrees(risk_score)
    risk_status = get_risk_status(risk_score)
    
    template_path = Path("templates/ensotrade_reel.html").resolve()
    html_content = template_path.read_text(encoding="utf-8")
    
    html_content = html_content.replace("{{SCORE_DEGREES}}", str(score_degrees))
    html_content = html_content.replace("{{VIDEO_TITLE}}", video_title)
    html_content = html_content.replace("{{RISK_SCORE}}", str(risk_score))
    html_content = html_content.replace("{{RISK_STATUS}}", risk_status)
    html_content = html_content.replace("{{KEYWORDS_HTML}}", generate_keyword_pills(flagged_keywords))
    
    all_words = []
    for ts in word_timestamps:
        words = ts["text"].split()
        all_words.extend(words)
    
    initial_subtitle = generate_subtitle_html(all_words, -1)
    html_content = html_content.replace("{{SUBTITLE_WORDS}}", initial_subtitle)
    
    frames_dir = output_dir / "ensotrade_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    temp_html = frames_dir / "ensotrade_frame.html"
    temp_html.write_text(html_content, encoding="utf-8")
    
    print("  Rendering animated frames with Playwright...")
    
    frame_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"file:///{temp_html.resolve()}")
        page.wait_for_load_state("networkidle")
        
        for word_idx, word_ts in enumerate(word_timestamps):
            offset = word_ts["offset"]
            duration = word_ts["duration"]
            
            subtitle_html = generate_subtitle_html(all_words, word_idx)
            
            page.evaluate(f"""
                document.getElementById('kinetic-subtitles').innerHTML = `{subtitle_html}`;
            """)
            
            frame_path = frames_dir / f"frame_{len(frame_data):04d}.png"
            page.screenshot(path=str(frame_path), full_page=False)
            
            frame_data.append({
                "path": str(frame_path),
                "start": offset,
                "duration": duration
            })
        
        page.close()
        browser.close()
    
    print(f"  Rendered {len(frame_data)} frames")
    
    print("  Compositing video with moviepy...")
    
    video_clips = []
    
    if frame_data and frame_data[0]["start"] > 0:
        intro_clip = ImageClip(str(frame_data[0]["path"])).with_duration(frame_data[0]["start"])
        video_clips.append(intro_clip)
    
    for fd in frame_data:
        img_clip = ImageClip(fd["path"]).with_duration(fd["duration"])
        video_clips.append(img_clip)
    
    if frame_data:
        last_end = frame_data[-1]["start"] + frame_data[-1]["duration"]
        if last_end < total_duration:
            outro_clip = ImageClip(str(frame_data[-1]["path"])).with_duration(total_duration - last_end)
            video_clips.append(outro_clip)
    
    if not video_clips:
        print("  No video clips to compose, creating static clip...")
        static_clip = ImageClip(str(frame_data[0]["path"])).with_duration(total_duration) if frame_data else None
        if static_clip:
            video_clips.append(static_clip)
    
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video = final_video.with_audio(audio_clip)
    
    reel_path = str(output_dir / "safesponsor_reel.mp4")
    final_video.write_videofile(
        reel_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        temp_audiofile=str(output_dir / "temp_audio.m4a"),
        remove_temp=True
    )
    
    audio_clip.close()
    for clip in video_clips:
        clip.close()
    final_video.close()
    
    print(f"  Reel saved: {reel_path}")
    
    for fd in frame_data:
        if os.path.exists(fd["path"]):
            os.remove(fd["path"])
    
    return {
        "reel": reel_path,
        "voiceover": voiceover_path,
        "word_timestamps": word_timestamps
    }
