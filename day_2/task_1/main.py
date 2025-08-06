import os
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
from typing import List, Dict, Tuple
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

class RAGAmazonReviews:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        print("🔧 Initializing Gemini AI model...")
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)
        
        print("🗄️ Setting up ChromaDB vector store...")
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="amazon_reviews",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
    
    def chunk_reviews(self, csv_path: str, aspect_keywords: List[str]) -> List[Dict]:
        """Chunk reviews by product, sentiment and aspect, avoiding duplicates."""
        print(f"📄 Processing CSV: {os.path.basename(csv_path)}")
        df = pd.read_csv(csv_path)
        chunks = []
        seen_reviews = set()  # Track unique review texts to avoid duplicates
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Chunking reviews"):
            product = row['product'].lower()  # Normalize to lowercase
            review = row['review_text']
            reviewer_id = row['reviewer_id']
            sentiment = row.get('sentiment', 'unknown')
            matching_aspects = [kw.lower() for kw in aspect_keywords if kw.lower() in review.lower()]
            if matching_aspects and review not in seen_reviews:
                seen_reviews.add(review)
                aspects_str = ",".join(matching_aspects)  # Serialize list to string for ChromaDB
                chunks.append({
                    "text": review,
                    "metadata": {
                        "product": product,
                        "reviewer_id": reviewer_id,
                        "sentiment": sentiment,
                        "aspects_str": aspects_str  # String version for storage
                    }
                })
        print(f"✅ {len(chunks)} unique chunks found in {csv_path}")
        return chunks

    def add_reviews(self, data_dir: str, aspect_keywords: List[str]):
        print(f"📁 Scanning directory: {data_dir}")
        if not os.path.exists(data_dir):
            print(f"⚠️ Directory '{data_dir}' not found! Creating it now.")
            os.makedirs(data_dir)
            print("Please add CSV files to the new directory and rerun.")
            return
        
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            print("⚠️ No CSV files found in the directory!")
            return
        
        print(f"📚 Found {len(csv_files)} CSV files to process")
        for filename in csv_files:
            file_path = os.path.join(data_dir, filename)
            chunks = self.chunk_reviews(file_path, aspect_keywords)
            print(f"💾 Adding {len(chunks)} chunks to vector store...")
            self.collection.add(
                documents=[ch["text"] for ch in chunks],
                metadatas=[ch["metadata"] for ch in chunks],
                ids=[f"{filename}_{i}" for i in range(len(chunks))]
            )
        print("🎉 All CSVs processed and added to the knowledge base!")

    def query(self, question: str, product: str, aspect: str, n_results: int = 5) -> Tuple[str, List[Dict]]:
        print("🔍 Searching for relevant reviews...")
        query_str = f"{product} {aspect} {question}"
        # Normalize inputs to lowercase for case-insensitive matching
        normalized_product = product.lower()
        normalized_aspect = aspect.lower()
        results = self.collection.query(
            query_texts=[query_str],
            n_results=n_results * 2,  # Fetch more to account for potential duplicates
            # Filter by product using exact match (case-sensitive), we'll handle case-insensitivity post-query
        )
        # De-duplicate and manually filter by product and aspect (case-insensitive)
        unique_results = {}
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            meta_product = meta.get('product', '').lower()
            meta_aspects = meta.get('aspects_str', '').lower().split(',')
            if doc not in unique_results and normalized_product in meta_product and normalized_aspect in meta_aspects:
                unique_results[doc] = meta
        unique_docs = list(unique_results.keys())
        unique_metas = list(unique_results.values())
        print(f"📊 Found {len(unique_docs)} unique relevant chunks (after de-duplication and aspect filter)")
        
        if not unique_docs:
            return "No relevant reviews found for the specified product and aspect. Try adjusting your query or adding more data.", []
        
        context = "\n\n".join([
            f"{meta['product']} | Reviewer {meta['reviewer_id']} | Sentiment: {meta['sentiment']} | Aspects: {meta['aspects_str']}\n{text}"
            for text, meta in zip(unique_docs, unique_metas)
        ])
        print("🤖 Generating Gemini response...")
        prompt = (
            "Summarize the main pros and cons about the product, referencing reviewer IDs and aspects:\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Please cite product name and reviewer ID in your answer. Focus on common issues if asked."
        )
        response = self.model.generate_content(prompt)
        return response.text, unique_metas

def main():
    print("🚀 Starting RAG System for Amazon Reviews...")
    print("=" * 50)
    rag = RAGAmazonReviews()
    # Define product review aspects of interest
    ASPECTS = ["battery", "camera", "screen", "performance", "price", "design"]  # Expand as needed
    # Add reviews (expects data dir with CSVs: columns must be product, review_text, reviewer_id, [sentiment])
    print("\n📋 Processing Amazon review CSVs...")
    rag.add_reviews("/Users/subashkannan/Desktop/agentic-learning-main/day_2/task_1/data/", ASPECTS)
    
    print("\n" + "=" * 50)
    print("🎯 RAG System Ready! Type 'quit' to exit.")
    print("💡 Ask a question about Amazon products by aspect!")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n❓ Enter your question: ")
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using RAG QA for Amazon Reviews!")
                break
            product = input("🛒 Enter product name: ")
            aspect = input("🔑 Enter aspect (battery, camera, etc.): ")
            
            print("\n🔄 Processing your query...")
            answer, sources = rag.query(question, product, aspect)
            
            print("\n" + "=" * 50)
            print("Answer:")
            print("-" * 50)
            print(answer)
            print("\n📚 Sources:")
            print("-" * 50)
            for i, source in enumerate(sources, 1):
                print(f"{i}. {source['product']} | Reviewer: {source['reviewer_id']} | Aspects: {source['aspects_str']} | Sentiment: {source['sentiment']}")
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f" Error occurred: {str(e)}")
            print("Please try again or contact support.")

if __name__ == "__main__":
    main()
