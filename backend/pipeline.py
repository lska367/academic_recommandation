
import os
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

from arxiv_crawler import ArxivCrawler
from pdf_processor import PDFProcessor
from multimodal_retrieval import MultimodalRetrieval


class DataPipeline:
    def __init__(self, data_dir: Optional[str] = None):
        load_dotenv()
        
        self.data_dir = Path(data_dir or os.getenv("DATA_DIR", "./data"))
        
        self.crawler = ArxivCrawler(data_dir=str(self.data_dir))
        self.pdf_processor = PDFProcessor(data_dir=str(self.data_dir))
        self.retrieval = MultimodalRetrieval(data_dir=str(self.data_dir))
    
    def run_crawler(
        self,
        categories: list = None,
        target_count: int = None
    ):
        print("=" * 60)
        print("📥 Step 1: Crawling papers from arXiv")
        print("=" * 60)
        
        if categories is None:
            categories = ["cs.AI", "cs.LG", "cs.CL"]
        
        if target_count is None:
            target_count = int(os.getenv("TARGET_PAPER_COUNT", 50))
        
        print(f"Categories: {categories}")
        print(f"Target paper count: {target_count}")
        
        papers = self.crawler.run(
            categories=categories,
            target_count=target_count
        )
        
        print(f"\n✅ Crawling completed. Total papers: {len(papers)}")
        return papers
    
    def run_pdf_processing(self, papers: list = None, limit: int = None):
        print("\n" + "=" * 60)
        print("📄 Step 2: Processing PDF files")
        print("=" * 60)
        
        if papers is None:
            papers = self.crawler.load_metadata()
        
        if not papers:
            print("❌ No papers found. Please run crawler first.")
            return []
        
        if limit is not None:
            papers = papers[:limit]
            print(f"Processing first {limit} papers...")
        
        print(f"Total papers to process: {len(papers)}")
        
        processed_papers = self.pdf_processor.process_all_papers(papers)
        
        print(f"\n✅ PDF processing completed. Processed {len(processed_papers)} papers")
        return processed_papers
    
    def run_indexing(self):
        print("\n" + "=" * 60)
        print("🔍 Step 3: Encoding and indexing papers")
        print("=" * 60)
        
        total_chunks = self.retrieval.encode_and_index_all_processed()
        
        print(f"\n✅ Indexing completed. Total chunks indexed: {total_chunks}")
        return total_chunks
    
    def run_full_pipeline(
        self,
        categories: list = None,
        target_count: int = None,
        process_limit: int = None,
        skip_crawler: bool = False,
        skip_processing: bool = False,
        skip_indexing: bool = False
    ):
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 10 + "🎓 Academic Recommendation Data Pipeline" + " " * 12 + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"Data directory: {self.data_dir}")
        
        start_time = time.time()
        
        papers = None
        
        if not skip_crawler:
            papers = self.run_crawler(categories=categories, target_count=target_count)
        
        if not skip_processing:
            self.run_pdf_processing(papers=papers, limit=process_limit)
        
        if not skip_indexing:
            self.run_indexing()
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("✅ Full pipeline completed!")
        print(f"⏱️  Total elapsed time: {elapsed_time:.2f} seconds")
        print("=" * 60)
        
        stats = self.get_pipeline_stats()
        print("\n📊 Pipeline Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def get_pipeline_stats(self) -> dict:
        stats = {}
        
        metadata_count = self.crawler.get_paper_count()
        stats["metadata_papers"] = metadata_count
        
        pdf_dir = self.data_dir / "pdfs"
        if pdf_dir.exists():
            stats["pdf_files"] = len(list(pdf_dir.glob("*.pdf")))
        else:
            stats["pdf_files"] = 0
        
        processed_dir = self.data_dir / "processed"
        if processed_dir.exists():
            stats["processed_papers"] = len(list(processed_dir.glob("*_processed.json")))
        else:
            stats["processed_papers"] = 0
        
        try:
            index_stats = self.retrieval.get_index_stats()
            stats["indexed_chunks"] = index_stats.get("count", 0)
        except:
            stats["indexed_chunks"] = 0
        
        return stats
    
    def clear_all(self):
        print("⚠️  WARNING: This will delete all data and index!")
        confirm = input("Type 'YES' to confirm: ")
        
        if confirm != "YES":
            print("Operation cancelled.")
            return
        
        print("Clearing index...")
        self.retrieval.clear_index()
        
        import shutil
        
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)
            print(f"Deleted data directory: {self.data_dir}")
        
        print("✅ All data cleared.")


def main():
    parser = argparse.ArgumentParser(
        description="Academic Recommendation Data Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with default settings
  python pipeline.py
  
  # Run only crawler
  python pipeline.py --only-crawler
  
  # Run only PDF processing
  python pipeline.py --only-processing
  
  # Run only indexing
  python pipeline.py --only-indexing
  
  # Skip crawler, run processing and indexing
  python pipeline.py --skip-crawler
  
  # Process only first 10 papers
  python pipeline.py --process-limit 10
  
  # Get pipeline statistics
  python pipeline.py --stats
  
  # Clear all data
  python pipeline.py --clear
        """
    )
    
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="arXiv categories to crawl (e.g., cs.AI cs.LG cs.CL)"
    )
    
    parser.add_argument(
        "--target-count",
        type=int,
        default=None,
        help="Target number of papers to crawl"
    )
    
    parser.add_argument(
        "--process-limit",
        type=int,
        default=None,
        help="Limit number of papers to process"
    )
    
    parser.add_argument(
        "--skip-crawler",
        action="store_true",
        help="Skip the crawling step"
    )
    
    parser.add_argument(
        "--skip-processing",
        action="store_true",
        help="Skip the PDF processing step"
    )
    
    parser.add_argument(
        "--skip-indexing",
        action="store_true",
        help="Skip the indexing step"
    )
    
    parser.add_argument(
        "--only-crawler",
        action="store_true",
        help="Run only the crawler"
    )
    
    parser.add_argument(
        "--only-processing",
        action="store_true",
        help="Run only PDF processing"
    )
    
    parser.add_argument(
        "--only-indexing",
        action="store_true",
        help="Run only indexing"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show pipeline statistics"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all data and index"
    )
    
    args = parser.parse_args()
    
    pipeline = DataPipeline()
    
    if args.clear:
        pipeline.clear_all()
        return
    
    if args.stats:
        stats = pipeline.get_pipeline_stats()
        print("📊 Pipeline Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return
    
    skip_crawler = args.skip_crawler or args.only_processing or args.only_indexing
    skip_processing = args.skip_processing or args.only_crawler or args.only_indexing
    skip_indexing = args.skip_indexing or args.only_crawler or args.only_processing
    
    pipeline.run_full_pipeline(
        categories=args.categories,
        target_count=args.target_count,
        process_limit=args.process_limit,
        skip_crawler=skip_crawler,
        skip_processing=skip_processing,
        skip_indexing=skip_indexing
    )


if __name__ == "__main__":
    main()
