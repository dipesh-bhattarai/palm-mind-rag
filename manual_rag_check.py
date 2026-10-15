
from app.services.rag_service import answer_question

question = input("Ask a question about your documents: ")

try:
    result = answer_question(question)

    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== SOURCES ===")
    for source in result["sources"]:
        print(
            f"\nFile: {source['filename']}"
            f"\nChunk: {source['chunk_index']}"
            f"\nScore: {source['score']:.4f}"
        )

except Exception as exc:
    print(f"RAG failed: {exc}")
