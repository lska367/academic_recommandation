
from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

print("=" * 80)
print("1.任务书.docx")
print("=" * 80)
print(read_docx("1.任务书.docx"))
print("\n\n")

print("=" * 80)
print("杨锴-2022212431-开题报告.docx")
print("=" * 80)
print(read_docx("杨锴-2022212431-开题报告.docx"))
