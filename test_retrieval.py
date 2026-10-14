
from app.services.retrieval_service import retrieve_chunks

question = input("Ask a question about your uploaded documents: ")

try:
    results = retrieve_chunks(question, limit=5)

    if not results:
        print("No matching chunks found.")
    else:
        for index, result in enumerate(results, start=1):
            print(f"\n--- Result {index} ---")
            print(f"File: {result['filename']}")
            print(f"Chunk: {result['chunk_index']}")
            print(f"Similarity score: {result['score']:.4f}")
            print(f"Text: {result['text']}")

except Exception as exc:
    print(f"Retrieval failed: {exc}")
