# Working With Coding Agents

This project template is meant to help students practice software development
decisions, not only generate code. When using an agent, expect it to ask
clarifying questions before implementing larger features or accepting technology
choices.

Good prompts include both the desired result and the decisions already made:

```text
Implement an order overview page for administrators. It should show a paginated
table with order number, customer, status, total price, and creation date.
Filtering by status is enough for the first version. Authorization must be
checked in the backend.
```

If these decisions are not yet clear, ask the agent to help you decide:

```text
We need an order overview page, but we are not sure yet who should see it, which
filters are useful, and whether filtering should happen in the backend or
frontend. Please challenge our assumptions before implementing it.
```

Important decisions should be documented in `docs/decisions` using the
continuous numbering scheme, for example `0001-framework-choice.md` followed by
`0002-order-overview-scope.md`.
