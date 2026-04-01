
import os
import json
from pathlib import Path
from dotenv import load_dotenv

from arxiv_crawler import ArxivCrawler
from pdf_processor import PDFProcessor
from multimodal_retrieval import MultimodalRetrieval


def main():
    load_dotenv()
    
    print("=" * 80)
    print("  多模态学术推荐系统 - 数据准备工具")
    print("=" * 80)
    print()
    
    api_key = os.getenv("VOLCENGINE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  警告：未配置有效的 VOLCENGINE_API_KEY")
        print("   请在 backend/.env 文件中设置正确的 API Key")
        print()
        print("   即使没有 API Key，我们也可以：")
        print("   - 从 arXiv 获取论文")
        print("   - 处理 PDF 文件")
        print("   - 保存处理后的数据（不进行向量化）")
        print()
        
        proceed = input("是否继续？(y/n): ").strip().lower()
        if proceed != "y":
            print("取消操作")
            return
    
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    target_count = int(os.getenv("TARGET_PAPER_COUNT", 50))
    
    print("\n" + "=" * 80)
    print("📥 步骤 1: 从 arXiv 获取论文")
    print("=" * 80)
    
    crawler = ArxivCrawler()
    papers = crawler.run(target_count=target_count)
    
    if not papers:
        print("❌ 未能获取论文")
        return
    
    print(f"\n✅ 成功获取 {len(papers)} 篇论文")
    
    print("\n" + "=" * 80)
    print("📄 步骤 2: 处理 PDF 文件")
    print("=" * 80)
    
    pdf_processor = PDFProcessor()
    processed_papers = pdf_processor.process_all_papers(papers)
    
    if not processed_papers:
        print("❌ 未能处理任何论文")
        return
    
    print(f"\n✅ 成功处理 {len(processed_papers)} 篇论文")
    
    if api_key and api_key != "your_api_key_here":
        print("\n" + "=" * 80)
        print("🔍 步骤 3: 向量化和建立索引")
        print("=" * 80)
        
        try:
            retrieval = MultimodalRetrieval()
            total_chunks = retrieval.encode_and_index_all_processed()
            
            print(f"\n✅ 成功索引 {total_chunks} 个文本块")
            
            stats = retrieval.get_index_stats()
            print(f"\n📊 索引统计: {stats}")
            
        except Exception as e:
            print(f"\n❌ 向量化过程出错: {type(e).__name__}: {e}")
            print("\n提示：请检查你的 API Key 是否正确，以及模型是否已开通")
    else:
        print("\n⚠️  跳过向量化步骤（API Key 未配置）")
        print("   处理后的数据已保存在 data/processed/ 目录")
        print("   配置好 API Key 后，再次运行此脚本即可完成向量化")
    
    print("\n" + "=" * 80)
    print("✅ 数据准备完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
