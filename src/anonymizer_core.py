# src/anonymizer_core.py
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

from rapidfuzz import fuzz

def load_rules(config_path: str) -> Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def apply_exact_replacements(text: str, mapping: Dict[str, str]) -> Tuple[str, List[Tuple[str, str]]]:
    logs = []
    for src, dst in mapping.items():
        if src in text:
            text = text.replace(src, dst)
            logs.append((src, dst))
    return text, logs

def apply_regex_replacements(text: str, regex_rules: List[Dict]) -> Tuple[str, List[Tuple[str, str]]]:
    logs = []

    def make_repl(replacement_value: str, logs_inner: List[Tuple[str, str]]):
        def _repl(match):
            original = match.group(0)
            logs_inner.append((original, replacement_value))
            return replacement_value
        return _repl

    for rule in regex_rules:
        pattern = rule["pattern"]
        rtype = rule.get("replacement_type", "mask")
        replacement_value = rule.get("replacement_value", "***")

        # MVP：仅实现 mask
        if rtype == "mask":
            text = re.sub(pattern, make_repl(replacement_value, logs), text)
        else:
            # 后续可扩展 random / hash 等
            text = re.sub(pattern, make_repl(replacement_value, logs), text)

    return text, logs

def anonymize_text(text: str, config_path: str) -> Tuple[str, List[Tuple[str, str]]]:
    rules = load_rules(config_path)
    logs: List[Tuple[str, str]] = []

    # 0) 客户知识库：支持名称/别名替换，优先执行以覆盖后续规则
    kb_customers = rules.get("knowledge_base", {}).get("customers", [])
    for customer in kb_customers:
        replacement = customer.get("replacement", "[CLIENTE]")
        aliases = customer.get("aliases", [])
        names = [customer.get("name", "")] + aliases
        names = [n for n in names if n]

        for candidate in names:
            # 先尝试精确替换
            if candidate in text:
                text = text.replace(candidate, replacement)
                logs.append((candidate, replacement))
                continue

            # 不满足精确匹配时尝试模糊匹配，避免误判设定较高阈值
            score = fuzz.partial_ratio(candidate, text)
            if score >= 90:
                text = re.sub(re.escape(candidate), replacement, text, flags=re.IGNORECASE)
                logs.append((candidate, replacement))

    # 1) 精确替换
    exact_map = rules.get("exact_replacements", {})
    text, exact_logs = apply_exact_replacements(text, exact_map)
    logs.extend(exact_logs)

    # 2) 正则替换
    regex_rules = rules.get("regex_replacements", [])
    text, regex_logs = apply_regex_replacements(text, regex_rules)
    logs.extend(regex_logs)

    return text, logs
