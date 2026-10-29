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


USE_LIMIT = 900        # Cloudinary rejects SVGs with 1000+ <use> elements ("Resource is invalid")


def minify(svg):
    svg = re.sub(r'>\s+<', '><', svg)
    svg = re.sub(r'(-?\d*\.\d{3})\d+', r'\1', svg)   # 3 decimals: well below print resolution
    return limit_uses(svg)


def limit_uses(svg):
    """Text-as-path SVGs draw every letter as <use href="#glyph">. Drop uses of empty glyphs (spaces);
    if still too many for Cloudinary, write each glyph's path inline instead (same picture, bigger file)."""
    glyphs = dict(re.findall(r'<path id="([^"]+)" d="([^"]*)"/>', svg))
    empty = {k for k, d in glyphs.items() if not d.strip()}
    use_re = re.compile(r'<use ([^>]*?)xlink:href="#([^"]+)"([^>]*)/>')
    if empty:
        svg = use_re.sub(lambda m: '' if m.group(2) in empty else m.group(0), svg)
    if svg.count('<use') < USE_LIMIT:
        return svg

    def inline(m):
        d = glyphs.get(m.group(2))
        if d is None:
            return m.group(0)
        return f'<path {m.group(1)}{m.group(3).strip()} d="{d}"/>'.replace('  ', ' ')
    return use_re.sub(inline, svg)
