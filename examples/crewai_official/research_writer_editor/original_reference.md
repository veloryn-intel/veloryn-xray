# Original Reference

This example is inspired by the recognizable Researcher -> Writer -> Editor content-creation crew pattern used throughout CrewAI documentation and community examples.

Source inspiration:

- CrewAI documentation for `Agent`, `Task`, `Crew`, and sequential process workflows
- official/community CrewAI examples that use a researcher/writer/editor collaboration shape for content production

What was adapted:

- the topic was narrowed to a technical explainer about queue-based retry strategies for flaky API calls
- the workflow was reduced to one sequential research, drafting, and editing pass so the execution trajectory is easy to inspect
- outputs are captured into a deterministic X-Ray replay fixture

What remained unchanged:

- real CrewAI primitives are used
- the workflow remains sequential and multi-agent
- the provider path remains a real OpenAI-backed CrewAI execution

Why this workflow matters for execution analysis:

- it is a familiar multi-agent pattern in the CrewAI ecosystem
- it produces distinct stages with different structural roles
- it shows how X-Ray can analyze contribution across agent handoffs without evaluating semantic correctness
