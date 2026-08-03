import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image


def generate_carousel_assets(json_data: dict) -> dict:
    """
    Generate LinkedIn carousel assets from analysis JSON data.
    
    Args:
        json_data: Analysis result containing linkedin_carousel data
        
    Returns:
        dict with paths to generated slides and PDF
    """
    carousel_data = json_data.get("linkedin_carousel", [])
    
    if not carousel_data:
        raise ValueError("No linkedin_carousel data found in JSON")
    
    output_dir = Path("output/slides")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    template_path = Path("templates/slide_template.html").resolve()
    total_slides = len(carousel_data)
    
    slide_paths = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for slide in carousel_data:
            slide_num = slide["slide"]
            title = slide["title"]
            body = slide["body"]
            
            html_content = template_path.read_text(encoding="utf-8")
            html_content = html_content.replace("{{TITLE}}", title)
            html_content = html_content.replace("{{BODY}}", body)
            html_content = html_content.replace("{{SLIDE_NUM}}", str(slide_num))
            html_content = html_content.replace("{{TOTAL_SLIDES}}", str(total_slides))
            
            temp_html = output_dir / f"temp_slide_{slide_num}.html"
            temp_html.write_text(html_content, encoding="utf-8")
            
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            page.goto(f"file:///{temp_html.resolve()}")
            page.wait_for_load_state("networkidle")
            
            slide_path = output_dir / f"slide_{slide_num}.png"
            page.screenshot(path=str(slide_path), full_page=False)
            page.close()
            
            slide_paths.append(str(slide_path))
            temp_html.unlink()
            
            print(f"  Generated slide {slide_num}/{total_slides}: {slide_path}")
        
        browser.close()
    
    pdf_path = "output/linkedin_carousel.pdf"
    _combine_slides_to_pdf(slide_paths, pdf_path)
    
    return {
        "slides": slide_paths,
        "pdf": pdf_path
    }


def _combine_slides_to_pdf(slide_paths: list, output_pdf: str):
    """Combine PNG slides into a single PDF file."""
    images = []
    
    for path in slide_paths:
        img = Image.open(path)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        images.append(img)
    
    if images:
        first_image = images[0]
        rest_images = images[1:]
        
        os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
        first_image.save(output_pdf, "PDF", save_all=True, append_images=rest_images, resolution=100.0)
        print(f"\n  Combined PDF saved: {output_pdf}")
