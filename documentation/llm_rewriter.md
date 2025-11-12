# LLM Rewriter Context Processor - Usage Guide

## Overview
The LLM Rewriter is a context processor that uses the same LLM as your generator to refine retrieved documents before they are passed to the generator for answer generation. This helps to:
- Remove redundant information
- Highlight relevant information
- Integrate internal knowledge
- Create more coherent and consistent passages

## Implementation Location
- **Code**: `models/context_processors/llm_rewriter.py`
- **Config**: `config/context_processor/llm_rewriter/`

## Available Rewriter Types

### 1. Basic Rewriter (`rewriter_basic.yaml`)
Rewrites each document separately. Best for maintaining document boundaries.

```yaml
context_processor: llm_rewriter/rewriter_basic
```

### 2. Combined Rewriter (`rewriter_combined.yaml`)
Rewrites all documents together into a single coherent passage. Best for synthesizing information across documents.

```yaml
context_processor: llm_rewriter/rewriter_combined
```

### 3. Title-Preserving Rewriter (`rewriter_with_title.yaml`)
Preserves document titles and only rewrites content. Best when document structure matters.

```yaml
context_processor: llm_rewriter/rewriter_with_title
```

### 4. Custom Prompt Rewriter (`rewriter_custom_prompt.yaml`)
Allows you to define your own rewriting prompt. Best for specific rewriting strategies.

```yaml
context_processor: llm_rewriter/rewriter_custom_prompt
```

## How to Use

### Method 1: Using Existing Config
Create or modify a config file in `config/`:

```yaml
defaults:
    - _self_
    - retriever: contriever
    - reranker: null
    - generator: llama-3-8b-instruct
    - dataset: kilt_nq
    - context_processor: llm_rewriter/rewriter_basic  # Add this line

run_name: "my_rag_with_rewriter"
retrieve_top_k: 50
rerank_top_k: 50
generation_top_k: 5  # Documents to rewrite
```

Then run:
```bash
python bergen.py --config-name=my_config
```

### Method 2: Override from Command Line
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=5
```

### Method 3: Using Environment Variable
```bash
export CONFIG=my_config
python bergen.py
```

## Configuration Parameters

You can customize the rewriter behavior:

```yaml
context_processor:
    init_args:
        _target_: models.context_processors.llm_rewriter.LLMRewriter
        generator: null  # Automatically set to your generator
        batch_size: 4  # Process 4 documents at a time
        max_new_tokens: 256  # Tokens per rewritten passage
        process_separately: true  # true=separate docs, false=combined
        rewrite_prompt_template: |  # Optional custom prompt
            Your custom prompt here with {query} and {passage} placeholders
```

## Execution Flow

When you run `bergen.py` with the LLM rewriter enabled:

1. **Retrieval**: Retrieves top-k documents (e.g., 50)
2. **Reranking** (optional): Reranks to top-k (e.g., 50)
3. **Selection**: Selects top `generation_top_k` documents (e.g., 5)
4. **Rewriting** (NEW): Each of the 5 documents is rewritten using the generator LLM
5. **Generation**: The rewritten documents are passed to the generator for answer generation

## Performance Considerations

### Computational Cost
- The rewriter adds one LLM inference pass per document
- For `generation_top_k=5`, batch_size=4: ~2 additional inference batches per query
- Total time increase: ~20-50% depending on document length and LLM speed

### Memory Usage
- The generator LLM is reused (no additional model loading)
- Memory for rewritten contexts is temporary
- Use lower `batch_size` if you encounter OOM errors

### Optimization Tips
1. **Reduce batch size** if you have memory issues
2. **Decrease max_new_tokens** for shorter rewrites (faster, less memory)
3. **Use process_separately=false** to process all docs together (fewer batches)
4. **Adjust generation_top_k** to rewrite fewer documents

## Custom Prompts

Create your own rewriting strategy by defining a custom prompt:

```yaml
context_processor:
    init_args:
        _target_: models.context_processors.llm_rewriter.LLMRewriter
        generator: null
        batch_size: 4
        max_new_tokens: 256
        process_separately: true
        rewrite_prompt_template: |
            You are an expert at refining information.
            
            Query: {query}
            Document: {passage}
            
            Instructions:
            1. Keep only information relevant to the query
            2. Expand abbreviations and clarify technical terms
            3. Make the text flow naturally
            
            Refined Document:
```

## Metrics

The rewriter automatically computes:
- **Context Compression Ratio**: Percentage reduction in text length
  - Saved in: `experiments/your_run/eval_dev_context_metrics.json`
  - Formula: `(original_length - rewritten_length) / original_length * 100`

## Output Files

When running with the rewriter, you'll find:
- `processed_contexts/`: Cached rewritten contexts
- `experiments/your_run/eval_dev_context_metrics.json`: Compression metrics
- Original contexts are also saved for comparison

## Debugging

To test the rewriter in isolation:

```python
from models.context_processors.llm_rewriter import LLMRewriter
from models.generators.llm import LLM  # or your generator class

# Load generator
generator = LLM(model_name="meta-llama/Meta-Llama-3-8B-Instruct", ...)

# Create rewriter
rewriter = LLMRewriter(generator=generator, batch_size=2)

# Test
queries = ["What is the capital of France?"]
contexts = [["Paris is a city. It is the capital.", "France is in Europe."]]

rewritten, metrics = rewriter.process(contexts, queries)
print(rewritten)
```

## Troubleshooting

### Issue: "generator is None"
**Solution**: Make sure you have a generator configured in your main config

### Issue: OOM (Out of Memory)
**Solution**: Reduce `batch_size` or `max_new_tokens` in the context processor config

### Issue: Rewriting is too slow
**Solution**: 
- Decrease `generation_top_k` to rewrite fewer documents
- Use `process_separately=false` for batch processing
- Reduce `max_new_tokens`

### Issue: Rewritten contexts are poor quality
**Solution**: 
- Customize the `rewrite_prompt_template` for your use case
- Ensure your generator model is capable of text refinement tasks
- Try different generator models

## Example Runs

### Basic usage with LLaMA-3:
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=5 \
    run_name=nq_with_rewriter
```

### Using GPT-4 as both generator and rewriter:
```bash
python bergen.py \
    dataset=kilt_triviaqa \
    retriever=bm25 \
    generator=openai_gpt4 \
    context_processor=llm_rewriter/rewriter_custom_prompt \
    generation_top_k=3 \
    run_name=triviaqa_gpt4_rewriter
```

### With reranking:
```bash
python bergen.py \
    dataset=bioasq11b \
    retriever=contriever \
    reranker=monoT5 \
    generator=mistral-7b-chat \
    context_processor=llm_rewriter/rewriter_with_title \
    retrieve_top_k=100 \
    rerank_top_k=20 \
    generation_top_k=5 \
    run_name=bioasq_full_pipeline
```
