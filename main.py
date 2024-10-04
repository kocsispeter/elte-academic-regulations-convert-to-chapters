import json
from typing import List
import re
from PyPDF2 import PdfReader

import warnings

JSON_FILENAME = "hkr_chapters.json"

PDF_FILENAME = "PDFsam_merge_24-301.pdf"

def extract_prefix(text):
    pattern = r'^(CHAPTER\s+[IVXLCDM]+)(?:/[A-Z]|\d+)?'
    match = re.match(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else None

def extract_title(text):
    pattern = r'CHAPTER.*?\n(.*?)\n\s*\n'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        title = match.group(1).strip()
        # Remove digits from the end of the title
        title = re.sub(r'\d+$', '', title).strip()
        return title
    return None

# Function to extract text from a PDF file
def get_pdf_data(pdf_path, start_page, end_page=None):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(start_page, num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text


def get_chunks(full_text):
    chapters = re.split(r'(?=CHAPTER\s)', full_text)
    chapters = [chapter.strip() for chapter in chapters if chapter.strip()]

    processed_chapters = []
    for i, chapter in enumerate(chapters):
        start_page = "Unknown" if not (chapters[i - 1].split('\n')[-1].strip()).isdigit() else chapters[i - 1].split('\n')[-1].strip()
        chapter_number = extract_prefix(chapter) if extract_prefix(chapter) else "Unknown chapter number"
        title = extract_title(chapter) if extract_title(chapter) else "Unknown title"
        processed_chapters.append((chapter, chapter_number, title, start_page))

    return processed_chapters


def count_words(text):
    return len(re.findall(r'\w+', text))



def extract_pdf_chapters(chapters, filename) -> List[dict]:
    documents = []
    for i, (chapter_content, chapter_number, title, start_page) in enumerate(chapters):
        word_count = count_words(chapter_content)
        doc_json = {
            "id": f"{i+1}",
            "chapter_content": chapter_content,  # Taking first 100 characters as a sample
            "embedding": [],  # Placeholder for embedding
            "chapter_number": chapter_number,
            "chapter_title": title,
            "chapter_start_page": start_page,
            "word_count": word_count
        }
        documents.append(doc_json)

    return documents

full_doc_text = get_pdf_data(PDF_FILENAME, 0)
chunks = get_chunks(full_doc_text)
json_docs = extract_pdf_chapters(chunks, PDF_FILENAME)

# Save the JSON output
with open(JSON_FILENAME, 'w') as f:
    json.dump(json_docs, f, indent=4)

print(f"JSON output has been saved to '{JSON_FILENAME}'")





