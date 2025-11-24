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
from reportlab.pdfbase._fontdata import standardFonts

# 使用绝对导入，避免在脚本直接运行时出现"attempted relative import"错误
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


def _get_text_width(text: str, font_name: str, font_size: float) -> float:
    """计算文本在给定字体和字号下的宽度（单位：点）。"""

    if not text:
        return 0.0

    try:
        font = pdfmetrics.getFont(font_name)
        width = 0.0
        for char in text:
            width += font.face.charWidths.get(ord(char), 500)
        return width * font_size / 1000.0
    except:
        # 如果无法获取字体信息，使用估算值（平均字符宽度）
        return len(text) * font_size * 0.6


def _fit_text_to_width(text: str, font_name: str, font_size: float, max_width: float, min_font_size: float = 4.0) -> tuple:
    """
    调整文本以适应给定宽度。

    返回: (adjusted_text, adjusted_font_size)
    - 如果文本适合，返回原始文本和字号
    - 如果不适合，尝试缩小字号
    - 如果缩小到最小字号仍不适合，截断文本
    """

    if not text or max_width <= 0:
        return text, font_size

    # 计算当前宽度
    current_width = _get_text_width(text, font_name, font_size)

    # 如果适合，直接返回
    if current_width <= max_width:
        return text, font_size

    # 尝试缩小字号
    adjusted_size = font_size * (max_width / current_width)
    if adjusted_size >= min_font_size:
        return text, adjusted_size

    # 如果缩小到最小字号仍不适合，使用最小字号并截断文本
    adjusted_size = min_font_size
    chars_that_fit = int(len(text) * max_width / current_width)
    if chars_that_fit < len(text):
        return text[:max(1, chars_that_fit - 3)] + "...", adjusted_size

    return text, adjusted_size


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
            # 使用更精确的排序和分组逻辑
            words.sort(key=lambda w: (round(w.get("top", 0), 1), w.get("x0", 0)))
            current_top = None
            line_el = None
            for word in words:
                word_top = word.get("top", 0)
                word_size = word.get("size", 10) or 10
                rounded_top = round(word_top, 1)

                # 使用固定容差值（2个点），更稳定
                tolerance = 2.0

                if current_top is None or abs(rounded_top - current_top) > tolerance:
                    line_el = ET.SubElement(page_el, "line", top=str(rounded_top))
                    current_top = rounded_top

                # 保存单词的右边界，用于后续的宽度检测
                word_x0 = word.get("x0", 0)
                word_x1 = word.get("x1", 0)
                word_width = word_x1 - word_x0
                word_bottom = word.get("bottom", 0)
                word_height = word_bottom - word_top

                ET.SubElement(
                    line_el,
                    "word",
                    x0=str(word_x0),
                    x1=str(word_x1),
                    top=str(word_top),
                    bottom=str(word_bottom),
                    width=str(word_width),
                    height=str(word_height),
                    font=_guess_font_name(word.get("fontname", "")),
                    size=str(word_size),
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

        new_tokens = [t for t in new_line.split(" ") if t]  # 过滤空token

        # 改进的Token重分配策略
        if len(new_tokens) == len(words):
            # 精确匹配，直接替换
            for idx in range(len(words)):
                words[idx].text = new_tokens[idx]

        elif len(new_tokens) < len(words):
            # token减少：分配已有的token，剩余单词设为空或保留空格
            for idx in range(len(new_tokens)):
                words[idx].text = new_tokens[idx]
            # 剩余的单词清空，以保持原有的间距
            for idx in range(len(new_tokens), len(words)):
                words[idx].text = ""

        else:
            # token增加：尽量均匀分配，避免全部堆积到最后一个词
            # 策略：将多余的token均匀分配到可用空间较大的单词上
            tokens_per_word = len(new_tokens) // len(words)
            remainder = len(new_tokens) % len(words)

            token_idx = 0
            for word_idx in range(len(words)):
                # 基础分配
                tokens_to_assign = tokens_per_word
                # 将余数分配给前面的单词
                if word_idx < remainder:
                    tokens_to_assign += 1

                # 合并多个token到一个单词
                assigned_tokens = new_tokens[token_idx:token_idx + tokens_to_assign]
                words[word_idx].text = " ".join(assigned_tokens)
                token_idx += tokens_to_assign

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
                x1 = float(word_el.get("x1", x0 + 100))  # 使用x1作为右边界
                top = float(word_el.get("top", 40))
                size = float(word_el.get("size", 10))
                font = _normalize_font(word_el.get("font", "Helvetica"))
                height_word = float(word_el.get("height", size))

                # 获取文本内容并清理
                text = (word_el.text or "").replace("\n", " ").strip()
                if not text:
                    continue

                # 计算可用宽度（考虑右边界和页面宽度）
                available_width = min(x1 - x0, width - x0 - 10)  # 留10点右边距

                # 如果没有明确的x1或宽度信息，使用默认的较大宽度
                if available_width <= 0 or (x1 - x0) < 1:
                    available_width = width - x0 - 10

                # 调整文本以适应可用宽度
                adjusted_text, adjusted_size = _fit_text_to_width(
                    text, font, size, available_width
                )

                # 改进的基线偏移计算
                # 使用字体的上升高度（ascent）来计算更精确的基线位置
                # 一般字体的基线位置约为高度的 70-75%
                baseline_offset = height_word * 0.75 if height_word else adjusted_size * 0.75

                # pdfplumber 的 top 以页面上边为 0；reportlab 原点在左下
                y = height - top - baseline_offset

                # 绘制文本
                c.setFont(font, adjusted_size)
                c.drawString(x0, y, adjusted_text[:1000])

        c.showPage()

    c.save()
    with open(out_path, "wb") as f:
        f.write(buffer.getvalue())


def anonymize_pdf(input_path: str, output_path: str, config_path: str):
    xml_root = pdf_to_xml(input_path)
    anonymized_xml = anonymize_xml(xml_root, config_path)
    xml_to_pdf(anonymized_xml, output_path)
