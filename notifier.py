import os
import requests
from dotenv import load_dotenv


def send_to_telegram(pdf_path: str, twitter_thread: list, instagram_caption: str, reel_path: str = None) -> bool:
    """
    Send content to Telegram chat via Bot API.
    
    Args:
        pdf_path: Path to the LinkedIn carousel PDF
        twitter_thread: List of tweet strings
        instagram_caption: Instagram caption text
        reel_path: Path to the video reel (optional)
        
    Returns:
        bool: True if all messages sent successfully, False otherwise
    """
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or bot_token == "your_bot_token":
        print("  Telegram: No valid bot token configured, skipping notification")
        return False
    
    if not chat_id or chat_id == "your_chat_id":
        print("  Telegram: No valid chat ID configured, skipping notification")
        return False
    
    api_base = f"https://api.telegram.org/bot{bot_token}"
    success = True
    
    # Send PDF document
    try:
        with open(pdf_path, "rb") as pdf_file:
            files = {"document": ("linkedin_carousel.pdf", pdf_file, "application/pdf")}
            data = {"chat_id": chat_id, "caption": "LinkedIn Carousel PDF"}
            response = requests.post(f"{api_base}/sendDocument", files=files, data=data)
            
            if response.status_code == 200:
                print("  Telegram: PDF sent successfully")
            else:
                print(f"  Telegram: PDF send failed - {response.text}")
                success = False
    except Exception as e:
        print(f"  Telegram: PDF send error - {e}")
        success = False
    
    # Send Video Reel
    if reel_path and os.path.exists(reel_path):
        try:
            with open(reel_path, "rb") as video_file:
                files = {"video": ("reel.mp4", video_file, "video/mp4")}
                data = {"chat_id": chat_id, "caption": "Video Reel"}
                response = requests.post(f"{api_base}/sendVideo", files=files, data=data)
                
                if response.status_code == 200:
                    print("  Telegram: Video reel sent successfully")
                else:
                    print(f"  Telegram: Video reel send failed - {response.text}")
                    success = False
        except Exception as e:
            print(f"  Telegram: Video reel send error - {e}")
            success = False
    
    # Send Twitter thread
    try:
        thread_text = format_twitter_thread(twitter_thread)
        data = {"chat_id": chat_id, "text": thread_text}
        response = requests.post(f"{api_base}/sendMessage", data=data)
        
        if response.status_code == 200:
            print("  Telegram: Twitter thread sent successfully")
        else:
            print(f"  Telegram: Twitter thread send failed - {response.text}")
            success = False
    except Exception as e:
        print(f"  Telegram: Twitter thread send error - {e}")
        success = False
    
    # Send Instagram caption
    try:
        data = {"chat_id": chat_id, "text": f"Instagram Caption:\n\n{instagram_caption}"}
        response = requests.post(f"{api_base}/sendMessage", data=data)
        
        if response.status_code == 200:
            print("  Telegram: Instagram caption sent successfully")
        else:
            print(f"  Telegram: Instagram caption send failed - {response.text}")
            success = False
    except Exception as e:
        print(f"  Telegram: Instagram caption send error - {e}")
        success = False
    
    return success


def format_twitter_thread(twitter_thread: list) -> str:
    """Format Twitter thread for clean Telegram display."""
    lines = ["Twitter Thread:"]
    lines.append("=" * 30)
    
    for i, tweet in enumerate(twitter_thread, 1):
        lines.append(f"\nTweet {i}:")
        lines.append(tweet)
    
    return "\n".join(lines)
