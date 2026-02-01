import sys
from pathlib import Path
from typing import List, Dict
from PIL import Image, ImageOps
import pytesseract
from pytesseract import TesseractNotFoundError

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def ocr_single_image(image_path: Path, psm: int = 6) -> str:
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((img.width * 2, img.height * 2))
    
    try:
        return pytesseract.image_to_string(img, lang="eng", config=f"--psm {psm}")
    except TesseractNotFoundError:
        print("\n❌ ERROR: Tesseract OCR is not installed!")
        print("\nPlease install Tesseract:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS:         brew install tesseract")
        print("  Fedora/RHEL:   sudo dnf install tesseract")
        print("\nThen verify with: tesseract --version")
        raise

def process_menu_images(folder_path: str = "menu.jpg", output_dir: str = "outputs") -> Dict[str, any]:
    """
    Process all images in a folder using OCR.
    
    Args:
        folder_path: Path to folder containing menu images (default: "menu.jpg")
        output_dir: Directory to save OCR output text files (default: "outputs")
    
    Returns:
        Dictionary containing:
            - "processed_files": List of processed image filenames
            - "output_files": List of output text file paths
            - "output_dir": Path to output directory
    """
    folder = Path(folder_path)

    print("Working directory:", Path.cwd())
    print("Scanning folder:", folder.resolve())

    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder.resolve()}")

    images = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    print(f"Found {len(images)} image(s)")

    if not images:
        raise FileNotFoundError("No images found. Put .jpg/.png files into the folder above.")

    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    processed_files = []
    output_files = []

    for img_path in sorted(images):
        print(f"\nOCRing: {img_path.name}")
        text = ocr_single_image(img_path, psm=6)
        out_path = out_dir / f"{img_path.stem}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote: {out_path.resolve()}")
        
        processed_files.append(img_path.name)
        output_files.append(str(out_path.resolve()))

    print("\n✅ Done.")
    
    return {
        "processed_files": processed_files,
        "output_files": output_files,
        "output_dir": str(out_dir.resolve())
    }


def main():
    """Command-line entry point."""
    # Accept optional folder path as first argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        folder = sys.argv[1]
    else:
        folder = "menu.jpg"
    
    process_menu_images(folder)


if __name__ == "__main__":
    main()
