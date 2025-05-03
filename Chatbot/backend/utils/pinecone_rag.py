from pinecone import Index

def get_relevant_examples(
    query,
    embed_model,
    pdf_index: Index,
    json_index: Index,
    web_index: Index,
    max_length=2000,
    top_k=5
):
    print("▶️ Running get_relevant_examples with query:", query)

    query_embedding = embed_model.embed_query(query)

    # Query all three indexes
    results_pdf = pdf_index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    results_json = json_index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    results_web = web_index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    combined = results_pdf["matches"] + results_json["matches"] + results_web["matches"]
    combined.sort(key=lambda x: x["score"], reverse=True)

    examples = []
    total_length = 0
    for match in combined:
        chunk_text = match["metadata"].get("text", "")
        if total_length + len(chunk_text) > max_length:
            break
        examples.append(chunk_text)
        total_length += len(chunk_text)

    print(f"✅ Retrieved {len(examples)} relevant chunks\n")

    if examples:
        return "\n\n".join(examples)
    else:
        return "I couldn’t find anything helpful. Please try rephrasing your question."

# def pinecone_search(
#     query: str,
#     embed_model,
#     pdf_index: Index,
#     json_index: Index,
#     web_index: Index
# ) -> str:
#     print("🧠 PineconeSearch Tool Called")
#     print("🔍 Query:", query)

#     return get_relevant_examples(query, embed_model, pdf_index, json_index, web_index)

def pinecone_search(
    query: str,
    embed_model,
    pdf_index: Index,
    json_index: Index,
    web_index: Index
) -> str:
    print("🧠 PineconeSearch Tool Called")
    print("🔍 Query:", query)

    MENTAL_HEALTH_KEYWORDS = [
        "mental health", "anxiety", "depression", "stress", "therapy", "coping", "counseling",
        "self-esteem", "emotional", "suicidal", "trauma", "panic", "mindfulness", "psychologist",
        "cbt", "mental illness", "burnout", "intrusive thoughts", "bipolar", "grief", "loneliness",
        "mental", "psychotherapy", "psychology", "emotions", "diagnosis", "sleep disorder"
    ]

    query_lower = query.lower()

    if not any(keyword in query_lower for keyword in MENTAL_HEALTH_KEYWORDS):
        return "This topic appears to be unrelated to mental health. Please ask about mental health, therapy, or emotional well-being."

    return get_relevant_examples(query, embed_model, pdf_index, json_index, web_index)