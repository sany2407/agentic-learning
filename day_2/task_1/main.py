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
        """Chunk reviews by product, sentiment and aspect."""
        print(f"📄 Processing CSV: {os.path.basename(csv_path)}")
        df = pd.read_csv(csv_path)
        chunks = []
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="🔍 Chunking reviews"):
            product = row['product']
            review = row['review_text']
            reviewer_id = row['reviewer_id']
            sentiment = row.get('sentiment', 'unknown')
            # Split review into sentences/mini-chunks by aspect keyword matching
            for kw in aspect_keywords:
                if kw.lower() in review.lower():
                    # Optional: do more refined chunk splitting around keyword
                    chunk_text = review
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "product": product,
                            "reviewer_id": reviewer_id,
                            "sentiment": sentiment,
                            "aspect": kw
                        }
                    })
        print(f"✅ {len(chunks)} chunks found in {csv_path}")
        return chunks

    def add_reviews(self, data_dir: str, aspect_keywords: List[str]):
        print(f"📁 Scanning directory: {data_dir}")
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
        # Optionally make the question: [product] + [aspect] + [question] for better embedding
        query_str = f"{product} {aspect} {question}"
        results = self.collection.query(
            query_texts=[query_str],
            n_results=n_results,
            where={"product": product, "aspect": aspect}  # filters by attributes
        )
        print(f"📊 Found {len(results['documents'][0])} relevant chunks")
        # Compose retrieval context
        context = "\n\n".join([
            f"{meta['product']} | Reviewer {meta['reviewer_id']} | Sentiment: {meta['sentiment']} | Aspect: {meta['aspect']}\n{text}"
            for text, meta in zip(results["documents"][0], results["metadatas"][0])
        ])
        print("🤖 Generating Gemini response...")
        prompt = (
            "Summarize the main pros and cons about the product, referencing reviewer IDs and aspect:\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Please cite product name and reviewer ID in your answer."
        )
        response = self.model.generate_content(prompt)
        return response.text, results["metadatas"][0]

def main():
    print("🚀 Starting RAG System for Amazon Reviews...")
    print("=" * 50)
    rag = RAGAmazonReviews()
    # Define product review aspects of interest
    ASPECTS = ["battery", "camera", "screen", "performance", "price", "design"]  # Expand as needed
    # Add reviews (expects /data dir with CSVs: columns must be product, review_text, reviewer_id, [sentiment])
    print("\n📋 Processing Amazon review CSVs...")
    rag.add_reviews("data", ASPECTS)
    
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
                print(f"{i}. {source['product']} | Reviewer: {source['reviewer_id']} | Aspect: {source['aspect']} | Sentiment: {source['sentiment']}")
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f" Error occurred: {str(e)}")
            print("Please try again or contact support.")

if __name__ == "__main__":
    main()