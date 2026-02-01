from pathlib import Path
from PIL import Image, ImageOps
import pytesseract

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def ocr_single_image(image_path: Path, psm: int = 6) -> str:
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((img.width * 2, img.height * 2))
    return pytesseract.image_to_string(img, lang="eng", config=f"--psm {psm}")

def main():
    folder = Path("menu.jpg")  # <- scans THIS folder automatically

    print("Working directory:", Path.cwd())
    print("Scanning folder:", folder.resolve())

    if not folder.exists() or not folder.is_dir():
        raise RuntimeError(f"Folder not found: {folder.resolve()}")

    images = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    print(f"Found {len(images)} image(s)")

    if not images:
        raise RuntimeError("No images found. Put .jpg/.png files into the folder above.")

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    for img_path in sorted(images):
        print(f"\nOCRing: {img_path.name}")
        text = ocr_single_image(img_path, psm=6)
        out_path = out_dir / f"{img_path.stem}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote: {out_path.resolve()}")

    print("\n✅ Done.")

if __name__ == "__main__":
    main()
