# LLM Rewriter Update: Concatenation Mode

## What Changed?

The LLM rewriter now **concatenates** the rewritten version with the original document by default, rather than replacing it. This means the generator receives both the original document and the refined version together.

## Why This Change?

You requested: *"I want to concatenate that rewritten part to the original context it is sending to the generator"*

This approach is more conservative and preserves all information while still providing the refined, query-focused version.

## New Default Behavior

### Before (Old Behavior - Replacement):
```
Generator receives:
  Document 1: [Rewritten Doc 1]
  Document 2: [Rewritten Doc 2]
```

### After (New Behavior - Concatenation):
```
Generator receives:
  Document 1: [Original Doc 1]
  
  Refined version: [Rewritten Doc 1]
  
  Document 2: [Original Doc 2]
  
  Refined version: [Rewritten Doc 2]
```

## Configuration

### Use Concatenation (DEFAULT):
```bash
python bergen.py context_processor=llm_rewriter/rewriter_basic
```

### Use Replacement (Old Behavior):
```bash
python bergen.py context_processor=llm_rewriter/rewriter_replace_only
```

### Toggle via Command Line:
```bash
# Concatenate
python bergen.py context_processor.init_args.concatenate_original=true

# Replace
python bergen.py context_processor.init_args.concatenate_original=false
```

## Files Updated

### Core Implementation:
- `models/context_processors/llm_rewriter.py`
  - Added `concatenate_original` parameter (default: `true`)
  - Updated all three rewriter classes to support concatenation

### Config Files:
- `config/context_processor/llm_rewriter/rewriter_basic.yaml` - Updated
- `config/context_processor/llm_rewriter/rewriter_combined.yaml` - Updated
- `config/context_processor/llm_rewriter/rewriter_with_title.yaml` - Updated
- `config/context_processor/llm_rewriter/rewriter_custom_prompt.yaml` - Updated
- `config/context_processor/llm_rewriter/rewriter_replace_only.yaml` - NEW (for old behavior)

### Documentation:
- `documentation/rewriter_concatenation.md` - NEW detailed guide
- `LLM_REWRITER_README.md` - Updated
- `show_concatenation_example.py` - NEW visual examples

## Complete Example

```bash
# Query: "What is the capital of France?"

# Original retrieved document:
"Paris is the capital and most populous city of France. It has an area 
of 105 square kilometres. The city has a population of 2.2 million. 
Paris was founded in the 3rd century BC."

# What the GENERATOR now receives (with concatenation):
"Paris is the capital and most populous city of France. It has an area 
of 105 square kilometres. The city has a population of 2.2 million. 
Paris was founded in the 3rd century BC.

Refined version: Paris is the capital city of France, serving as the 
political and cultural center of the nation."
```

## Quick Start

1. **Test the implementation:**
   ```bash
   python test_llm_rewriter.py
   ```

2. **See concatenation examples:**
   ```bash
   python show_concatenation_example.py
   ```

3. **Run with concatenation (default):**
   ```bash
   python bergen.py \
       dataset=kilt_nq \
       retriever=contriever \
       generator=llama-3-8b-instruct \
       context_processor=llm_rewriter/rewriter_basic \
       generation_top_k=5
   ```

4. **Run without concatenation (replace mode):**
   ```bash
   python bergen.py \
       dataset=kilt_nq \
       retriever=contriever \
       generator=llama-3-8b-instruct \
       context_processor=llm_rewriter/rewriter_replace_only \
       generation_top_k=5
   ```

## Benefits of Concatenation

✅ **No Information Loss**: All original details are preserved  
✅ **Dual Perspective**: Generator can use full context or refined summary  
✅ **Query Focus**: Refined version highlights relevant information  
✅ **Safer**: If rewriting quality varies, original is still available  
✅ **Flexible**: Generator learns to leverage both versions  

## Trade-offs

⚠️ **Longer Context**: ~2x the original length  
⚠️ **Higher Token Cost**: More tokens for API-based models  
⚠️ **Slightly Slower**: More tokens to process during generation  

## When to Use Each Mode

| Use Concatenation When: | Use Replacement When: |
|-------------------------|----------------------|
| Answer quality is critical | Context length is a concern |
| Information is dense | Documents are very redundant |
| Multi-hop reasoning needed | API costs are important |
| Rewriter quality varies | Rewriter quality is consistently high |
| Default choice | Performance optimization needed |

## Backward Compatibility

The old behavior (replacement) is still available via:
- `context_processor=llm_rewriter/rewriter_replace_only` config
- `concatenate_original=false` parameter

No existing code is broken - concatenation is opt-in via the default configs.

## Testing Both Modes

Compare performance:

```bash
# Test concatenation
python bergen.py \
    dataset=kilt_nq \
    retriever=bm25 \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    run_name=concat_test

# Test replacement
python bergen.py \
    dataset=kilt_nq \
    retriever=bm25 \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_replace_only \
    run_name=replace_test

# Compare
python print_results.py --runs concat_test replace_test
```

## Documentation

- **Quick Start**: `LLM_REWRITER_README.md`
- **Concatenation Details**: `documentation/rewriter_concatenation.md`
- **Full Guide**: `documentation/llm_rewriter.md`
- **Visual Examples**: Run `python show_concatenation_example.py`
- **Technical Details**: `IMPLEMENTATION_SUMMARY.md`

## Summary

The rewriter now **appends** refined versions to original documents by default, giving the generator access to both. This is a safer, more robust approach while still providing query-focused refinement. You can still use replacement mode if needed.
