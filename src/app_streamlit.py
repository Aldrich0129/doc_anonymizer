# src/app_streamlit.py
import streamlit as st
from pathlib import Path
from tempfile import NamedTemporaryFile

from handlers_docx import anonymize_docx
from handlers_pdf import anonymize_pdf
from config import load_rules


CONFIG_PATH = "config/rules.yaml"

st.set_page_config(page_title="文档匿名过滤 · MVP", layout="centered")

st.title("文档匿名化 / 脱敏过滤（试用版）")
st.write("支持 DOCX & PDF，基于规则自动替换敏感信息。")

uploaded_files = st.file_uploader("上传文件", type=["docx", "pdf"], accept_multiple_files=True)

if uploaded_files:
    for f in uploaded_files:
        ext = Path(f.name).suffix.lower()
        st.write(f"处理文件：**{f.name}**")

        with NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
            tmp_in.write(f.read())
            tmp_in_path = tmp_in.name

        tmp_out = NamedTemporaryFile(delete=False, suffix=ext)
        tmp_out_path = tmp_out.name
        tmp_out.close()

        if ext == ".docx":
            anonymize_docx(tmp_in_path, tmp_out_path, CONFIG_PATH)
        elif ext == ".pdf":
            anonymize_pdf(tmp_in_path, tmp_out_path, CONFIG_PATH)
        else:
            st.warning(f"暂不支持类型：{ext}")
            continue

        with open(tmp_out_path, "rb") as out_f:
            st.download_button(
                label=f"下载脱敏后的文件：{f.name}",
                data=out_f,
                file_name=f"anonymized_{f.name}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if ext == ".docx" else "application/pdf",
            )
