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


async def generate_voiceover(text: str, output_path: str, voice: str = "en-US-ChristopherNeural"):
    """Generate AI voiceover using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_reel(reel_script_data: dict, analysis_data: dict) -> dict:
    """
    Generate a 9:16 vertical video reel.
    
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
    
    voiceover_path = str(output_dir / "voiceover.mp3")
    print("  Generating AI voiceover...")
    asyncio.run(generate_voiceover(full_script, voiceover_path))
    print(f"  Voiceover saved: {voiceover_path}")
    
    risk_score = analysis_data.get("risk_score", 0)
    risk_level = analysis_data.get("risk_level", "LOW")
    flagged_keywords = analysis_data.get("flagged_keywords", [])
    
    if risk_score <= 30:
        risk_color = "#10b981"
    elif risk_score <= 60:
        risk_color = "#f59e0b"
    else:
        risk_color = "#ef4444"
    
    keywords_html = ""
    for kw in flagged_keywords[:5]:
        keywords_html += f'<span class="bg-red-500/20 text-red-400 px-4 py-2 rounded-full text-lg">{kw}</span>'
    if not keywords_html:
        keywords_html = '<span class="bg-green-500/20 text-green-400 px-4 py-2 rounded-full text-lg">No issues found</span>'
    
    template_path = Path("templates/reel_template.html").resolve()
    html_content = template_path.read_text(encoding="utf-8")
    html_content = html_content.replace("{{RISK_SCORE}}", str(risk_score))
    html_content = html_content.replace("{{RISK_LEVEL}}", risk_level)
    html_content = html_content.replace("{{RISK_COLOR}}", risk_color)
    html_content = html_content.replace("{{KEYWORDS_HTML}}", keywords_html)
    
    slides_dir = output_dir / "reel_frames"
    slides_dir.mkdir(parents=True, exist_ok=True)
    
    temp_html = slides_dir / "reel_frame.html"
    temp_html.write_text(html_content, encoding="utf-8")
    
    print("  Rendering video frames with Playwright...")
    frame_paths = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        scripts = [hook, body, cta]
        durations = [5, 20, 5]
        
        for i, (script_text, duration) in enumerate(zip(scripts, durations)):
            current_html = html_content.replace("{{SCRIPT_TEXT}}", script_text)
            temp_html.write_text(current_html, encoding="utf-8")
            
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.goto(f"file:///{temp_html.resolve()}")
            page.wait_for_load_state("networkidle")
            
            frame_path = slides_dir / f"frame_{i}.png"
            page.screenshot(path=str(frame_path), full_page=False)
            page.close()
            
            frame_paths.append((str(frame_path), duration))
            print(f"    Frame {i+1}/3 rendered ({duration}s)")
        
        browser.close()
    
    print("  Compositing video with moviepy...")
    
    audio_clip = AudioFileClip(voiceover_path)
    
    video_clips = []
    for frame_path, duration in frame_paths:
        img_clip = ImageClip(frame_path).with_duration(duration)
        video_clips.append(img_clip)
    
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    final_video = final_video.with_audio(audio_clip)
    
    reel_path = str(output_dir / "reel.mp4")
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
    
    for frame_path, _ in frame_paths:
        if os.path.exists(frame_path):
            os.remove(frame_path)
    
    return {
        "reel": reel_path,
        "voiceover": voiceover_path
    }
