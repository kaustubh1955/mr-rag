"""
Visual Flow Diagram: LLM Rewriter in RAG Pipeline

Run this to see a visual representation of how the rewriter fits into the pipeline.
"""

def print_pipeline_flow():
    diagram = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    RAG PIPELINE WITH LLM REWRITER                          ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: QUERY INPUT                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Question: "What is the capital of France?"                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: QUERY GENERATION (optional)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Original: "What is the capital of France?"                                 │
│  Generated: "capital city France location"                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: RETRIEVAL                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Input: Search query                                                        │
│  Model: BM25 / Contriever / E5 / etc.                                       │
│  Output: Top-50 documents                                                   │
│                                                                             │
│  [Doc 1] [Doc 2] [Doc 3] ... [Doc 50]                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: RERANKING (optional)                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  Input: Top-50 documents                                                    │
│  Model: Cross-encoder (MonoT5, etc.)                                        │
│  Output: Re-scored Top-50 documents                                         │
│                                                                             │
│  [Doc A] [Doc B] [Doc C] ... [Doc 50]                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: TOP-K SELECTION                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Select top generation_top_k documents (e.g., 5)                            │
│                                                                             │
│  [Doc 1] [Doc 2] [Doc 3] [Doc 4] [Doc 5]                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║  STEP 6: LLM REWRITING ⭐ NEW STEP ⭐                                       ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Input: 5 retrieved documents + original query                              ║
║  Model: Same LLM as generator (e.g., LLaMA-3-8B)                            ║
║  Process: For each document:                                                ║
║                                                                             ║
║    ┌──────────────────────────────────────────────────────────┐            ║
║    │  Prompt:                                                 │            ║
║    │  "Given query and passage, rewrite to:                  │            ║
║    │   - Remove redundant info                               │            ║
║    │   - Highlight relevant info                             │            ║
║    │   - Integrate knowledge                                 │            ║
║    │                                                          │            ║
║    │  Query: What is the capital of France?                  │            ║
║    │  Passage: [Original Doc 1]                              │            ║
║    │  Rewritten: ..."                                        │            ║
║    └──────────────────────────────────────────────────────────┘            ║
║                                                                             ║
║  Output: 5 refined documents                                                ║
║                                                                             ║
║  BEFORE:                                                                    ║
║  Doc 1: "Paris is the capital and most populous city of                    ║
║          France. It has area of 105 sq km. Population 2.2M.                 ║
║          Founded in 3rd century BC. Many museums..."                        ║
║                                                                             ║
║  AFTER:                                                                     ║
║  Doc 1: "Paris is the capital city of France, serving as                   ║
║          the political and cultural center."                                ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: ANSWER GENERATION                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Input: Original query + 5 rewritten documents                              │
│  Model: LLM Generator (same as rewriter)                                    │
│                                                                             │
│  Prompt:                                                                    │
│  "Answer the question using the documents below:                            │
│                                                                             │
│   Question: What is the capital of France?                                  │
│                                                                             │
│   Document 1: [Rewritten Doc 1]                                             │
│   Document 2: [Rewritten Doc 2]                                             │
│   ...                                                                       │
│                                                                             │
│   Answer:"                                                                  │
│                                                                             │
│  Output: "Paris is the capital of France."                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: EVALUATION                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  Metrics: F1, EM, ROUGE, BLEU, etc.                                         │
│  Additional: Context compression ratio                                      │
└─────────────────────────────────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════
                              COMPARISON VIEW
════════════════════════════════════════════════════════════════════════════════

WITHOUT REWRITER:                    WITH REWRITER:
┌──────────────────┐                ┌──────────────────┐
│   Retrieval      │                │   Retrieval      │
│     (50)         │                │     (50)         │
└────────┬─────────┘                └────────┬─────────┘
         │                                   │
         ▼                                   ▼
┌──────────────────┐                ┌──────────────────┐
│   Reranking      │                │   Reranking      │
│     (50)         │                │     (50)         │
└────────┬─────────┘                └────────┬─────────┘
         │                                   │
         ▼                                   ▼
┌──────────────────┐                ┌──────────────────┐
│   Selection      │                │   Selection      │
│     (5)          │                │     (5)          │
└────────┬─────────┘                └────────┬─────────┘
         │                                   │
         │                                   ▼
         │                          ┌──────────────────┐
         │                          │  ⭐ Rewriting    │
         │                          │     (5)          │
         │                          └────────┬─────────┘
         │                                   │
         ▼                                   ▼
┌──────────────────┐                ┌──────────────────┐
│   Generation     │                │   Generation     │
│   (uses 5 docs)  │                │ (uses 5 refined) │
└──────────────────┘                └──────────────────┘


════════════════════════════════════════════════════════════════════════════════
                          TECHNICAL ARCHITECTURE
════════════════════════════════════════════════════════════════════════════════

┌───────────────────────────────────────────────────────────────────────────┐
│  RAG Class (modules/rag.py)                                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐           │
│  │  Retriever  │   │  Reranker   │   │  Generator (LLM)     │           │
│  │             │   │             │   │  - model: LLaMA-3    │           │
│  └─────────────┘   └─────────────┘   │  - tokenizer         │           │
│                                      │  - generate()        │           │
│                                      └──────────┬───────────┘           │
│                                                 │                        │
│                                                 │ shared instance        │
│  ┌──────────────────────────────────────────────┼──────────────────┐    │
│  │  Context Processor                           ▼                  │    │
│  │  (modules/process_context.py)     ┌──────────────────┐         │    │
│  │                                    │  LLM Rewriter    │         │    │
│  │                                    │  - generator ────┘         │    │
│  │                                    │  - batch_size: 4           │    │
│  │                                    │  - process()               │    │
│  │                                    └────────────────────────────┘    │
│  └───────────────────────────────────────────────────────────────────────┘
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════
                              FILE STRUCTURE
════════════════════════════════════════════════════════════════════════════════

mr-rag/
│
├── bergen.py  ←──────────────── Entry point
│
├── modules/
│   ├── rag.py  ←──────────────── Modified: Injects generator into rewriter
│   └── process_context.py
│
├── models/
│   └── context_processors/
│       ├── llm_rewriter.py  ←── NEW: Rewriter implementation
│       ├── recomp.py
│       └── ...
│
├── config/
│   ├── rag_with_rewriter.yaml  ←── NEW: Example config
│   └── context_processor/
│       └── llm_rewriter/  ←───── NEW: Rewriter configs
│           ├── rewriter_basic.yaml
│           ├── rewriter_combined.yaml
│           ├── rewriter_with_title.yaml
│           └── rewriter_custom_prompt.yaml
│
├── documentation/
│   └── llm_rewriter.md  ←──────── NEW: Full documentation
│
└── test_llm_rewriter.py  ←─────── NEW: Test suite


════════════════════════════════════════════════════════════════════════════════
                            CONFIGURATION EXAMPLE
════════════════════════════════════════════════════════════════════════════════

File: config/my_config.yaml
─────────────────────────────
defaults:
    - retriever: contriever
    - generator: llama-3-8b-instruct
    - dataset: kilt_nq
    - context_processor: llm_rewriter/rewriter_basic  ← Enable rewriter

run_name: "nq_with_rewriter"
retrieve_top_k: 50      ← Retrieve 50 docs
rerank_top_k: 50        ← Rerank 50 docs
generation_top_k: 5     ← Rewrite 5 docs, then generate with 5


Command:
─────────
python bergen.py --config-name=my_config


Output Files:
─────────────
experiments/nq_with_rewriter_20250111_143022/
├── eval_dev_out.json                    ← Generated answers
├── eval_dev_metrics.json                ← F1, EM, etc.
├── eval_dev_context_metrics.json        ← Compression: 23.5%
└── processed_context_file.json          ← Rewritten documents


════════════════════════════════════════════════════════════════════════════════
"""
    print(diagram)


def print_code_flow():
    code_flow = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          CODE EXECUTION FLOW                               ║
╚════════════════════════════════════════════════════════════════════════════╝

bergen.py (main)
│
├─→ Hydra loads config from config/rag.yaml (or specified config)
│
└─→ RAG.__init__(**config)
    │
    ├─→ Load retriever config
    ├─→ Load generator config
    ├─→ Load context_processor config (llm_rewriter)
    │
    ├─→ self.generator = instantiate(generator_config)  # Load LLM
    │
    └─→ if 'llm_rewriter' in context_processor_config:
        │   # Inject generator into context processor!
        │   context_processor_config.init_args.generator = self.generator
        │
        └─→ self.context_processor = ProcessContext(**context_processor_config)
            │
            └─→ self.model = instantiate(init_args)  # Creates LLMRewriter
                │
                └─→ LLMRewriter(generator=self.generator, ...)


RAG.eval(dataset_split='dev')
│
├─→ 1. generate_query(dataset, ...)
│   └─→ Returns dataset with 'generated_query' column
│
├─→ 2. retrieve(dataset, top_k=50, ...)
│   └─→ Returns (query_ids, doc_ids, scores)
│
├─→ 3. rerank(dataset, top_k=50, ...)  [if reranker configured]
│   └─→ Returns (query_ids, doc_ids, scores)
│
├─→ 4. Select top generation_top_k (e.g., 5)
│   └─→ doc_ids = [doc_ids_q[:5] for doc_ids_q in doc_ids]
│
├─→ 5. prepare_dataset_from_ids(...)
│   └─→ gen_dataset with 'query' and 'doc' columns
│
├─→ 6. process_context(gen_dataset, ...)  ⭐ REWRITING HAPPENS HERE
│   │
│   └─→ ProcessContext.eval(contexts, queries)
│       │
│       └─→ LLMRewriter._process(contexts, queries)
│           │
│           ├─→ For each (query, doc) pair:
│           │   │
│           │   ├─→ Create prompt: "Rewrite this passage..."
│           │   │
│           │   └─→ Append to all_prompts[]
│           │
│           ├─→ Process in batches:
│           │   │
│           │   └─→ for batch in all_prompts (batch_size=4):
│           │       │
│           │       └─→ self.generator.generate(batch)
│           │           │
│           │           └─→ Returns rewritten passages
│           │
│           └─→ Return rewritten_contexts[]
│
├─→ 7. generate(gen_dataset, ...)  # Now uses rewritten docs
│   │
│   └─→ self.generator.eval(gen_dataset)
│       │
│       └─→ For each query:
│           │
│           ├─→ Format prompt with query + rewritten docs
│           │
│           └─→ self.generator.generate(prompt)
│               │
│               └─→ Returns final answer
│
└─→ 8. eval_metrics(predictions, references, ...)
    └─→ Compute F1, EM, etc.


════════════════════════════════════════════════════════════════════════════════
                          KEY FUNCTION CALLS
════════════════════════════════════════════════════════════════════════════════

LLMRewriter._process(contexts, queries):
    │
    ├─→ Input:
    │   contexts = [
    │       ["Doc 1 for Query 1", "Doc 2 for Query 1", ...],  # Query 1 docs
    │       ["Doc 1 for Query 2", "Doc 2 for Query 2", ...],  # Query 2 docs
    │   ]
    │   queries = ["Query 1", "Query 2", ...]
    │
    ├─→ Process:
    │   for query_idx, (query, docs) in enumerate(zip(queries, contexts)):
    │       for doc_idx, doc in enumerate(docs):
    │           prompt = rewrite_prompt_template.format(
    │               query=query,
    │               passage=doc
    │           )
    │           all_prompts.append(prompt)
    │
    ├─→ Generate:
    │   for batch_start in range(0, len(all_prompts), batch_size):
    │       batch = all_prompts[batch_start:batch_start+batch_size]
    │       rewritten = self.generator.generate(batch)
    │       rewritten_passages.extend(rewritten)
    │
    └─→ Output:
        rewritten_contexts = [
            ["Rewritten Doc 1", "Rewritten Doc 2", ...],  # Query 1
            ["Rewritten Doc 1", "Rewritten Doc 2", ...],  # Query 2
        ]


════════════════════════════════════════════════════════════════════════════════
"""
    print(code_flow)


if __name__ == "__main__":
    print_pipeline_flow()
    print("\n\n")
    print_code_flow()
    print("\n")
    print("=" * 80)
    print("To use the LLM rewriter, see:")
    print("  - LLM_REWRITER_README.md (quick start)")
    print("  - documentation/llm_rewriter.md (full guide)")
    print("  - IMPLEMENTATION_SUMMARY.md (technical details)")
    print("=" * 80)
