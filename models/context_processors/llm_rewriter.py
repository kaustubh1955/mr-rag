"""
BERGEN
Copyright (c) 2024-present NAVER Corp.
CC BY-NC-SA 4.0 license

LLM-based context rewriter that refines retrieved passages in the context of the query.
This rewriter integrates internal knowledge, removes redundancy, and highlights relevant information.
"""

from models.context_processors.context_processor import ContextProcessor
import torch
from typing import List, Dict
from tqdm import tqdm


class LLMRewriter(ContextProcessor):
    """
    Uses an LLM to rewrite/refine retrieved documents for better coherence and relevance.
    
    Args:
        generator: The generator instance (LLM) to use for rewriting
        batch_size: Batch size for processing
        max_new_tokens: Maximum tokens to generate for each rewritten passage
        rewrite_prompt_template: Template for the rewriting prompt
        process_separately: If True, rewrite each document separately. If False, rewrite all docs together.
    """
    
    def __init__(
        self, 
        generator=None,
        batch_size: int = 4,
        max_new_tokens: int = 256,
        rewrite_prompt_template: str = None,
        process_separately: bool = True,
        concatenate_original: bool = True,
    ):
        super().__init__()
        self.generator = generator
        self.batch_size = batch_size
        self.max_new_tokens = max_new_tokens
        self.process_separately = process_separately
        self.concatenate_original = concatenate_original
        self.name = f"llm_rewriter_{self.generator.model_name.replace('/', '_')}"
        
        # Default prompt template for rewriting
        if rewrite_prompt_template is None:
            self.rewrite_prompt_template = """Given the following query and passage, rewrite the passage to:
1. Remove redundant information
2. Highlight information relevant to the query
3. Integrate any relevant knowledge to make it more coherent
4. Keep the passage concise and focused

Query: {query}

Original Passage: {passage}

Rewritten Passage:"""
        else:
            self.rewrite_prompt_template = rewrite_prompt_template
        
        # Track compression metrics
        self.predefined_context_processing_metrics = ["context_compression"]
    
    def _process(self, contexts: List[List[str]], queries: List[str]) -> tuple:
        """
        Process contexts by rewriting each passage using the LLM.
        
        Args:
            contexts: List of lists of documents (one list per query)
            queries: List of queries
            
        Returns:
            Tuple of (rewritten_contexts, metrics_dict)
        """
        rewritten_contexts = []
        total_processed = 0
        
        # Store original max_new_tokens to restore later
        original_max_new_tokens = self.generator.max_new_tokens
        self.generator.max_new_tokens = self.max_new_tokens
        
        if self.process_separately:
            # Rewrite each document separately
            all_prompts = []
            query_doc_mapping = []  # Track which query and doc index each prompt belongs to
            
            for query_idx, (query, docs) in enumerate(zip(queries, contexts)):
                for doc_idx, doc in enumerate(docs):
                    if len(doc.strip()) == 0:
                        continue
                    prompt = self.rewrite_prompt_template.format(query=query, passage=doc)
                    all_prompts.append(prompt)
                    query_doc_mapping.append((query_idx, doc_idx))
            
            # Generate rewritten passages in batches
            rewritten_passages = []
            with torch.no_grad():
                for batch_start in tqdm(range(0, len(all_prompts), self.batch_size), 
                                       desc='Rewriting contexts...'):
                    batch_prompts = all_prompts[batch_start:min(batch_start + self.batch_size, len(all_prompts))]
                    
                    # Create minimal data dict for generation
                    batch_dict = {
                        'model_input': batch_prompts,
                        'q_id': [f"temp_{i}" for i in range(len(batch_prompts))],
                        'instruction': batch_prompts,
                        'query': batch_prompts,
                        'label': [None] * len(batch_prompts),
                        'ranking_label': [None] * len(batch_prompts),
                    }
                    
                    # Generate using the LLM
                    try:
                        generated = self.generator.generate(batch_prompts)
                        rewritten_passages.extend(generated)
                    except Exception as e:
                        print(f"Error during generation: {e}")
                        # Fallback to original passages on error
                        rewritten_passages.extend(["" for _ in batch_prompts])
                    
                    total_processed += len(batch_prompts)
            
            # Reconstruct the nested structure - CONCATENATE or REPLACE based on config
            rewritten_contexts = [[""] * len(docs) for docs in contexts]
            for passage_idx, (query_idx, doc_idx) in enumerate(query_doc_mapping):
                original_text = contexts[query_idx][doc_idx]
                rewritten_text = rewritten_passages[passage_idx].strip()
                
                if len(rewritten_text) > 0:
                    if self.concatenate_original:
                        # Concatenate: Original + Rewritten version
                        concatenated = f"{original_text}\n\nRefined version: {rewritten_text}"
                        rewritten_contexts[query_idx][doc_idx] = concatenated
                    else:
                        # Replace with rewritten only
                        rewritten_contexts[query_idx][doc_idx] = rewritten_text
                else:
                    # If rewriting failed, just use original
                    rewritten_contexts[query_idx][doc_idx] = original_text
            
            # Fill in any empty docs that were skipped
            for query_idx, docs in enumerate(contexts):
                for doc_idx, doc in enumerate(docs):
                    if rewritten_contexts[query_idx][doc_idx] == "":
                        rewritten_contexts[query_idx][doc_idx] = docs[doc_idx]
                        
        else:
            # Rewrite all documents together for each query
            all_prompts = []
            
            for query, docs in zip(queries, contexts):
                # Combine all docs into one passage
                combined_passage = "\n\n".join([f"Passage {i+1}: {doc}" for i, doc in enumerate(docs) if len(doc.strip()) > 0])
                prompt = self.rewrite_prompt_template.format(query=query, passage=combined_passage)
                all_prompts.append(prompt)
            
            # Generate rewritten passages in batches
            rewritten_combined = []
            with torch.no_grad():
                for batch_start in tqdm(range(0, len(all_prompts), self.batch_size), 
                                       desc='Rewriting contexts...'):
                    batch_prompts = all_prompts[batch_start:min(batch_start + self.batch_size, len(all_prompts))]
                    
                    try:
                        generated = self.generator.generate(batch_prompts)
                        rewritten_combined.extend(generated)
                    except Exception as e:
                        print(f"Error during generation: {e}")
                        # Fallback to original passages on error
                        rewritten_combined.extend(["" for _ in batch_prompts])
                    
                    total_processed += len(batch_prompts)
            
            # Concatenate original + rewritten for combined mode (based on config)
            rewritten_contexts = []
            for query_idx, rewritten in enumerate(rewritten_combined):
                if len(rewritten.strip()) > 0:
                    if self.concatenate_original:
                        # Concatenate: Original docs + Rewritten version
                        original_combined = "\n\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(contexts[query_idx]) if len(doc.strip()) > 0])
                        concatenated = f"{original_combined}\n\nRefined version:\n{rewritten}"
                        rewritten_contexts.append([concatenated])
                    else:
                        # Replace with rewritten only
                        rewritten_contexts.append([rewritten])
                else:
                    # Fallback to original if rewriting failed - keep separate docs
                    rewritten_contexts.append(contexts[query_idx])
        
        # Restore original max_new_tokens
        self.generator.max_new_tokens = original_max_new_tokens
        
        # Return rewritten contexts and empty metrics dict (compression will be computed automatically)
        return rewritten_contexts, {}


class LLMRewriterWithTitle(ContextProcessor):
    """
    Variant that preserves document titles and only rewrites the content.
    Useful when document structure with titles is important.
    """
    
    def __init__(
        self, 
        generator=None,
        batch_size: int = 4,
        max_new_tokens: int = 256,
        rewrite_prompt_template: str = None,
        concatenate_original: bool = True,
    ):
        super().__init__()
        self.generator = generator
        self.batch_size = batch_size
        self.max_new_tokens = max_new_tokens
        self.concatenate_original = concatenate_original
        self.name = f"llm_rewriter_title_{self.generator.model_name.replace('/', '_')}"
        
        # Default prompt template for rewriting with title preservation
        if rewrite_prompt_template is None:
            self.rewrite_prompt_template = """Given the following query and passage with its title, rewrite ONLY the passage content to:
1. Remove redundant information
2. Highlight information relevant to the query
3. Integrate any relevant knowledge to make it more coherent
4. Keep the passage concise and focused

Do NOT include the title in your response, only output the rewritten content.

Query: {query}

Title: {title}

Original Content: {content}

Rewritten Content:"""
        else:
            self.rewrite_prompt_template = rewrite_prompt_template
        
        self.predefined_context_processing_metrics = ["context_compression"]
    
    def _split_title_content(self, doc: str) -> tuple:
        """Split document into title (first sentence) and content (rest)."""
        import nltk
        try:
            sentences = nltk.sent_tokenize(doc)
            if len(sentences) > 0:
                return sentences[0], " ".join(sentences[1:])
            else:
                return "", doc
        except:
            # Fallback if NLTK fails
            parts = doc.split(". ", 1)
            if len(parts) == 2:
                return parts[0] + ".", parts[1]
            else:
                return "", doc
    
    def _process(self, contexts: List[List[str]], queries: List[str]) -> tuple:
        """Process contexts by rewriting content while preserving titles."""
        
        # Store original max_new_tokens
        original_max_new_tokens = self.generator.max_new_tokens
        self.generator.max_new_tokens = self.max_new_tokens
        
        all_prompts = []
        query_doc_mapping = []
        titles = []
        
        for query_idx, (query, docs) in enumerate(zip(queries, contexts)):
            for doc_idx, doc in enumerate(docs):
                if len(doc.strip()) == 0:
                    continue
                    
                title, content = self._split_title_content(doc)
                titles.append(title)
                
                prompt = self.rewrite_prompt_template.format(
                    query=query, 
                    title=title, 
                    content=content
                )
                all_prompts.append(prompt)
                query_doc_mapping.append((query_idx, doc_idx))
        
        # Generate rewritten content in batches
        rewritten_contents = []
        with torch.no_grad():
            for batch_start in tqdm(range(0, len(all_prompts), self.batch_size), 
                                   desc='Rewriting contexts (with titles)...'):
                batch_prompts = all_prompts[batch_start:min(batch_start + self.batch_size, len(all_prompts))]
                
                try:
                    generated = self.generator.generate(batch_prompts)
                    rewritten_contents.extend(generated)
                except Exception as e:
                    print(f"Error during generation: {e}")
                    rewritten_contents.extend([""] * len(batch_prompts))
        
        # Reconstruct with titles - CONCATENATE or REPLACE based on config
        rewritten_contexts = [[""] * len(docs) for docs in contexts]
        for passage_idx, (query_idx, doc_idx) in enumerate(query_doc_mapping):
            original_text = contexts[query_idx][doc_idx]
            rewritten_text = rewritten_contents[passage_idx].strip()
            title = titles[passage_idx]
            
            if len(rewritten_text) == 0:
                # Fallback to original
                rewritten_contexts[query_idx][doc_idx] = original_text
            else:
                rewritten_with_title = f"{title} {rewritten_text}"
                if self.concatenate_original:
                    # Concatenate: Original + Refined version with title
                    concatenated = f"{original_text}\n\nRefined version: {rewritten_with_title}"
                    rewritten_contexts[query_idx][doc_idx] = concatenated
                else:
                    # Replace with rewritten only
                    rewritten_contexts[query_idx][doc_idx] = rewritten_with_title
        
        # Fill in any empty docs
        for query_idx, docs in enumerate(contexts):
            for doc_idx, doc in enumerate(docs):
                if rewritten_contexts[query_idx][doc_idx] == "":
                    rewritten_contexts[query_idx][doc_idx] = doc
        
        # Restore original max_new_tokens
        self.generator.max_new_tokens = original_max_new_tokens
        
        return rewritten_contexts, {}
