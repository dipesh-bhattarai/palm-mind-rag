from app.services.rag_service import answer_question

session_id = "memory-integration-test"

first = answer_question(
    "Summarize the document.",
    session_id=session_id,
)
print("First answer:", first["answer"])

second = answer_question(
    "What are its three main points?",
    session_id=session_id,
)
print("Follow-up answer:", second["answer"])