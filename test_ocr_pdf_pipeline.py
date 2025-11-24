"""测试基于OCR的PDF匿名化流程，验证版式保留。"""
from pathlib import Path
import sys

import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pytest
import shutil

sys.path.insert(0, str(Path(__file__).parent / "src"))
from handlers_pdf import anonymize_pdf


def _create_sample_pdf(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 50, "Cliente: Ayuntamiento de Barcelona")
    c.drawString(50, height - 70, "Correo: demo@example.com")
    c.drawString(50, height - 90, "Teléfono: +34 612345678")
    c.save()


def test_ocr_anonymization_preserves_layout(tmp_path: Path):
    if shutil.which("tesseract") is None:
        pytest.skip("tesseract 未安装，跳过 OCR 测试")

    input_pdf = tmp_path / "ocr_input.pdf"
    output_pdf = tmp_path / "ocr_output.pdf"
    config_path = Path(__file__).parent / "config" / "rules.yaml"

    _create_sample_pdf(input_pdf)

    anonymize_pdf(str(input_pdf), str(output_pdf), str(config_path), use_ocr=True)

    assert output_pdf.exists(), "输出文件未生成"
    assert output_pdf.stat().st_size > 0, "输出文件为空"

    with pdfplumber.open(output_pdf) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    assert "Ayuntamiento de Barcelona" not in text
    assert "Entidad Pública" in text
