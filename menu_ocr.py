from pathlib import Path
from PIL import Image, ImageOps
import pytesseract

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def ocr_single_image(image_path: Path, psm: int = 6) -> str:
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)   # fixes phone rotation
    img = img.convert("L")               # greyscale
    img = ImageOps.autocontrast(img)     # improve contrast
    img = img.resize((img.width * 2, img.height * 2))  # enlarge

    return pytesseract.image_to_string(
        img,
        lang="eng",
        config=f"--psm {psm}"
    )

def list_images(folder: Path) -> list[Path]:
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS])

def ocr_folder(folder_path: str, psm: int = 6) -> dict[str, str]:
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Not a folder: {folder}")

    images = list_images(folder)
    if not images:
        raise ValueError(f"No images found in: {folder}")

    results: dict[str, str] = {}
    for img in images:
        print(f"OCRing: {img.name}")
        results[img.name] = ocr_single_image(img, psm=psm)

    return results
