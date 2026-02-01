from PIL import Image, ImageOps
import pytesseract
import sys

def ocr(image_path: str) -> str:
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((img.width * 2, img.height * 2))

    return pytesseract.image_to_string(
        img,
        lang="eng",
        config="--psm 6"
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python ocr_test.py path\\to\\menu.jpg")
        raise SystemExit(1)

    path = sys.argv[1]
    text = ocr(path)

    print("----- OCR OUTPUT START -----")
    print(text)
    print("----- OCR OUTPUT END -----")
