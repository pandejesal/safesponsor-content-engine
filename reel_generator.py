import os
import math
import wave
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright
from moviepy import ImageClip, concatenate_videoclips


SCENE_DURATIONS = {
    "scene-1": 2.0,
    "scene-2": 2.5,
    "scene-3": 2.5,
    "scene-4": 2.0,
}


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


def create_sfx_wav(path, frequency=800, duration_ms=40, volume=0.2):
    samples = generate_tone(frequency, duration_ms, volume, 10)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(22050)
        f.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def create_transition_sfx(path):
    samples = generate_tone(600, 60, 0.15, 15)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(22050)
        f.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def generate_safesponsor_reel(reel_script_data, analysis_data):
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    risk_score = analysis_data.get("risk_score", 0)
    summary = analysis_data.get("summary", "Analysis complete.")
    audience_alignment = analysis_data.get("audience_alignment", "Creator Analysis")
    comment_sentiment = analysis_data.get("comment_sentiment", 88)

    transcript_flags = analysis_data.get("transcript_flags", {})
    slurs_count = transcript_flags.get("slurs_count", 0)
    policy_flags = transcript_flags.get("policy_flags_count", 0)
    profanity_count = transcript_flags.get("profanity_count", 0)

    if risk_score <= 30:
        recommendation = "Recommended: Sponsor"
        status_class = "safe"
    elif risk_score <= 60:
        recommendation = "Caution: Review Required"
        status_class = "caution"
    else:
        recommendation = "Not Recommended"
        status_class = "risky"

    fps = 15
    frames_dir = output_dir / "safesponsor_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    template_path = Path("templates/safesponsor_reel.html").resolve()
    html_content = template_path.read_text(encoding="utf-8")

    html_content = html_content.replace("{{RISK_SCORE}}", str(risk_score))
    html_content = html_content.replace("{{SLURS_COUNT}}", str(slurs_count))
    html_content = html_content.replace("{{POLICY_FLAGS}}", str(policy_flags))
    html_content = html_content.replace("{{PROFANITY_COUNT}}", str(profanity_count))
    html_content = html_content.replace("{{RECOMMENDATION}}", recommendation)
    html_content = html_content.replace("{{STATUS_CLASS}}", status_class)
    html_content = html_content.replace("{{VIDEO_TITLE}}", audience_alignment[:100])
    html_content = html_content.replace("{{SENTIMENT_PERCENT}}", str(comment_sentiment))
    html_content = html_content.replace("{{SUMMARY}}", summary[:150])

    temp_html = frames_dir / "reel.html"
    temp_html.write_text(html_content, encoding="utf-8")

    all_frame_paths = []
    frame_idx = 0

    print(f"  Rendering scenes to frames at {fps}fps...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"file:///{temp_html.resolve()}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        scene_index = 0
        for scene_id, duration in SCENE_DURATIONS.items():
            num_frames = int(duration * fps)

            page.evaluate(f"activateScene({scene_index});")
            page.wait_for_timeout(100)

            for i in range(num_frames):
                page.wait_for_timeout(int(1000 / fps))

                frame_path = frames_dir / f"frame_{frame_idx:04d}.png"
                page.screenshot(path=str(frame_path), full_page=False)
                all_frame_paths.append(str(frame_path))
                frame_idx += 1
            scene_index += 1

        page.close()
        browser.close()

    print(f"  Rendered {len(all_frame_paths)} frames across {len(SCENE_DURATIONS)} scenes")

    sfx_dir = output_dir / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    click_path = str(sfx_dir / "click.wav")
    transition_path = str(sfx_dir / "transition.wav")
    create_sfx_wav(click_path, frequency=800, duration_ms=40)
    create_transition_sfx(transition_path)

    print("  Compositing video with moviepy...")

    video_clips = []
    for frame_path in all_frame_paths:
        img_clip = ImageClip(frame_path).with_duration(1.0 / fps)
        video_clips.append(img_clip)

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

    for fp in all_frame_paths:
        if os.path.exists(fp):
            os.remove(fp)

    return {"reel": reel_path, "sfx_click": click_path, "sfx_transition": transition_path}
