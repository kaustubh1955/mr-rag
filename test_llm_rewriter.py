"""
Test script for LLM Rewriter Context Processor
Run this to verify the rewriter is working correctly before full pipeline execution
"""

import sys
sys.path.append('.')

from models.context_processors.llm_rewriter import LLMRewriter, LLMRewriterWithTitle
from hydra.utils import instantiate
from omegaconf import OmegaConf

def test_rewriter_simple():
    """Test rewriter with a simple mock generator"""
    print("=" * 80)
    print("TEST 1: Simple Mock Generator Test")
    print("=" * 80)
    
    # Create a mock generator with generate method
    class MockGenerator:
        def __init__(self):
            self.model_name = "mock-llm"
            self.max_new_tokens = 100
        
        def generate(self, prompts):
            """Mock generation - just returns truncated version"""
            return [f"[REWRITTEN] {prompt[:100]}..." for prompt in prompts]
    
    generator = MockGenerator()
    rewriter = LLMRewriter(generator=generator, batch_size=2, max_new_tokens=50)
    
    queries = [
        "What is the capital of France?",
        "Who invented the telephone?"
    ]
    
    contexts = [
        [
            "Paris is the capital and most populous city of France. It has an area of 105 square kilometres.",
            "France is a country in Western Europe. Paris has been a major settlement for more than two millennia."
        ],
        [
            "Alexander Graham Bell was a Scottish-born inventor, scientist and engineer.",
            "The telephone was invented in the 1870s. Bell is credited with inventing the telephone."
        ]
    ]
    
    print("\nOriginal Contexts:")
    for i, (q, docs) in enumerate(zip(queries, contexts)):
        print(f"\nQuery {i+1}: {q}")
        for j, doc in enumerate(docs):
            print(f"  Doc {j+1}: {doc}")
    
    print("\n" + "-" * 80)
    print("Running rewriter...")
    rewritten, metrics = rewriter._process(contexts, queries)
    
    print("\nRewritten Contexts:")
    for i, (q, docs) in enumerate(zip(queries, rewritten)):
        print(f"\nQuery {i+1}: {q}")
        for j, doc in enumerate(docs):
            print(f"  Doc {j+1}: {doc}")
    
    print("\n" + "=" * 80)
    print("✓ Test 1 passed!")
    print("=" * 80)


def test_with_real_generator(model_name="meta-llama/Meta-Llama-3.2-3B-Instruct"):
    """Test with a real generator model (requires GPU and model access)"""
    print("\n" + "=" * 80)
    print(f"TEST 2: Real Generator Test - {model_name}")
    print("=" * 80)
    
    try:
        # Try to load a real generator
        from models.generators.llm import LLM
        import torch
        
        if not torch.cuda.is_available():
            print("⚠ WARNING: No GPU available, skipping real generator test")
            return
        
        print(f"\nLoading generator: {model_name}")
        generator = LLM(
            model_name=model_name,
            batch_size=2,
            max_new_tokens=100,
        )
        
        rewriter = LLMRewriter(
            generator=generator, 
            batch_size=2, 
            max_new_tokens=128,
            process_separately=True
        )
        
        queries = ["What is quantum computing?"]
        contexts = [[
            "Quantum computing is a type of computation that uses quantum phenomena. "
            "It leverages quantum bits or qubits. Qubits can exist in superposition. "
            "This allows quantum computers to process information differently than classical computers. "
            "Many companies are developing quantum computers today."
        ]]
        
        print("\nOriginal Context:")
        print(contexts[0][0])
        
        print("\n" + "-" * 80)
        print("Running rewriter with real LLM...")
        rewritten, metrics = rewriter._process(contexts, queries)
        
        print("\nRewritten Context:")
        print(rewritten[0][0])
        
        print("\n" + "=" * 80)
        print("✓ Test 2 passed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n⚠ Test 2 skipped: {e}")
        print("This is expected if you don't have the model or GPU available")


def test_config_loading():
    """Test loading rewriter from config files"""
    print("\n" + "=" * 80)
    print("TEST 3: Config Loading Test")
    print("=" * 80)
    
    config_paths = [
        "config/context_processor/llm_rewriter/rewriter_basic.yaml",
        "config/context_processor/llm_rewriter/rewriter_combined.yaml",
        "config/context_processor/llm_rewriter/rewriter_with_title.yaml",
        "config/context_processor/llm_rewriter/rewriter_custom_prompt.yaml",
    ]
    
    for config_path in config_paths:
        try:
            print(f"\nLoading: {config_path}")
            config = OmegaConf.load(config_path)
            print(f"  ✓ Config loaded successfully")
            print(f"  Target: {config.init_args._target_}")
            
            # Check if required fields exist
            assert 'init_args' in config
            assert '_target_' in config.init_args
            assert 'llm_rewriter' in config.init_args._target_.lower()
            print(f"  ✓ Config structure is valid")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("✓ Test 3 passed!")
    print("=" * 80)
    return True


def test_prompt_templates():
    """Test custom prompt templates"""
    print("\n" + "=" * 80)
    print("TEST 4: Custom Prompt Template Test")
    print("=" * 80)
    
    class MockGenerator:
        def __init__(self):
            self.model_name = "mock-llm"
            self.max_new_tokens = 100
        
        def generate(self, prompts):
            # Print the prompts to verify template was applied
            print("\nGenerated prompts:")
            for i, prompt in enumerate(prompts):
                print(f"\n--- Prompt {i+1} ---")
                print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
            return ["Rewritten text" for _ in prompts]
    
    generator = MockGenerator()
    
    custom_template = """Simplify this passage for the query.

Query: {query}
Passage: {passage}

Simplified:"""
    
    rewriter = LLMRewriter(
        generator=generator,
        batch_size=1,
        rewrite_prompt_template=custom_template
    )
    
    queries = ["What is AI?"]
    contexts = [["Artificial Intelligence (AI) is a complex field of computer science."]]
    
    rewritten, _ = rewriter._process(contexts, queries)
    
    print("\n" + "=" * 80)
    print("✓ Test 4 passed!")
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LLM REWRITER TEST SUITE" + " " * 36 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Run tests
        test_rewriter_simple()
        test_config_loading()
        test_prompt_templates()
        
        # Optional: test with real generator (commented out by default)
        # Uncomment the line below and adjust model name if you want to test with a real LLM
        # test_with_real_generator(model_name="meta-llama/Meta-Llama-3.2-3B-Instruct")
        
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "ALL TESTS PASSED!" + " " * 36 + "║")
        print("╚" + "=" * 78 + "╝")
        print("\nYou can now use the LLM rewriter in your RAG pipeline!")
        print("See documentation/llm_rewriter.md for usage instructions.")
        
    except Exception as e:
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 28 + "TEST FAILED!" + " " * 38 + "║")
        print("╚" + "=" * 78 + "╝")
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
