# Document Sources in BERGEN RAG Pipeline

## Quick Answer

**Yes, the codebase downloads Wikipedia pages** from HuggingFace datasets when you run `bergen.py`. The documents are automatically downloaded, processed, cached, and then used for retrieval.

## How It Works

### 1. **Dataset Configuration**

When you run bergen with a dataset like `kilt_nq`, the config specifies both:
- **Query dataset**: Questions to answer (e.g., Natural Questions)
- **Document dataset**: Wikipedia corpus to retrieve from

Example from `config/dataset/kilt_nq.yaml`:
```yaml
dev:
    doc: 
        init_args:
            _target_: modules.dataset_processor.KILT100w  # Wikipedia documents
            split: "full"
    
    query: 
        init_args:
            _target_: modules.processors.kilt_dataset_processor.KILTNQ  # Questions
            split: "validation"
```

### 2. **Wikipedia Download Sources**

The codebase uses **HuggingFace datasets** to download Wikipedia:

| Dataset Processor | HuggingFace Dataset | Wikipedia Version |
|-------------------|---------------------|-------------------|
| `KILT100w` | `kilt_wikipedia` | 2019 Wikipedia snapshot |
| `Wiki_monolingual_100w` | `wikimedia/wikipedia` | 2023 Wikipedia (multilingual) |
| `Wikipedia2023_section` | `rasdani/cohere-wikipedia-2023-11-en` | 2023 Wikipedia |
| `Wikipedia2023_full` | `Cohere/wikipedia-2023-11-embed-multilingual-v3` | 2023 Wikipedia |

### 3. **Document Processing**

The Wikipedia pages are downloaded and then:

1. **Split into passages**: 
   - `KILT100w`: Splits into 100-word chunks
   - `Wikipedia2023_section`: Uses predefined sections
   - Each passage gets an ID

2. **Formatted with title**:
   ```
   [Title]. [100-word passage text]
   ```

3. **Stored locally** in `datasets/` folder (e.g., `datasets/kilt-100w_full/`)

4. **Cached** - downloaded only once, reused for all future runs

### 4. **What Gets Downloaded**

For KILT datasets (most common):
```python
# From modules/dataset_processor.py, KILT100w class:

hf_name = 'kilt_wikipedia'  # HuggingFace dataset
dataset = datasets.load_dataset(hf_name, num_proc=self.num_proc)[self.split]

# Each Wikipedia article is split into 100-word passages:
def map_100w(sample, num_words=100):
    wiki_id = sample['wikipedia_id']
    title = sample['wikipedia_title']
    passages = [x.strip() for x in sample["text"]["paragraph"]]
    doc = " ".join(passages)
    words = doc.split()
    # Create overlapping 100-word chunks
    paragraphs = [title + '. ' + " ".join(words[i:i + num_words]) 
                  for i in range(0, len(words), num_words)]
    return {'paragraphs': paragraphs}
```

### 5. **Storage Locations**

After first run:

```
mr-rag/
├── datasets/                    # Downloaded & processed data
│   ├── kilt-100w_full/         # Wikipedia passages (~5.9M passages)
│   │   ├── data-00000-of-*.arrow
│   │   ├── dataset_info.json
│   │   └── id2index.p
│   └── KILTNQ_validation/      # Questions
│
├── indexes/                     # Encoded embeddings (if using dense retriever)
│   └── kilt-100w_doc_[retriever_name]/
│       ├── embeddings_0.pt
│       ├── embeddings_1.pt
│       └── ...
│
└── runs/                        # Retrieval results (cached)
    └── run.[retriever].[dataset].trec
```

## Execution Flow

```
1. You run: python bergen.py dataset=kilt_nq retriever=bm25 generator=llama-3-8b

2. Dataset Loading:
   ├─ Check if datasets/kilt-100w_full/ exists
   │  ├─ YES → Load from disk (fast)
   │  └─ NO → Download from HuggingFace
   │            ├─ Download kilt_wikipedia dataset
   │            ├─ Process into 100-word passages
   │            └─ Save to datasets/kilt-100w_full/
   │
   └─ Check if datasets/KILTNQ_validation/ exists
      ├─ YES → Load from disk
      └─ NO → Download questions from HuggingFace

3. Retrieval:
   ├─ For each question, search through ~5.9M Wikipedia passages
   └─ Return top-k most relevant passages

4. Rewriting (if enabled):
   └─ Refine the retrieved passages with LLM

5. Generation:
   └─ Use refined passages to answer the question
```

## Size & Download Time

| Dataset | # Passages | Download Size | First-Run Time |
|---------|-----------|---------------|----------------|
| KILT Wikipedia (100w) | ~5.9M | ~3-4 GB | 10-30 min |
| Wikipedia 2023 (en) | ~41M | ~20 GB | 1-2 hours |
| Multilingual Wikipedia | Varies | ~50+ GB | 2-3 hours |

**Good news**: Downloads happen **only once**. Subsequent runs reuse cached data.

## Checking What Will Be Downloaded

Before running, check the dataset config:

```bash
# View what dataset will be used
cat config/dataset/kilt_nq.yaml

# Output shows:
# doc: KILT100w (Wikipedia passages)
# query: KILTNQ (Natural Questions)
```

Common document datasets:
- `KILT100w` - KILT Wikipedia 2019 (~5.9M passages)
- `Wiki_monolingual_100w` - Wikipedia 2023 (various languages)
- `Wikipedia2023_section` - 2023 Wikipedia sections
- `MSMarco` - MS MARCO documents
- `PubMed` - Biomedical articles

## Controlling Downloads

### Use Pre-downloaded Indexes

Download pre-encoded indexes to skip encoding:
```bash
mkdir -p indexes
cd indexes
wget https://download.europe.naverlabs.com/bergen/kilt-100w_doc_Shitao_RetroMAE_MSMARCO_distill.tar
tar -xvf kilt-100w_doc_Shitao_RetroMAE_MSMARCO_distill.tar
```

### Skip Datasets

Set to null in config:
```yaml
dev:
    doc: null  # Don't load documents (won't work for retrieval)
    query: ...
```

### Overwrite Downloaded Data

Force re-download:
```bash
python bergen.py +overwrite_datasets=True
```

### Use Existing Retrieval Runs

The `runs/` folder contains pre-computed retrieval results. If a run file exists, it's reused (no retrieval needed).

## Where Documents Come From

```
HuggingFace Datasets → Download → Process → Cache Locally → Index → Retrieve
       ↓                   ↓            ↓           ↓           ↓         ↓
  kilt_wikipedia    (First run)   100-word   datasets/   indexes/   runs/
                                  chunks      
```

## Example: KILT Natural Questions

```bash
python bergen.py dataset=kilt_nq retriever=bm25 generator=llama-3-8b-instruct

# What happens:
# 1. Downloads KILT Wikipedia (~3-4 GB) from HuggingFace
# 2. Splits into ~5.9M passages of 100 words each
# 3. Saves to: datasets/kilt-100w_full/
# 4. Downloads NQ questions from HuggingFace
# 5. Saves to: datasets/KILTNQ_validation/
# 6. For each question:
#    - Retrieves top-50 passages from Wikipedia
#    - (Optional) Rewrites passages with LLM
#    - Generates answer using LLM + passages
```

## Using Different Document Collections

### KILT Wikipedia (2019) - Default
```bash
python bergen.py dataset=kilt_nq  # Uses KILT100w
```

### Wikipedia 2023
```bash
python bergen.py dataset=kilt_nq_wiki2024  # Uses Wikipedia2023
```

### Multilingual Wikipedia
```bash
python bergen.py dataset=mkqa_fr  # Uses French Wikipedia
```

### MS MARCO
```bash
python bergen.py dataset=msmarco  # Uses MS MARCO docs
```

### PubMed (Biomedical)
```bash
python bergen.py dataset=bioasq11b  # Uses PubMed articles
```

## Offline Usage

After first run, you can work offline:
1. Documents are cached in `datasets/`
2. Indexes are cached in `indexes/`
3. Runs are cached in `runs/`

No internet needed for subsequent runs with same dataset/retriever.

## Summary

✅ **Yes, Wikipedia pages are downloaded** from HuggingFace  
✅ **Downloaded only once** (cached locally)  
✅ **Automatically processed** into retrievable passages  
✅ **Multiple versions available** (2019, 2023, multilingual)  
✅ **Can use pre-computed indexes** to skip encoding  
✅ **Works offline** after first download  

The system is designed to handle everything automatically - you just specify the dataset and it takes care of downloading, processing, and caching.
