import os
import json
import fitz
import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image


class PDFProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.pdf_dir = self.data_dir / "pdfs"
        self.processed_dir = self.data_dir / "processed"
        self.images_dir = self.processed_dir / "images"
        
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"Error extracting text with pdfplumber from {pdf_path}: {e}")
        return text
    
    def extract_text_with_pymupdf(self, pdf_path: str) -> str:
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n\n"
            doc.close()
        except Exception as e:
            print(f"Error extracting text with pymupdf from {pdf_path}: {e}")
        return text
    
    def extract_text(self, pdf_path: str) -> str:
        text = self.extract_text_with_pdfplumber(pdf_path)
        if not text or len(text.strip()) < 100:
            text = self.extract_text_with_pymupdf(pdf_path)
        return text
    
    def extract_images(self, pdf_path: str, paper_id: str) -> List[str]:
        image_paths = []
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)
                for img_idx, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    image_filename = f"{paper_id}_page{page_num}_img{img_idx}.{image_ext}"
                    image_path = self.images_dir / image_filename
                    
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    image_paths.append(str(image_path))
            doc.close()
        except Exception as e:
            print(f"Error extracting images from {pdf_path}: {e}")
        return image_paths
    
    def extract_page_images(self, pdf_path: str, paper_id: str, dpi: int = 150) -> List[str]:
        page_image_paths = []
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                image_filename = f"{paper_id}_page{page_num}.png"
                image_path = self.images_dir / image_filename
                
                pix.save(str(image_path))
                page_image_paths.append(str(image_path))
            doc.close()
        except Exception as e:
            print(f"Error extracting page images from {pdf_path}: {e}")
        return page_image_paths
    
    def clean_text(self, text: str) -> str:
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines)
    
    def chunk_text_by_paragraph(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                if len(para) > chunk_size:
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= chunk_size:
                            if temp_chunk:
                                temp_chunk += " " + word
                            else:
                                temp_chunk = word
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = word
                    if temp_chunk:
                        current_chunk = temp_chunk
                    else:
                        current_chunk = ""
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        if overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i == 0:
                    overlapped_chunks.append(chunk)
                else:
                    prev_chunk = chunks[i-1]
                    prev_words = prev_chunk.split()
                    overlap_words = prev_words[-min(len(prev_words), 20):]
                    overlap_text = " ".join(overlap_words)
                    
                    if len(overlap_text) <= overlap:
                        overlapped_chunk = overlap_text + "\n\n" + chunk
                    else:
                        overlapped_chunk = chunk
                    overlapped_chunks.append(overlapped_chunk)
            chunks = overlapped_chunks
        
        return chunks
    
    def process_paper(self, paper: Dict) -> Optional[Dict]:
        paper_id = paper["id"]
        pdf_path = paper.get("pdf_path", str(self.pdf_dir / f"{paper_id}.pdf"))
        
        if not Path(pdf_path).exists():
            print(f"PDF not found for {paper_id}: {pdf_path}")
            return None
        
        print(f"Processing paper: {paper_id}")
        
        text = self.extract_text(pdf_path)
        cleaned_text = self.clean_text(text)
        
        images = self.extract_images(pdf_path, paper_id)
        page_images = self.extract_page_images(pdf_path, paper_id)
        
        chunks = self.chunk_text_by_paragraph(cleaned_text)
        
        processed_data = {
            "paper_id": paper_id,
            "title": paper["title"],
            "authors": paper["authors"],
            "summary": paper["summary"],
            "full_text": cleaned_text,
            "chunks": chunks,
            "images": images,
            "page_images": page_images,
            "num_chunks": len(chunks),
            "num_images": len(images),
            "num_pages": len(page_images)
        }
        
        output_file = self.processed_dir / f"{paper_id}_processed.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"Processed {paper_id}: {len(chunks)} chunks, {len(images)} images, {len(page_images)} pages")
        
        return processed_data
    
    def process_all_papers(self, papers: List[Dict]) -> List[Dict]:
        processed_papers = []
        for paper in papers:
            processed = self.process_paper(paper)
            if processed:
                processed_papers.append(processed)
        return processed_papers
    
    def load_processed_paper(self, paper_id: str) -> Optional[Dict]:
        output_file = self.processed_dir / f"{paper_id}_processed.json"
        if output_file.exists():
            with open(output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


def main():
    from arxiv_crawler import ArxivCrawler
    
    crawler = ArxivCrawler()
    papers = crawler.load_metadata()
    
    if not papers:
        print("No papers found. Please run the crawler first.")
        return
    
    processor = PDFProcessor()
    
    print(f"Processing {len(papers)} papers...")
    processed = processor.process_all_papers(papers[:5])
    
    print(f"\nSummary:")
    print(f"Total papers processed: {len(processed)}")
    print(f"Processed data stored in: {processor.processed_dir}")


if __name__ == "__main__":
    main()
