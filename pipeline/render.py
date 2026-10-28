"""Cut page regions into standalone vector SVGs (text converted to outlines so no fonts are needed).

Content outside the region is deleted (not just hidden) with redactions, so each SVG holds
only what it shows.
"""
import re
import pymupdf as fitz


def _isolated_page(src_doc, page_index, clip):
    tmp = fitz.open()
    tmp.insert_pdf(src_doc, from_page=page_index, to_page=page_index)
    page = tmp[0]
    W, H = page.rect.width, page.rect.height
    outside = [fitz.Rect(-50, -50, W + 50, clip.y0 - 0.5), fitz.Rect(-50, clip.y1 + 0.5, W + 50, H + 50),
               fitz.Rect(-50, clip.y0, clip.x0 - 0.5, clip.y1), fitz.Rect(clip.x1 + 0.5, clip.y0, W + 50, clip.y1)]
    for r in outside:
        if not r.is_empty:
            page.add_redact_annot(r, fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)
    return tmp


def region_pdf(src_doc, page_index, bbox):
    """A one-page PDF containing only the clipped region at its original size."""
    clip = fitz.Rect(bbox)
    tmp = _isolated_page(src_doc, page_index, clip)
    out = fitz.open()
    page = out.new_page(width=clip.width, height=clip.height)
    page.show_pdf_page(page.rect, tmp, 0, clip=clip)
    return out


def region_svg(src_doc, page_index, bbox):
    doc = region_pdf(src_doc, page_index, bbox)
    return minify(doc[0].get_svg_image(text_as_path=True))


def minify(svg):
    svg = re.sub(r'>\s+<', '><', svg)
    svg = re.sub(r'(-?\d*\.\d{3})\d+', r'\1', svg)   # 3 decimals: well below print resolution
    return svg
