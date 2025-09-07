## Current AI Implementation & Future Agentic AI

The current prototype uses a **hybrid approach** combining deterministic heuristics with AI-powered classification. The system already leverages LLMs for menu classification and noise filtering, while using heuristics for link extraction and crawling orchestration.

### Current AI Usage
The system currently uses AI in two key areas:

1. **Noise Classification** (`NoiseClassifier`): Filters out non-menu links using a lightweight LLM prompt to reduce false positives during crawling. *Note: This is a conscious overkill decision for rapid prototyping - in production, this should use a small, ultra-fast ML model instead of an LLM.*

2. **Menu Classification** (`MenuClassifier`): Analyzes page content to determine if it contains a menu, classify the menu type, format, and languages using structured prompts.

### Current Pipeline Steps
The concrete steps for crawling, loading, analyzing, and parsing are well-defined in the codebase:

1. **Crawl**: Playwright-based site crawling with configurable depth (default: 3 levels)
2. **Load**: Extract links using heuristics (DOM parsing, onclick handlers, data attributes)
3. **Analyze**: AI-powered noise filtering and menu classification
4. **Parse**: Content extraction and structured data generation

### Future: Full Agentic AI Orchestration
While link extraction currently uses heuristics, this could be replaced with an **agentic AI** approach to make the system more adaptive and scalable across arbitrary restaurant websites.

### Why Full Agentic AI?
- **Reduce heuristics maintenance**: Instead of hardcoding rules for detecting menus, an LLM agent can interpret new layouts and terminology.
- **Handle ambiguity**: Agents can reason about edge cases (e.g., "Offers" vs. "Menu") and ask clarifying questions internally before deciding.
- **Scalability**: New sites can be added with little or no extra engineering effort.
- **Orchestration**: The agent could dynamically plan and execute the crawl → load → analyze → parse pipeline based on site-specific requirements.

### How Full Agentic AI Could Work
1. **LLM Orchestration Framework**  
   - Use LangChain, LlamaIndex, or Semantic Kernel to provide the agent with memory, planning, and tool usage.
   
2. **Define Tools**  
   - **Browser Tool**: Playwright integration for navigation, clicking, and extracting HTML.  
   - **PDF Tool**: PyMuPDF wrapper for text extraction from menus.  
   - **Language Tool**: Existing `langdetect` or a multilingual embedding model for more robust detection.  
   - **Logging Tool**: For tracking reasoning steps and avoiding infinite loops.

3. **Execution Loop**  
   - The agent receives the task: *"Find all menus on this restaurant site and classify them."*  
   - It plans steps, chooses tools, executes them, and iterates until menus are found or a stop condition is reached.

4. **Guardrails & Cost Control**  
   - Limit maximum tool calls per restaurant to avoid runaway loops.  
   - Use a lightweight OSS model (e.g., LLaMA 3, Mistral 7B) for reasoning in dev mode, with GPT-4/4.1 reserved for production-grade accuracy.

### Production-Ready ML Alternatives
For production deployment, the current LLM-based noise classification should be replaced with lightweight ML models:

**Recommended Architectures:**
- **Random Forest**: Fast, interpretable, works well with text features (TF-IDF, n-grams)
- **LightGBM/XGBoost**: Gradient boosting with excellent performance on tabular/text data
- **DistilBERT**: Compressed transformer model for text classification (much faster than full BERT)
- **FastText**: Facebook's text classification library optimized for speed
- **Scikit-learn Linear Models**: Logistic regression or SVM with text vectorization

**Implementation Approach:**
1. Extract features from link text and URLs (TF-IDF, character n-grams, domain patterns)
2. Train on labeled dataset of menu vs. non-menu links
3. Deploy as lightweight model (few MB) with sub-millisecond inference
4. Fallback to LLM only for edge cases or when confidence is low

### Trade-offs
- **Complexity**: Requires additional dependencies and orchestration code.  
- **Cost**: Commercial LLM calls (e.g., GPT-4.1) introduce per-request costs.  
- **Time**: AI orchestration adds latency compared to deterministic heuristics.
- **Stability**: Agents can behave unpredictably without careful guardrails.  

### Conclusion
The current hybrid approach demonstrates viability with AI-powered classification and heuristic-based orchestration. However, a **full agentic AI layer** would unlock the ability to parse a far larger and more diverse set of restaurant websites with less manual engineering effort. The trade-offs of cost and time must be carefully optimized for scale deployment.
