# LLM Rewriter - Concatenation vs Replacement

## Updated Behavior (Default: Concatenation)

By default, the LLM rewriter now **concatenates** the rewritten version with the original document, rather than replacing it. This means the generator receives both versions.

## How It Works

### Example Input (Original Document):
```
Paris is the capital and most populous city of France. It has an area of 105 
square kilometres. The city has a population of 2.2 million. Paris was founded 
in the 3rd century BC. The city has many famous museums and landmarks.
```

### Query:
```
What is the capital of France?
```

### Rewritten Version:
```
Paris is the capital city of France, serving as the political and cultural center.
```

### What the Generator Receives (Concatenation Mode - DEFAULT):
```
Paris is the capital and most populous city of France. It has an area of 105 
square kilometres. The city has a population of 2.2 million. Paris was founded 
in the 3rd century BC. The city has many famous museums and landmarks.

Refined version: Paris is the capital city of France, serving as the political 
and cultural center.
```

### What the Generator Receives (Replace Mode):
```
Paris is the capital city of France, serving as the political and cultural center.
```

## Why Concatenation?

1. **Preserves Information**: Original details remain available to the generator
2. **Highlights Relevance**: The refined version emphasizes query-relevant information
3. **Best of Both Worlds**: Generator can use full details OR the focused summary
4. **Reduces Risk**: If rewriting removes important info, it's still in the original

## Configuration

### Default (Concatenation):
```yaml
context_processor: llm_rewriter/rewriter_basic
```

or explicitly:
```yaml
init_args:
  concatenate_original: true  # DEFAULT
```

### Replace Mode (No Concatenation):
```yaml
context_processor: llm_rewriter/rewriter_replace_only
```

or explicitly:
```yaml
init_args:
  concatenate_original: false
```

## Available Configs

| Config | Mode | Behavior |
|--------|------|----------|
| `rewriter_basic.yaml` | Concatenate (default) | Original + Rewritten |
| `rewriter_combined.yaml` | Concatenate | All originals + Combined rewrite |
| `rewriter_with_title.yaml` | Concatenate | Original + Title+Rewritten |
| `rewriter_custom_prompt.yaml` | Concatenate | Original + Custom rewrite |
| `rewriter_replace_only.yaml` | Replace | Rewritten only (no original) |

## Command Line Usage

### With Concatenation (Default):
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=5
```

### Without Concatenation (Replace):
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_replace_only \
    generation_top_k=5
```

### Override from Command Line:
```bash
# Enable concatenation
python bergen.py \
    context_processor=llm_rewriter/rewriter_basic \
    context_processor.init_args.concatenate_original=true

# Disable concatenation
python bergen.py \
    context_processor=llm_rewriter/rewriter_basic \
    context_processor.init_args.concatenate_original=false
```

## Output Format Examples

### Separate Documents (process_separately=true, concatenate_original=true):
```
Document 1: [Original Doc 1]

Refined version: [Rewritten Doc 1]

Document 2: [Original Doc 2]

Refined version: [Rewritten Doc 2]
```

### Combined Documents (process_separately=false, concatenate_original=true):
```
Document 1: [Original Doc 1]

Document 2: [Original Doc 2]

Document 3: [Original Doc 3]

Refined version:
[Combined rewritten version synthesizing all docs]
```

### Replace Mode (concatenate_original=false):
```
Document 1: [Rewritten Doc 1]

Document 2: [Rewritten Doc 2]
```

## Performance Impact

### Concatenation Mode:
- **Context Length**: ~2x longer (original + rewritten)
- **Generation Time**: Slightly slower (more tokens to process)
- **Token Cost**: Higher for API-based models
- **Quality**: Better - preserves all information

### Replace Mode:
- **Context Length**: Same as rewritten length
- **Generation Time**: Faster (fewer tokens)
- **Token Cost**: Lower for API-based models
- **Quality**: Depends on rewriting quality

## Recommendations

| Scenario | Recommendation |
|----------|----------------|
| **High-stakes QA** | Concatenation (default) - preserves all info |
| **Long documents** | Replace - reduces context length |
| **API costs matter** | Replace - fewer tokens |
| **Information-dense docs** | Concatenation - keeps details |
| **Noisy/redundant docs** | Replace - cleaner context |
| **Multi-hop reasoning** | Concatenation - needs full context |

## Testing Both Modes

Run experiments with both modes to see which works better for your use case:

```bash
# With concatenation
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    run_name=nq_concat

# Without concatenation
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_replace_only \
    run_name=nq_replace

# Compare results
python print_results.py --runs nq_concat nq_replace
```
