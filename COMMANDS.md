# Quick Command Reference - LLM Rewriter

## Test the Implementation
```bash
# Run test suite
python test_llm_rewriter.py

# Show visual flow diagram
python show_rewriter_flow.py
```

## Basic Usage

### Option 1: Command Line (Simplest)
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=5
```

### Option 2: Config File (Recommended)
```bash
# Use pre-made config
python bergen.py --config-name=rag_with_rewriter

# Or create your own config in config/ folder, then:
python bergen.py --config-name=my_config
```

### Option 3: Environment Variable
```bash
export CONFIG=rag_with_rewriter
python bergen.py
```

## Rewriter Variants

### Separate Document Rewriting (Default)
```bash
python bergen.py context_processor=llm_rewriter/rewriter_basic
```

### Combined Document Rewriting
```bash
python bergen.py context_processor=llm_rewriter/rewriter_combined
```

### Title-Preserving Rewriting
```bash
python bergen.py context_processor=llm_rewriter/rewriter_with_title
```

### Custom Prompt
```bash
python bergen.py context_processor=llm_rewriter/rewriter_custom_prompt
```

## Common Parameters

```bash
python bergen.py \
    dataset=kilt_nq \                          # Dataset
    retriever=contriever \                     # Retrieval model
    generator=llama-3-8b-instruct \            # LLM for rewriting + generation
    context_processor=llm_rewriter/rewriter_basic \  # Enable rewriter
    retrieve_top_k=50 \                        # Retrieve 50 docs
    rerank_top_k=50 \                          # Rerank 50 docs
    generation_top_k=5 \                       # Rewrite 5, generate with 5
    run_name=my_experiment                     # Experiment name
```

## Dataset Options

```bash
# KILT datasets
dataset=kilt_nq
dataset=kilt_triviaqa
dataset=kilt_hotpotqa
dataset=kilt_fever
dataset=kilt_eli5

# MKQA (multilingual)
dataset=mkqa_en
dataset=mkqa_fr
dataset=mkqa_de
dataset=mkqa_es

# BioASQ
dataset=bioasq11b
```

## Retriever Options

```bash
retriever=bm25                    # Sparse retrieval
retriever=contriever              # Dense retrieval
retriever=bge-large-en-v1.5       # BGE model
retriever=e5-large-v2             # E5 model
retriever=dragon+                 # Dragon
```

## Generator Options

```bash
# LLaMA models
generator=llama-3-8b-instruct
generator=llama-2-7b-chat
generator=llama-2-13b-chat

# Mistral models
generator=mistral-7b-chat
generator=mixtral-moe-7b-chat

# Qwen models
generator=qwen-25-7b-instruct
generator=qwen-25-3b-instruct

# OpenAI (requires API key)
generator=openai_gpt4
generator=openai_gpt4o
```

## Reranker Options

```bash
reranker=null                     # No reranking
reranker=monoT5                   # T5-based reranker
reranker=cross-encoder            # Cross-encoder
```

## Advanced Examples

### Full Pipeline with Reranking
```bash
python bergen.py \
    dataset=kilt_hotpotqa \
    retriever=contriever \
    reranker=monoT5 \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    retrieve_top_k=100 \
    rerank_top_k=20 \
    generation_top_k=5 \
    run_name=hotpot_full_pipeline
```

### Multilingual with Rewriter
```bash
python bergen.py \
    dataset=mkqa_fr \
    retriever=bge-m3 \
    generator=mistral-7b-chat \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=5 \
    run_name=mkqa_french_rewriter
```

### BioASQ with Custom Rewriter
```bash
python bergen.py \
    dataset=bioasq11b \
    retriever=dragon+ \
    generator=llama-2-13b-chat \
    context_processor=llm_rewriter/rewriter_custom_prompt \
    generation_top_k=3 \
    run_name=bioasq_custom_rewriter
```

### Debug Mode (Small Subset)
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=bm25 \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=3 \
    debug=true \
    run_name=debug_test
```

### With Training
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=contriever \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    train=lora_training \
    generation_top_k=5 \
    run_name=train_with_rewriter
```

## Customizing Rewriter Config

### Edit config file directly:
```bash
# Edit this file:
nano config/context_processor/llm_rewriter/rewriter_basic.yaml

# Change parameters like:
batch_size: 2          # Reduce if OOM
max_new_tokens: 128    # Reduce for faster rewriting
```

### Override from command line:
```bash
python bergen.py \
    context_processor=llm_rewriter/rewriter_basic \
    context_processor.init_args.batch_size=2 \
    context_processor.init_args.max_new_tokens=128
```

## Output Locations

```bash
# Generated answers and metrics
experiments/{run_name}/
├── eval_dev_out.json              # Answers
├── eval_dev_metrics.json          # Quality metrics
└── eval_dev_context_metrics.json  # Rewriter metrics

# Cached rewritten contexts
processed_contexts/
└── {dataset}_{retriever}_{rewriter}.json

# Retrieval runs
runs/
└── run.{retriever}.{dataset}.trec
```

## Monitoring Progress

### View experiment results:
```bash
# After running
cat experiments/{run_name}/eval_dev_metrics.json

# View compression ratio
cat experiments/{run_name}/eval_dev_context_metrics.json
```

### Compare with/without rewriter:
```bash
# Run without rewriter
python bergen.py dataset=kilt_nq retriever=bm25 generator=llama-3-8b-instruct \
    context_processor=null run_name=baseline

# Run with rewriter
python bergen.py dataset=kilt_nq retriever=bm25 generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic run_name=with_rewriter

# Compare
python print_results.py --runs baseline with_rewriter
```

## Troubleshooting Commands

### Check if config is valid:
```bash
python -c "from omegaconf import OmegaConf; print(OmegaConf.load('config/context_processor/llm_rewriter/rewriter_basic.yaml'))"
```

### Test with minimal settings:
```bash
python bergen.py \
    dataset=kilt_nq \
    retriever=bm25 \
    generator=llama-3-8b-instruct \
    context_processor=llm_rewriter/rewriter_basic \
    generation_top_k=1 \
    debug=true
```

### Check GPU memory:
```bash
nvidia-smi
watch -n 1 nvidia-smi  # Monitor during execution
```

## Performance Optimization

### Reduce memory usage:
```bash
python bergen.py \
    context_processor.init_args.batch_size=1 \
    context_processor.init_args.max_new_tokens=100
```

### Speed up rewriting:
```bash
python bergen.py \
    generation_top_k=3 \  # Fewer docs to rewrite
    context_processor.init_args.batch_size=8  # Larger batches (if memory allows)
```

### Use combined mode (faster):
```bash
python bergen.py \
    context_processor=llm_rewriter/rewriter_combined  # All docs in one pass
```

## Getting Help

```bash
# Show all available options
python bergen.py --help

# Show rewriter documentation
cat documentation/llm_rewriter.md

# Run tests
python test_llm_rewriter.py

# View flow diagram
python show_rewriter_flow.py
```
