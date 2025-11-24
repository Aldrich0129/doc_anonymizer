# src/handlers_pdf.py
from pathlib import Path
from io import BytesIO
import warnings
from cryptography.utils import CryptographyDeprecationWarning

# 避免 pypdf 在导入时因弃用 ARC4 发出的噪声告警
warnings.filterwarnings(
    "ignore",
    category=CryptographyDeprecationWarning,
    module="pypdf\\._crypt_providers\\._cryptography",
)

from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 使用绝对导入，避免在脚本直接运行时出现“attempted relative import”错误
from anonymizer_core import anonymize_text

def extract_pdf_text(input_path: str) -> str:
    reader = PdfReader(input_path)
    all_text = []
    for page in reader.pages:
        all_text.append(page.extract_text() or "")
    return "\n\n".join(all_text)

def create_pdf_from_text(text: str, output_path: str):
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x, y = 40, height - 40
    for line in text.split("\n"):
        if y < 40:  # 换页
            c.showPage()
            y = height - 40
        c.drawString(x, y, line[:1000])  # 简单版本
        y -= 14
    c.save()

    with open(out_path, "wb") as f:
        f.write(buffer.getvalue())

def anonymize_pdf(input_path: str, output_path: str, config_path: str):
    text = extract_pdf_text(input_path)
    new_text, _ = anonymize_text(text, config_path)
    create_pdf_from_text(new_text, output_path)
