# src/handlers_pdf.py
from pathlib import Path
from io import BytesIO
import warnings
import xml.etree.ElementTree as ET
from cryptography.utils import CryptographyDeprecationWarning

# 避免 pypdf 在导入时因弃用 ARC4 发出的噪声告警
warnings.filterwarnings(
    "ignore",
    category=CryptographyDeprecationWarning,
    module="pypdf\\._crypt_providers\\._cryptography",
)

import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics

# 使用绝对导入，避免在脚本直接运行时出现“attempted relative import”错误
from anonymizer_core import anonymize_text


def _guess_font_name(fontname: str) -> str:
    """将 PDF 中的字体映射到 reportlab 内置字体，以最大程度保留样式。"""

    font_upper = (fontname or "").upper()
    if "BOLD" in font_upper:
        return "Helvetica-Bold"
    if "ITALIC" in font_upper or "OBLIQUE" in font_upper:
        return "Helvetica-Oblique"
    return "Helvetica"


def _normalize_font(fontname: str) -> str:
    """返回一个 reportlab 已注册的字体名称，避免绘制时报错。"""

    guessed = _guess_font_name(fontname)
    if guessed in pdfmetrics.getRegisteredFontNames():
        return guessed
    return "Helvetica"


def pdf_to_xml(input_path: str) -> ET.Element:
    """使用 pdfplumber 将 PDF 转为包含位置和字体信息的 XML。"""

    root = ET.Element("document")
    with pdfplumber.open(input_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_el = ET.SubElement(
                root,
                "page",
                index=str(page_index),
                width=str(page.width),
                height=str(page.height),
            )

            words = page.extract_words(
                extra_attrs=["fontname", "size"],
            )

            # 按行聚合，确保样式和位置更贴近原文
            words.sort(key=lambda w: (round(w.get("top", 0), 1), w.get("x0", 0)))
            current_top = None
            line_el = None
            for word in words:
                rounded_top = round(word.get("top", 0), 1)
                tolerance = max(0.4, (word.get("size") or 10) * 0.15)
                if current_top is None or abs(rounded_top - current_top) > tolerance:
                    line_el = ET.SubElement(page_el, "line", top=str(rounded_top))
                    current_top = rounded_top

                ET.SubElement(
                    line_el,
                    "word",
                    x0=str(word.get("x0", 0)),
                    top=str(word.get("top", 0)),
                    width=str(word.get("x1", 0) - word.get("x0", 0)),
                    height=str(word.get("bottom", 0) - word.get("top", 0)),
                    font=_guess_font_name(word.get("fontname", "")),
                    size=str(word.get("size", 10) or 10),
                    upright=str(word.get("upright", True)),
                ).text = word.get("text", "")

    return root


def anonymize_xml(xml_root: ET.Element, config_path: str) -> ET.Element:
    """对 XML 中的每一行文本执行匿名化，同时保留样式节点。"""

    for line_el in xml_root.iter("line"):
        words = list(line_el.iter("word"))
        if not words:
            continue

        original_line = " ".join(word.text or "" for word in words)
        new_line, _ = anonymize_text(original_line, config_path)

        new_tokens = new_line.split(" ")
        # 若分词数量变化，采用最小长度部分匹配，剩余文本放入最后一个词
        min_len = min(len(words), len(new_tokens))
        for idx in range(min_len):
            words[idx].text = new_tokens[idx]

        if len(new_tokens) > len(words):
            tail_text = " ".join(new_tokens[min_len:])
            words[-1].text = f"{words[-1].text} {tail_text}".strip()
        elif len(new_tokens) < len(words):
            # 不足的词保持原文，避免空白
            for idx in range(len(new_tokens), len(words)):
                words[idx].text = words[idx].text or ""

    return xml_root


def xml_to_pdf(xml_root: ET.Element, output_path: str):
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFillColor(black)

    for page_el in xml_root.findall("page"):
        width = float(page_el.get("width", 595.2))
        height = float(page_el.get("height", 841.8))
        c.setPageSize((width, height))

        for line_el in page_el.findall("line"):
            for word_el in line_el.findall("word"):
                x0 = float(word_el.get("x0", 40))
                top = float(word_el.get("top", 40))
                size = float(word_el.get("size", 10))
                font = _normalize_font(word_el.get("font", "Helvetica"))
                height_word = float(word_el.get("height", size))

                # pdfplumber 的 top 以页面上边为 0；reportlab 原点在左下。
                baseline_offset = height_word * 0.8 if height_word else 0
                y = height - top - baseline_offset
                c.setFont(font, size)
                c.drawString(x0, y, (word_el.text or "")[:1000].replace("\n", " "))

        c.showPage()

    c.save()
    with open(out_path, "wb") as f:
        f.write(buffer.getvalue())


def anonymize_pdf(input_path: str, output_path: str, config_path: str):
    xml_root = pdf_to_xml(input_path)
    anonymized_xml = anonymize_xml(xml_root, config_path)
    xml_to_pdf(anonymized_xml, output_path)
