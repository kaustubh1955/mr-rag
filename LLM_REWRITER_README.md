# LLM Rewriter for RAG Pipeline - Quick Start

## What is this?

An LLM-based context rewriter that refines retrieved documents before passing them to the generator. By default, it **concatenates** the refined version with the original, giving the generator both perspectives. It uses the **same LLM** as your generator to:
- Remove redundant information
- Highlight relevant content
- Integrate internal knowledge
- Create coherent passages

**Default behavior:** Original document + Refined version (concatenated)

## Quick Setup (3 steps)

### 1. Choose a rewriter configuration

Pick one from `config/context_processor/llm_rewriter/`:
- `rewriter_basic.yaml` - Rewrites each doc separately (recommended)
- `rewriter_combined.yaml` - Rewrites all docs together
- `rewriter_with_title.yaml` - Preserves titles, rewrites content
- `rewriter_custom_prompt.yaml` - Custom prompt template

### 2. Add to your config file

Edit your config in `config/` or create a new one:

```yaml
defaults:
    - retriever: contriever
    - generator: llama-3-8b-instruct
    - dataset: kilt_nq
    - context_processor: llm_rewriter/rewriter_basic  # Add this!

generation_top_k: 5  # Number of docs to rewrite
```

### 3. Run bergen.py

```bash
python bergen.py --config-name=your_config
```

## Command Line Usage

```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=5
```

## Testing

Verify the installation:

```bash
python test_llm_rewriter.py
```

## Where It Fits in the Pipeline

```
Retrieval → Reranking → [NEW: Rewriting] → Generation
   (50)        (50)         (5)               (5)
```

The rewriter processes the top-5 documents (or whatever you set as `generation_top_k`) before they're passed to the generator.

## Configuration Options

In your context processor config:

```yaml
init_args:
    _target_: models.context_processors.llm_rewriter.LLMRewriter
    generator: null  # Auto-filled with your generator
    batch_size: 4    # Docs per batch
    max_new_tokens: 256  # Tokens per rewritten doc
    process_separately: true  # true=separate, false=combined
    concatenate_original: true  # true=append, false=replace (default: true)
```

## Performance Impact

- **Time**: +20-50% (depends on `generation_top_k` and model speed)
- **Memory**: No extra model loading (reuses generator)
- **Cost**: +1 LLM call per document

## Full Documentation

See `documentation/llm_rewriter.md` for:
- Detailed usage examples
- Custom prompt templates
- Troubleshooting guide
- Performance optimization tips

## Files Added

```
models/context_processors/llm_rewriter.py          # Implementation
config/context_processor/llm_rewriter/             # Configs
  ├── rewriter_basic.yaml
  ├── rewriter_combined.yaml
  ├── rewriter_with_title.yaml
  └── rewriter_custom_prompt.yaml
config/rag_with_rewriter.yaml                      # Example config
documentation/llm_rewriter.md                      # Full docs
test_llm_rewriter.py                               # Tests
```

## Example Output

**Query:** "What is the capital of France?"

**Before Rewriting:**
```
Document 1: Paris is the capital and most populous city of France. 
It has an area of 105 square kilometres. The city has a population 
of 2.2 million. Paris was founded in the 3rd century BC.
```

**After Rewriting (with concatenation - DEFAULT):**
```
Document 1: Paris is the capital and most populous city of France. 
It has an area of 105 square kilometres. The city has a population 
of 2.2 million. Paris was founded in the 3rd century BC.

Refined version: Paris is the capital city of France, serving as both 
the political and cultural center of the country.
```

**After Rewriting (replacement mode - concatenate_original=false):**
```
Document 1: Paris is the capital city of France, serving as both 
the political and cultural center of the country.
```

## Need Help?

1. Check `documentation/rewriter_concatenation.md` for concatenation details
2. Check `documentation/llm_rewriter.md` for full documentation
3. Run `python test_llm_rewriter.py` to verify setup
4. Run `python show_concatenation_example.py` to see concatenation examples
5. See example config: `config/rag_with_rewriter.yaml`
