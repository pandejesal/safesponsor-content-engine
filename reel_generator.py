import os
import time
import math
import wave
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright
from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
)


def get_gauge_color(score: int) -> str:
    if score <= 30:
        return "#22c55e"
    elif score <= 60:
        return "#eab308"
    else:
        return "#ef4444"


def get_gauge_degrees(score: int) -> int:
    return int((score / 100) * 360)


def get_risk_status(score: int) -> str:
    if score <= 30:
        return "LOW RISK"
    elif score <= 60:
        return "MODERATE"
    else:
        return "HIGH RISK"


def get_status_class(score: int) -> str:
    if score <= 30:
        return "status-low"
    elif score <= 60:
        return "status-medium"
    else:
        return "status-high"


def generate_keyword_pills(keywords: list) -> str:
    if not keywords:
        return '<span class="keyword-pill">No flags</span>'
    return "".join(
        f'<span class="keyword-pill">{kw}</span>' for kw in keywords[:5]
    )


def generate_tone(frequency=440, duration_ms=100, volume=0.3, fade_ms=20):
    sample_rate = 22050
    num_samples = int(sample_rate * duration_ms / 1000)
    fade_samples = int(sample_rate * fade_ms / 1000)

    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        val = volume * math.sin(2 * math.pi * frequency * t)
        if i < fade_samples:
            val *= i / fade_samples
        elif i > num_samples - fade_samples:
            val *= (num_samples - i) / fade_samples
        samples.append(int(val * 32767))

    return samples


def generate_click_sound():
    return generate_tone(800, 40, 0.2, 10)


def generate_whoosh_sound():
    sample_rate = 22050
    num_samples = int(sample_rate * 200 / 1000)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        freq = 200 + (i / num_samples) * 600
        val = 0.15 * math.sin(2 * math.pi * freq * t)
        fade = 1.0 - (i / num_samples)
        val *= fade
        samples.append(int(val * 32767))
    return samples


def generate_pop_sound():
    return generate_tone(1200, 30, 0.25, 5)


def create_sfx_wav(path: str, sound_type: str):
    if sound_type == "click":
        samples = generate_click_sound()
    elif sound_type == "whoosh":
        samples = generate_whoosh_sound()
    elif sound_type == "pop":
        samples = generate_pop_sound()
    else:
        samples = generate_click_sound()

    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(22050)
        f.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def generate_safesponsor_reel(reel_script_data: dict, analysis_data: dict) -> dict:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    risk_score = analysis_data.get("risk_score", 0)
    flagged_keywords = analysis_data.get("flagged_keywords", [])
    summary = analysis_data.get("summary", "Analysis complete.")
    comment_sentiment = analysis_data.get("comment_sentiment", 88)
    audience_alignment = analysis_data.get("audience_alignment", "Creator Analysis")

    transcript_flags = analysis_data.get("transcript_flags", {})
    slurs_count = transcript_flags.get("slurs_count", 0)
    policy_flags = transcript_flags.get("policy_flags_count", 0)
    profanity_count = transcript_flags.get("profanity_count", 0)

    video_title = audience_alignment[:100] if audience_alignment else "Creator Analysis"

    gauge_color = get_gauge_color(risk_score)
    gauge_degrees = get_gauge_degrees(risk_score)
    risk_status = get_risk_status(risk_score)
    status_class = get_status_class(risk_score)

    cta_text = "Run a free creator safety audit"

    template_path = Path("templates/safesponsor_reel.html").resolve()
    html_content = template_path.read_text(encoding="utf-8")

    html_content = html_content.replace("{{VIDEO_TITLE}}", video_title)
    html_content = html_content.replace("{{RISK_SCORE}}", str(risk_score))
    html_content = html_content.replace("{{RISK_STATUS}}", risk_status)
    html_content = html_content.replace("{{STATUS_CLASS}}", status_class)
    html_content = html_content.replace("{{SUMMARY}}", summary[:150])
    html_content = html_content.replace("{{GAUGE_COLOR}}", gauge_color)
    html_content = html_content.replace("{{GAUGE_DEGREES}}", str(gauge_degrees))
    html_content = html_content.replace("{{SLURS_COUNT}}", str(slurs_count))
    html_content = html_content.replace("{{POLICY_FLAGS}}", str(policy_flags))
    html_content = html_content.replace("{{PROFANITY_COUNT}}", str(profanity_count))
    html_content = html_content.replace("{{SENTIMENT_PERCENT}}", str(comment_sentiment))
    html_content = html_content.replace("{{KEYWORDS_HTML}}", generate_keyword_pills(flagged_keywords))
    html_content = html_content.replace("{{CTA_TEXT}}", cta_text)

    frames_dir = output_dir / "safesponsor_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    temp_html = frames_dir / "safesponsor_frame.html"
    temp_html.write_text(html_content, encoding="utf-8")

    fps = 30
    total_duration = 8.0
    total_frames = int(total_duration * fps)

    print(f"  Rendering {total_frames} frames at {fps}fps with Playwright...")

    frame_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"file:///{temp_html.resolve()}")
        page.wait_for_load_state("networkidle")

        for frame_idx in range(total_frames):
            t = frame_idx / fps
            progress = frame_idx / total_frames

            page.evaluate(f"""
                const elements = document.querySelectorAll('.fade-in, .fade-in-delay-1, .fade-in-delay-2, .fade-in-delay-3, .fade-in-delay-4');
                elements.forEach(el => {{
                    el.style.animationPlayState = 'running';
                }});
            """)

            frame_path = frames_dir / f"frame_{frame_idx:04d}.png"
            page.screenshot(path=str(frame_path), full_page=False)
            frame_data.append({
                "path": str(frame_path),
                "duration": 1.0 / fps
            })

        page.close()
        browser.close()

    print(f"  Rendered {len(frame_data)} frames")

    sfx_dir = output_dir / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)

    click_path = str(sfx_dir / "click.wav")
    whoosh_path = str(sfx_dir / "whoosh.wav")
    pop_path = str(sfx_dir / "pop.wav")

    create_sfx_wav(click_path, "click")
    create_sfx_wav(whoosh_path, "whoosh")
    create_sfx_wav(pop_path, "pop")

    print("  Compositing video with moviepy...")

    video_clips = []
    for fd in frame_data:
        img_clip = ImageClip(fd["path"]).with_duration(fd["duration"])
        video_clips.append(img_clip)

    if not video_clips:
        print("  No video clips to compose")
        return {"reel": None}

    final_video = concatenate_videoclips(video_clips, method="compose")

    reel_path = str(output_dir / "safesponsor_reel.mp4")
    final_video.write_videofile(
        reel_path,
        fps=fps,
        codec="libx264",
        audio=False,
        logger=None,
    )

    for clip in video_clips:
        clip.close()
    final_video.close()

    print(f"  Reel saved: {reel_path}")

    for fd in frame_data:
        if os.path.exists(fd["path"]):
            os.remove(fd["path"])

    return {
        "reel": reel_path,
        "sfx_click": click_path,
        "sfx_whoosh": whoosh_path,
        "sfx_pop": pop_path,
    }
