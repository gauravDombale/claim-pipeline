import base64
import fitz  # PyMuPDF


def pdf_to_page_images(pdf_bytes: bytes, dpi: int = 150) -> list[dict]:
    """
    Convert each page of a PDF to a base64-encoded PNG.

    Uses PyMuPDF (fitz) which works on image-protected PDFs — it renders
    pixels directly instead of trying to extract text, so it handles
    scanned / image-only PDFs perfectly.

    Returns:
        [{"page_number": 1, "base64_image": "<base64_png_string>"}, ...]
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []

    mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 is default PDF DPI

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat)

        # Ensure RGB (some PDFs use CMYK)
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)

        img_bytes = pix.tobytes("png")
        b64 = base64.b64encode(img_bytes).decode("utf-8")

        pages.append({
            "page_number": i + 1,  # 1-indexed
            "base64_image": b64,
        })

    doc.close()
    return pages


def filter_pages_by_types(
    page_classifications: list,
    allowed_types: list[str],
) -> list:
    """
    From the segregator's classifications, return only pages whose
    doc_type is in allowed_types.

    This is the key rule: each agent only sees its relevant pages,
    NOT the whole PDF.
    """
    return [p for p in page_classifications if p.doc_type in allowed_types]
