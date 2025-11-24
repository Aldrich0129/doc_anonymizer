#!/usr/bin/env python3
"""
测试新的 PyMuPDF PDF 脱敏流程
"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from handlers_pdf import anonymize_pdf_via_pymupdf


def test_reporte_2():
    """测试 reporte_2.pdf 文件"""
    input_pdf = "Example/reporte_2.pdf"
    output_pdf = "Example/reporte_2_pymupdf.pdf"
    config_path = "config/rules.yaml"

    print("=" * 60)
    print("测试: reporte_2.pdf (PyMuPDF方法)")
    print("=" * 60)
    print(f"输入文件: {input_pdf}")
    print(f"输出文件: {output_pdf}")
    print(f"配置文件: {config_path}")
    print()

    try:
        print("开始处理...")
        anonymize_pdf_via_pymupdf(input_pdf, output_pdf, config_path)
        print("✓ 处理成功!")
        print(f"✓ 输出文件已生成: {output_pdf}")

        # 检查文件大小
        output_size = Path(output_pdf).stat().st_size
        print(f"✓ 输出文件大小: {output_size / 1024:.2f} KB")

        # 对比源文件和旧方法的文件大小
        input_size = Path(input_pdf).stat().st_size
        old_output = Path("Example/reporte_2 exp.pdf")
        if old_output.exists():
            old_size = old_output.stat().st_size
            print(f"\n文件大小对比:")
            print(f"  源文件:     {input_size / 1024:.2f} KB")
            print(f"  新方法:     {output_size / 1024:.2f} KB")
            print(f"  旧方法:     {old_size / 1024:.2f} KB")

        print()
        return True

    except Exception as e:
        print(f"✗ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("PDF 脱敏 - PyMuPDF 流程测试")
    print("=" * 60)
    print()

    # 测试 reporte_2.pdf
    test_result = test_reporte_2()

    # 测试总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"PyMuPDF 方法测试: {'✓ 通过' if test_result else '✗ 失败'}")
    print()

    if test_result:
        print("=" * 60)
        print("格式验证（请手动检查）")
        print("=" * 60)
        print("请打开以下文件进行对比:")
        print("1. Example/reporte_2.pdf (源文件)")
        print("2. Example/reporte_2_pymupdf.pdf (PyMuPDF新方法)")
        print("3. Example/reporte_2 exp.pdf (旧方法)")
        print()
        print("检查项:")
        print("  ✓ 字体大小是否一致")
        print("  ✓ 排版是否整齐")
        print("  ✓ 是否有文字重叠")
        print("  ✓ 是否有字符大小不一")
        print("  ✓ 内容是否被正确脱敏")
        print()
        print("✓ 所有测试通过!")
        return 0
    else:
        print("✗ 测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
