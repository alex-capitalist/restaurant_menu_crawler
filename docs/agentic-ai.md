## Future Work: Agentic AI

While the current prototype uses deterministic heuristics with Playwright, a natural extension is to introduce **agentic AI** to make the system more adaptive and scalable across arbitrary restaurant websites.  

### Why Agentic AI?
- **Reduce heuristics maintenance**: Instead of hardcoding rules for detecting menus, an LLM agent can interpret new layouts and terminology.
- **Handle ambiguity**: Agents can reason about edge cases (e.g., "Offers" vs. "Menu") and ask clarifying questions internally before deciding.
- **Scalability**: New sites can be added with little or no extra engineering effort.

### How It Could Work
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

### Trade-offs
- **Complexity**: Requires additional dependencies and orchestration code.  
- **Cost**: Commercial LLM calls (e.g., GPT-4.1) introduce per-request costs.  
- **Stability**: Agents can behave unpredictably without careful guardrails.  

### Conclusion
For this prototype, heuristics are sufficient to demonstrate viability. However, an **agentic AI layer** would unlock the ability to parse a far larger and more diverse set of restaurant websites with less manual engineering effort.
