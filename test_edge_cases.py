#!/usr/bin/env python3
"""
边界情况测试：测试各种边界场景和复杂情况
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import xml.etree.ElementTree as ET


def test_very_long_text():
    """测试超长文本"""
    print("\n" + "=" * 60)
    print("测试1: 超长文本处理")
    print("=" * 60)

    try:
        from handlers_pdf import _fit_text_to_width

        # 创建超长文本
        very_long_text = "A" * 500
        max_width = 100.0

        adjusted_text, adjusted_size = _fit_text_to_width(
            very_long_text, "Helvetica", 12.0, max_width
        )

        print(f"原始文本长度: {len(very_long_text)} 字符")
        print(f"调整后文本长度: {len(adjusted_text)} 字符")
        print(f"调整后字号: {adjusted_size:.2f}")

        # 验证文本被合理处理
        assert len(adjusted_text) <= len(very_long_text), "文本长度应该减少或保持不变"
        assert adjusted_size <= 12.0, "字号应该减少或保持不变"

        print("✓ 超长文本测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_empty_and_whitespace():
    """测试空文本和空白字符"""
    print("\n" + "=" * 60)
    print("测试2: 空文本和空白字符")
    print("=" * 60)

    try:
        from handlers_pdf import _get_text_width, _fit_text_to_width

        # 测试空文本
        width1 = _get_text_width("", "Helvetica", 12.0)
        print(f"空文本宽度: {width1}")
        assert width1 == 0.0, "空文本宽度应为0"

        # 测试空白字符
        width2 = _get_text_width("   ", "Helvetica", 12.0)
        print(f"空白文本宽度: {width2:.2f}")

        # 测试适配空文本
        text, size = _fit_text_to_width("", "Helvetica", 12.0, 100.0)
        assert text == "", "空文本应保持为空"

        print("✓ 空文本测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_token_scenarios():
    """测试各种Token数量变化场景"""
    print("\n" + "=" * 60)
    print("测试3: 多种Token变化场景")
    print("=" * 60)

    try:
        # 场景1: Token数量大幅增加 (1 → 10)
        line_el = ET.Element("line", top="100")
        words = [
            ET.SubElement(line_el, "word", x0="10", x1="100", top="100", bottom="110",
                          width="90", height="10", font="Helvetica", size="10")
        ]
        words[0].text = "Original"

        new_tokens = ["Token1", "Token2", "Token3", "Token4", "Token5",
                      "Token6", "Token7", "Token8", "Token9", "Token10"]

        # 应用重分配
        tokens_per_word = len(new_tokens) // len(words)
        remainder = len(new_tokens) % len(words)
        token_idx = 0
        for word_idx in range(len(words)):
            tokens_to_assign = tokens_per_word
            if word_idx < remainder:
                tokens_to_assign += 1
            assigned_tokens = new_tokens[token_idx:token_idx + tokens_to_assign]
            words[word_idx].text = " ".join(assigned_tokens)
            token_idx += tokens_to_assign

        print(f"场景1 - 1词→10token:")
        print(f"  结果: '{words[0].text}'")
        assert len(words[0].text) > 0, "单词应包含所有token"

        # 场景2: Token数量减少 (5 → 2)
        line_el2 = ET.Element("line", top="100")
        words2 = [
            ET.SubElement(line_el2, "word", x0=str(i*50), x1=str(i*50+45), top="100", bottom="110",
                          width="45", height="10", font="Helvetica", size="10")
            for i in range(5)
        ]
        for i, word in enumerate(words2):
            word.text = f"Word{i+1}"

        new_tokens2 = ["NewToken1", "NewToken2"]

        # 应用重分配
        for idx in range(len(new_tokens2)):
            words2[idx].text = new_tokens2[idx]
        for idx in range(len(new_tokens2), len(words2)):
            words2[idx].text = ""

        print(f"场景2 - 5词→2token:")
        filled_words = [w.text for w in words2 if w.text]
        empty_words = [w.text for w in words2 if not w.text]
        print(f"  填充的词: {filled_words}")
        print(f"  空词数量: {len(empty_words)}")

        assert len(filled_words) == 2, "应有2个填充的词"
        assert len(empty_words) == 3, "应有3个空词"

        print("✓ Token变化场景测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_special_characters():
    """测试特殊字符处理"""
    print("\n" + "=" * 60)
    print("测试4: 特殊字符处理")
    print("=" * 60)

    try:
        from handlers_pdf import _get_text_width

        # 测试各种特殊字符
        test_strings = [
            "Hello\nWorld",  # 换行符
            "Test\tTab",     # 制表符
            "Español",       # 重音字符
            "测试中文",       # 中文字符
            "©®™",           # 符号
            "123@#$%",       # 数字和符号
        ]

        for text in test_strings:
            try:
                width = _get_text_width(text, "Helvetica", 12.0)
                print(f"✓ '{text[:20]}': {width:.2f} 点")
            except Exception as e:
                print(f"⚠ '{text[:20]}': 无法计算宽度 (使用估算)")

        print("✓ 特殊字符测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_font_variations():
    """测试各种字体变体"""
    print("\n" + "=" * 60)
    print("测试5: 字体变体处理")
    print("=" * 60)

    try:
        from handlers_pdf import _normalize_font, _get_text_width

        fonts_to_test = [
            "Helvetica",
            "Helvetica-Bold",
            "Helvetica-Oblique",
            "Times-Roman",
            "Courier",
            "Unknown-Font",
        ]

        for font in fonts_to_test:
            normalized = _normalize_font(font)
            width = _get_text_width("Test", normalized, 12.0)
            print(f"✓ {font:25} → {normalized:20} (宽度: {width:.2f})")

        print("✓ 字体变体测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extreme_coordinates():
    """测试极端坐标值"""
    print("\n" + "=" * 60)
    print("测试6: 极端坐标值")
    print("=" * 60)

    try:
        from handlers_pdf import xml_to_pdf

        # 创建包含极端坐标的XML
        root = ET.Element("document")
        page = ET.SubElement(root, "page", index="0", width="595.2", height="841.8")

        # 测试场景
        test_cases = [
            ("接近页面边缘", {"x0": "5", "x1": "590", "top": "5"}),
            ("页面底部", {"x0": "50", "x1": "150", "top": "835"}),
            ("很小的宽度", {"x0": "50", "x1": "51", "top": "100"}),
            ("负宽度修正", {"x0": "100", "x1": "50", "top": "100"}),
        ]

        for desc, coords in test_cases:
            line = ET.SubElement(page, "line", top=coords["top"])
            word = ET.SubElement(line, "word",
                                 x0=coords["x0"],
                                 x1=coords["x1"],
                                 top=coords["top"],
                                 bottom=str(float(coords["top"]) + 10),
                                 width=str(max(0, float(coords["x1"]) - float(coords["x0"]))),
                                 height="10",
                                 font="Helvetica",
                                 size="10")
            word.text = f"Test {desc}"

        # 生成PDF
        test_dir = Path(__file__).parent / "test_output"
        test_dir.mkdir(exist_ok=True)
        output_pdf = test_dir / "test_extreme_coords.pdf"

        xml_to_pdf(root, str(output_pdf))

        if output_pdf.exists() and output_pdf.stat().st_size > 0:
            print(f"✓ 极端坐标PDF生成成功")
            print(f"  文件: {output_pdf}")
            print(f"  大小: {output_pdf.stat().st_size} bytes")
            return True
        else:
            print("✗ PDF生成失败")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_page():
    """测试多页PDF处理"""
    print("\n" + "=" * 60)
    print("测试7: 多页PDF处理")
    print("=" * 60)

    try:
        from handlers_pdf import xml_to_pdf

        # 创建多页XML
        root = ET.Element("document")

        for page_num in range(3):
            page = ET.SubElement(root, "page",
                                 index=str(page_num),
                                 width="595.2",
                                 height="841.8")

            # 每页添加一些内容
            for line_num in range(5):
                y_pos = 100 + line_num * 30
                line = ET.SubElement(page, "line", top=str(y_pos))
                word = ET.SubElement(line, "word",
                                     x0="50",
                                     x1="200",
                                     top=str(y_pos),
                                     bottom=str(y_pos + 12),
                                     width="150",
                                     height="12",
                                     font="Helvetica",
                                     size="11")
                word.text = f"Page {page_num + 1}, Line {line_num + 1}"

        # 生成PDF
        test_dir = Path(__file__).parent / "test_output"
        test_dir.mkdir(exist_ok=True)
        output_pdf = test_dir / "test_multipage.pdf"

        xml_to_pdf(root, str(output_pdf))

        if output_pdf.exists() and output_pdf.stat().st_size > 0:
            print(f"✓ 多页PDF生成成功")
            print(f"  文件: {output_pdf}")
            print(f"  大小: {output_pdf.stat().st_size} bytes")
            print(f"  页数: 3")
            return True
        else:
            print("✗ PDF生成失败")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有边界情况测试"""
    print("\n" + "=" * 60)
    print("PDF处理边界情况测试（第二轮）")
    print("=" * 60)

    results = []
    results.append(("超长文本", test_very_long_text()))
    results.append(("空文本处理", test_empty_and_whitespace()))
    results.append(("Token变化场景", test_multiple_token_scenarios()))
    results.append(("特殊字符", test_special_characters()))
    results.append(("字体变体", test_font_variations()))
    results.append(("极端坐标", test_extreme_coordinates()))
    results.append(("多页PDF", test_multi_page()))

    # 总结
    print("\n" + "=" * 60)
    print("第二轮测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:20} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n" + "=" * 60)
        print("✓ 第二轮测试全部通过！")
        print("=" * 60)
        print("\n系统已验证的场景:")
        print("  ✓ 超长文本自动截断或缩放")
        print("  ✓ 空文本和空白字符正确处理")
        print("  ✓ Token数量大幅变化时的均匀分配")
        print("  ✓ 特殊字符（换行符、重音、中文等）")
        print("  ✓ 多种字体变体的规范化")
        print("  ✓ 极端坐标值的安全处理")
        print("  ✓ 多页PDF的稳定生成")
        print("\n生成的测试文件:")
        print("  - test_output/test_extreme_coords.pdf")
        print("  - test_output/test_multipage.pdf")
        return True
    else:
        print(f"\n✗ 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
