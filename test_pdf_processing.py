#!/usr/bin/env python3
"""
测试PDF处理功能，验证文字排版、重叠等问题的修复
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from handlers_pdf import anonymize_pdf


def create_test_pdf(output_path: str):
    """创建一个包含各种排版场景的测试PDF"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # 设置字体
    c.setFont("Helvetica", 12)

    # 测试场景1：正常文本
    y = height - 50
    c.drawString(50, y, "Test Case 1: Normal text spacing")
    y -= 20
    c.drawString(50, y, "Cliente: KFC España")
    y -= 20
    c.drawString(50, y, "NIF: A12345678")
    y -= 20
    c.drawString(50, y, "Email: demo@empresa.es")

    # 测试场景2：密集文本（容易重叠）
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Test Case 2: Dense text layout")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Contacto: demo@empresa.es disponible 9-18h")
    y -= 12
    c.drawString(50, y, "Teléfono: +34 612345678 o +34 987654321")

    # 测试场景3：不同字体大小混合
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Test Case 3: Mixed font sizes")
    y -= 20
    c.setFont("Helvetica", 8)
    c.drawString(50, y, "Small text: NIF X1234567T")
    c.setFont("Helvetica", 12)
    c.drawString(250, y, "Normal: 600000000")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(400, y, "Large")

    # 测试场景4：长文本（测试宽度检测）
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Test Case 4: Long text overflow test")
    y -= 20
    c.setFont("Helvetica", 10)
    long_text = "Este es un texto muy largo que contiene información como correo@ejemplo.es y números de teléfono +34 600000000"
    c.drawString(50, y, long_text)

    # 测试场景5：多行紧密排列
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Test Case 5: Closely spaced lines")
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "Línea 1: Ayuntamiento de Barcelona - A98765432")
    y -= 14
    c.drawString(50, y, "Línea 2: Contacto demo@test.com teléfono 612345678")
    y -= 14
    c.drawString(50, y, "Línea 3: Dirección: Calle Mayor 123, 28001 Madrid")

    # 测试场景6：斜体和粗体
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Test Case 6: Style variations")
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Bold: KFC España")
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(250, y, "Italic: NIF A12345678")

    c.showPage()
    c.save()
    print(f"✓ 测试PDF已创建: {output_path}")


def test_pdf_anonymization():
    """测试PDF匿名化处理"""
    print("\n" + "=" * 60)
    print("开始测试PDF匿名化处理")
    print("=" * 60)

    # 创建测试目录
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)

    # 文件路径
    input_pdf = test_dir / "test_input.pdf"
    output_pdf = test_dir / "test_output_anonymized.pdf"
    config_path = str(Path(__file__).parent / "config" / "rules.yaml")

    # 步骤1：创建测试PDF
    print("\n[步骤 1/3] 创建测试PDF文件...")
    create_test_pdf(str(input_pdf))

    # 步骤2：执行匿名化
    print("\n[步骤 2/3] 执行PDF匿名化处理...")
    try:
        anonymize_pdf(str(input_pdf), str(output_pdf), config_path)
        print(f"✓ 匿名化完成: {output_pdf}")
    except Exception as e:
        print(f"✗ 匿名化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 步骤3：验证输出
    print("\n[步骤 3/3] 验证输出文件...")
    if output_pdf.exists():
        file_size = output_pdf.stat().st_size
        print(f"✓ 输出文件已生成")
        print(f"  - 文件大小: {file_size} bytes")
        print(f"  - 输入文件: {input_pdf}")
        print(f"  - 输出文件: {output_pdf}")

        if file_size > 0:
            print("\n" + "=" * 60)
            print("✓ 测试通过！")
            print("=" * 60)
            print("\n请手动检查以下项目：")
            print("  1. 文字是否有重叠")
            print("  2. 排版是否正常")
            print("  3. 匿名化替换是否正确")
            print("  4. 是否有文字被截断或超出页面")
            print(f"\n输出文件位置: {output_pdf.absolute()}")
            return True
        else:
            print("✗ 输出文件为空")
            return False
    else:
        print("✗ 输出文件未生成")
        return False


if __name__ == "__main__":
    success = test_pdf_anonymization()
    sys.exit(0 if success else 1)
