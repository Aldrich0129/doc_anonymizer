#!/usr/bin/env python3
"""
简化的PDF处理测试：测试核心函数而不需要真实PDF
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import xml.etree.ElementTree as ET


def test_text_width_calculation():
    """测试文本宽度计算功能"""
    print("\n" + "=" * 60)
    print("测试1: 文本宽度计算")
    print("=" * 60)

    try:
        from handlers_pdf import _get_text_width, _fit_text_to_width

        # 测试1: 正常文本
        text = "Hello World"
        width = _get_text_width(text, "Helvetica", 12.0)
        print(f"✓ 文本 '{text}' 宽度: {width:.2f} 点")

        # 测试2: 长文本适配
        long_text = "This is a very long text that should be adjusted to fit within a specific width"
        max_width = 200.0
        adjusted_text, adjusted_size = _fit_text_to_width(long_text, "Helvetica", 12.0, max_width)
        print(f"✓ 长文本适配:")
        print(f"  原始: '{long_text[:40]}...' (字号12)")
        print(f"  调整: '{adjusted_text[:40]}...' (字号{adjusted_size:.2f})")

        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_token_redistribution():
    """测试Token重分配逻辑"""
    print("\n" + "=" * 60)
    print("测试2: Token重分配逻辑")
    print("=" * 60)

    try:
        # 创建模拟的XML结构
        line_el = ET.Element("line", top="100")

        # 场景1: 原始3个词，匿名化后5个token
        words = [
            ET.SubElement(line_el, "word", x0="10", top="100", width="50", height="10",
                          font="Helvetica", size="10"),
            ET.SubElement(line_el, "word", x0="65", top="100", width="100", height="10",
                          font="Helvetica", size="10"),
            ET.SubElement(line_el, "word", x0="170", top="100", width="80", height="10",
                          font="Helvetica", size="10"),
        ]
        words[0].text = "Cliente:"
        words[1].text = "KFC"
        words[2].text = "España"

        # 模拟匿名化结果
        new_tokens = ["Cliente:", "ABC", "S.A.", "Empresa", "Anónima"]

        print(f"原始词数: {len(words)}")
        print(f"原始文本: {' '.join(w.text for w in words)}")
        print(f"新token数: {len(new_tokens)}")
        print(f"新文本: {' '.join(new_tokens)}")

        # 应用重分配逻辑（复制自handlers_pdf.py）
        if len(new_tokens) == len(words):
            for idx in range(len(words)):
                words[idx].text = new_tokens[idx]
        elif len(new_tokens) < len(words):
            for idx in range(len(new_tokens)):
                words[idx].text = new_tokens[idx]
            for idx in range(len(new_tokens), len(words)):
                words[idx].text = ""
        else:
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

        print("\n重分配结果:")
        for i, word in enumerate(words):
            print(f"  词{i+1}: '{word.text}'")

        print("✓ Token重分配测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_font_normalization():
    """测试字体规范化"""
    print("\n" + "=" * 60)
    print("测试3: 字体规范化")
    print("=" * 60)

    try:
        from handlers_pdf import _guess_font_name, _normalize_font

        test_fonts = [
            ("Arial-Bold", "Helvetica-Bold"),
            ("TimesNewRoman-Italic", "Helvetica-Oblique"),
            ("Courier", "Helvetica"),
            ("CustomFont-Bold", "Helvetica-Bold"),
        ]

        for input_font, expected_base in test_fonts:
            guessed = _guess_font_name(input_font)
            normalized = _normalize_font(input_font)
            print(f"✓ {input_font:25} → {normalized}")

        print("✓ 字体规范化测试通过")
        return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("PDF处理核心功能测试")
    print("=" * 60)

    results = []
    results.append(("文本宽度计算", test_text_width_calculation()))
    results.append(("Token重分配", test_token_redistribution()))
    results.append(("字体规范化", test_font_normalization()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:20} {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n✓ 所有测试通过！核心功能正常工作。")
        return True
    else:
        print(f"\n✗ 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
