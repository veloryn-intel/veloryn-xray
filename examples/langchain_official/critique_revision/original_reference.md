# Original Reference

Official inspiration:

- LangChain `ConstitutionalChain` documentation:
  - [ConstitutionalChain](https://api.python.langchain.com/en/latest/langchain/chains/langchain.chains.constitutional_ai.base.ConstitutionalChain.html)

What was adapted:

- The official critique and revision prompt structure was kept.
- The full chain wrapper was unfolded into explicit LangChain runnable steps so each critique and revision becomes visible to X-Ray.
- The task was changed to operational guidance for API key rotation.

What remained unchanged in spirit:

- draft generation
- critique pass
- revision pass
- repeated self-improvement loop around one response

Why this workflow is relevant to execution analysis:

- critique and revise loops are common LangChain patterns
- they can improve structure or simply add repetition
- X-Ray helps show when repeated self-critique stops producing meaningful structural change
