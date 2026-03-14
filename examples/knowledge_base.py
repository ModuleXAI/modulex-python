"""Knowledge base management example."""

import asyncio

from modulex import Modulex


async def main() -> None:
    async with Modulex(
        api_key="mx_live_your_api_key_here",
        organization_id="your-org-id",
    ) as client:
        # Create a knowledge base
        kb = await client.knowledge.create(
            name="Engineering Docs",
            description="Internal engineering documentation",
            embedding_config={
                "provider": "openai",
                "model": "text-embedding-3-small",
                "dimension": 1536,
            },
            chunking_config={
                "strategy": "recursive",
                "chunk_size": 1000,
                "overlap": 200,
            },
        )
        kb_id = kb["id"]
        print(f"Created knowledge base: {kb_id}")

        # Upload a document
        doc = await client.knowledge.upload_document(
            knowledge_base_id=kb_id,
            file_path="/path/to/document.pdf",
            metadata={"department": "engineering", "type": "runbook"},
        )
        print(f"Uploaded document: {doc['id']} ({doc.get('filename')})")

        # Check document processing status
        status = await client.knowledge.document_status(kb_id, doc["id"])
        print(f"Processing status: {status.get('status')}")

        # Search the knowledge base
        results = await client.knowledge.search(
            knowledge_base_id=kb_id,
            query="How do I deploy to production?",
            top_k=5,
            min_score=0.3,
        )
        print(f"\nSearch results ({results.get('total_results', 0)}):")
        for result in results.get("results", []):
            print(f"  Score: {result.get('score', 0):.2f}")
            print(f"  Content: {result.get('content', '')[:100]}...")

        # Hybrid search (keyword + semantic)
        hybrid = await client.knowledge.hybrid_search(
            knowledge_base_id=kb_id,
            query="deployment pipeline",
            keyword_weight=0.3,
            semantic_weight=0.7,
        )
        print(f"\nHybrid search results: {hybrid.get('total_results', 0)}")

        # Retrieve formatted context for RAG
        context = await client.knowledge.retrieve_context(
            knowledge_base_id=kb_id,
            query="deployment steps",
            max_tokens=2000,
        )
        print(f"\nRAG context ({len(context.get('context', ''))} chars):")
        print(context["context"][:200] + "...")

        # List all knowledge bases
        kbs = await client.knowledge.list()
        print(f"\nTotal knowledge bases: {len(kbs.get('items', []))}")

        # Get stats
        stats = await client.knowledge.stats()
        print(f"Organization KB stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
