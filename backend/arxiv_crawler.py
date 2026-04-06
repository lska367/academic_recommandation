import os
import json
import time
import feedparser
import requests
from pathlib import Path
from typing import List, Dict, Optional
from requests.exceptions import HTTPError


class ArxivCrawler:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.pdf_dir = self.data_dir / "pdfs"
        self.metadata_file = self.data_dir / "metadata.json"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        self.base_api_url = "http://export.arxiv.org/api/query"
        self.request_delay = 3

    def fetch_papers(
        self,
        categories: List[str] = ["cs.AI", "cs.LG", "cs.CL"],
        max_results: int = 50,
        start: int = 0
    ) -> List[Dict]:
        category_query = " OR ".join([f"cat:{cat}" for cat in categories])
        query = f"({category_query})"

        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        max_retries = 5
        base_delay = 10

        for attempt in range(max_retries):
            try:
                response = requests.get(self.base_api_url, params=params)
                response.raise_for_status()
                break
            except HTTPError as e:
                if response.status_code == 429:
                    delay = base_delay * (2 ** attempt)
                    print(f"Rate limit hit (429). Waiting {delay} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(delay)
                else:
                    raise
        else:
            raise Exception(f"Failed to fetch after {max_retries} retries due to rate limiting")

        feed = feedparser.parse(response.content)
        papers = []
        
        for entry in feed.entries:
            paper = {
                "id": entry.id.split("/")[-1],
                "title": entry.title.strip(),
                "authors": [author.name for author in entry.authors],
                "published": entry.published,
                "updated": entry.updated,
                "summary": entry.summary.strip(),
                "categories": [tag.term for tag in entry.tags],
                "pdf_url": entry.link.replace("abs", "pdf") + ".pdf",
                "abs_url": entry.link
            }
            papers.append(paper)
        
        return papers
    
    def download_pdf(self, pdf_url: str, paper_id: str) -> Optional[str]:
        pdf_path = self.pdf_dir / f"{paper_id}.pdf"
        
        if pdf_path.exists():
            return str(pdf_path)
        
        try:
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            
            return str(pdf_path)
        except Exception as e:
            print(f"Failed to download {paper_id}: {e}")
            return None
    
    def save_metadata(self, papers: List[Dict]):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
    
    def load_metadata(self) -> List[Dict]:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def get_paper_count(self) -> int:
        if self.metadata_file.exists():
            return len(self.load_metadata())
        return 0
    
    def run(
        self,
        categories: List[str] = ["cs.AI", "cs.LG", "cs.CL"],
        target_count: int = 50
    ) -> List[Dict]:
        existing_papers = self.load_metadata()
        existing_ids = {p["id"] for p in existing_papers}
        
        if len(existing_papers) >= target_count:
            print(f"Already have {len(existing_papers)} papers, which meets target {target_count}")
            return existing_papers
        
        print(f"Fetching papers... Current: {len(existing_papers)}, Target: {target_count}")
        
        new_papers = []
        start = 0
        batch_size = 100
        
        while len(new_papers) + len(existing_papers) < target_count:
            batch = self.fetch_papers(categories, batch_size, start)
            
            if not batch:
                break
            
            for paper in batch:
                if paper["id"] not in existing_ids:
                    new_papers.append(paper)
                    existing_ids.add(paper["id"])
                    
                    if len(new_papers) + len(existing_papers) >= target_count:
                        break
            
            start += batch_size
            time.sleep(self.request_delay)
        
        all_papers = existing_papers + new_papers
        
        print(f"Downloading PDFs for {len(new_papers)} new papers...")
        for i, paper in enumerate(new_papers, 1):
            print(f"Downloading {i}/{len(new_papers)}: {paper['id']}")
            pdf_path = self.download_pdf(paper["pdf_url"], paper["id"])
            if pdf_path:
                paper["pdf_path"] = pdf_path
            time.sleep(0.5)
        
        self.save_metadata(all_papers)
        print(f"Done! Total papers: {len(all_papers)}")
        
        return all_papers


def main():
    crawler = ArxivCrawler()
    papers = crawler.run(target_count=50)
    print(f"\nSummary:")
    print(f"Total papers: {len(papers)}")
    print(f"PDF directory: {crawler.pdf_dir}")
    print(f"Metadata file: {crawler.metadata_file}")


if __name__ == "__main__":
    main()
