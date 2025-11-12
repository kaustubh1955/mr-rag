"""
Visual Example: Concatenation vs Replacement Mode

Run this to see concrete examples of what the generator receives.
"""

def show_examples():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║           LLM REWRITER: CONCATENATION vs REPLACEMENT MODE                  ║
╚════════════════════════════════════════════════════════════════════════════╝

QUERY: "What is the capital of France?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORIGINAL RETRIEVED DOCUMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document 1:
Paris is the capital and most populous city of France. It has an area of 
105 square kilometres and a population of 2.2 million. The city was founded 
in the 3rd century BC by a Celtic tribe. Today, Paris is known for its many 
museums, monuments, and cultural landmarks including the Eiffel Tower and 
the Louvre Museum.

Document 2:
France is a country in Western Europe with several overseas territories. 
Paris has been a major European settlement for more than two millennia. 
The French Revolution began in Paris in 1789. The city is divided into 
20 districts called arrondissements.


════════════════════════════════════════════════════════════════════════════════
MODE 1: CONCATENATION (concatenate_original=true) ✅ DEFAULT
════════════════════════════════════════════════════════════════════════════════

What the Generator Receives:
────────────────────────────

Document 1:
Paris is the capital and most populous city of France. It has an area of 
105 square kilometres and a population of 2.2 million. The city was founded 
in the 3rd century BC by a Celtic tribe. Today, Paris is known for its many 
museums, monuments, and cultural landmarks including the Eiffel Tower and 
the Louvre Museum.

Refined version: Paris is the capital city of France, serving as the 
political, economic, and cultural center of the nation.

────────────────────────────

Document 2:
France is a country in Western Europe with several overseas territories. 
Paris has been a major European settlement for more than two millennia. 
The French Revolution began in Paris in 1789. The city is divided into 
20 districts called arrondissements.

Refined version: Paris is the capital of France and has been a significant 
European city throughout history.

────────────────────────────

✅ ADVANTAGES:
  • Preserves all original information
  • Refined version highlights query-relevant facts
  • Generator can choose to use full details or summary
  • Safe - no information loss

⚠️  DISADVANTAGES:
  • Longer context (more tokens)
  • Higher API costs for GPT models
  • May slow down generation slightly


════════════════════════════════════════════════════════════════════════════════
MODE 2: REPLACEMENT (concatenate_original=false)
════════════════════════════════════════════════════════════════════════════════

What the Generator Receives:
────────────────────────────

Document 1:
Paris is the capital city of France, serving as the political, economic, 
and cultural center of the nation.

────────────────────────────

Document 2:
Paris is the capital of France and has been a significant European city 
throughout history.

────────────────────────────

✅ ADVANTAGES:
  • Shorter, more focused context
  • Faster generation (fewer tokens)
  • Lower API costs
  • Removes redundant information

⚠️  DISADVANTAGES:
  • Original details are lost
  • Relies on rewriting quality
  • May lose important nuances


════════════════════════════════════════════════════════════════════════════════
COMBINED MODE EXAMPLE (process_separately=false)
════════════════════════════════════════════════════════════════════════════════

With Concatenation:
────────────────────

Document 1: Paris is the capital and most populous city of France...
Document 2: France is a country in Western Europe...

Refined version:
Paris is the capital of France, a Western European nation. As both the 
political and cultural center, Paris has been a major European settlement 
for over two millennia and is known for its historic landmarks.

────────────────────

Without Concatenation:
────────────────────

Document 1: Paris is the capital of France, a Western European nation. 
As both the political and cultural center, Paris has been a major European 
settlement for over two millennia and is known for its historic landmarks.


════════════════════════════════════════════════════════════════════════════════
COMPARISON TABLE
════════════════════════════════════════════════════════════════════════════════

┌─────────────────────┬───────────────────┬───────────────────┐
│ Metric              │ Concatenation     │ Replacement       │
├─────────────────────┼───────────────────┼───────────────────┤
│ Context Length      │ ~2x original      │ ~0.5x original    │
│ Information Loss    │ None              │ Possible          │
│ Generation Speed    │ Slower            │ Faster            │
│ API Token Cost      │ Higher            │ Lower             │
│ Answer Quality      │ More robust       │ Depends on LLM    │
│ Use Case            │ High-stakes QA    │ Long docs, costs  │
└─────────────────────┴───────────────────┴───────────────────┘


════════════════════════════════════════════════════════════════════════════════
CONFIGURATION EXAMPLES
════════════════════════════════════════════════════════════════════════════════

1. DEFAULT (Concatenation):
   ────────────────────────
   python bergen.py context_processor=llm_rewriter/rewriter_basic

2. REPLACE MODE:
   ─────────────
   python bergen.py context_processor=llm_rewriter/rewriter_replace_only

3. OVERRIDE ON COMMAND LINE:
   ─────────────────────────
   # Enable concatenation
   python bergen.py context_processor.init_args.concatenate_original=true
   
   # Disable concatenation
   python bergen.py context_processor.init_args.concatenate_original=false


════════════════════════════════════════════════════════════════════════════════
RECOMMENDATION
════════════════════════════════════════════════════════════════════════════════

START WITH: Concatenation (default) ✅
  - Safer approach
  - No information loss
  - Best for most use cases

SWITCH TO: Replacement if:
  - Context length becomes too long
  - API costs are a concern
  - Documents have extreme redundancy
  - Rewriter quality is very high


════════════════════════════════════════════════════════════════════════════════
""")

if __name__ == "__main__":
    show_examples()
    print("\nFor more details, see:")
    print("  - documentation/rewriter_concatenation.md")
    print("  - LLM_REWRITER_README.md")
