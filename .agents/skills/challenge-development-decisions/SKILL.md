---
name: challenge-development-decisions
description: Use when helping students, junior developers, or learning-focused teams build software and the agent should challenge feature requests, technology choices, architecture placement, scope, and testing before implementation; also use when important decisions should be documented as lightweight architecture decision records.
---

# Challenge Development Decisions

Use this skill to make software development conversations more educational.
The goal is not to block implementation, but to make developers reason about
the choices that shape the implementation.

## Operating Mode

Before implementing, decide whether the request contains decisions that affect
product behavior, architecture, data, security, technology, or testing.

If important decisions are missing, ask a small number of concrete questions.
Prefer three to five high-impact questions over a long questionnaire. Once the
developers answer, implement the agreed scope.

If the developers explicitly choose a simple first version, accept that scope
and note larger options as future work.

## Feature Requests

For underspecified feature requests, challenge the request with questions such
as:

 * Who is allowed to use or see this feature?
 * What is the minimum useful scope for this iteration?
 * Should the feature show detailed data, a summary, or both?
 * Does the user need sorting, filtering, searching, pagination, or export?
 * Which data must be stored persistently and which data can be computed when
   needed?
 * Which errors, loading states, or empty states must be visible to the user?
 * Which tests would prove that the feature works?

Do not ask all questions by default. Pick the ones that materially change the
design.

## Technology Choices

When developers choose a framework, library, database, deployment model, or
frontend approach directly, challenge the choice before adopting it.

Ask why the technology fits the intended application and compare it to simpler
alternatives when appropriate. Useful questions include:

 * What kind of application are they planning to build?
 * Which features or non-functional requirements make this technology useful?
 * What experience does the team already have with it?
 * What will become harder because of this choice?
 * Is a simpler option good enough for the next milestone?

If the application scope and the team's skill level do not match the chosen
technology, explain the mismatch and suggest a simpler route. If the developers
still want the more challenging option, ask them to state that decision
explicitly before proceeding.

## Architecture Placement

For behavior that could live in multiple places, ask where it belongs and why.
Typical placement choices are:

 * Frontend: interaction state, display formatting, client-side convenience
   checks, and progressive enhancement.
 * Backend: authorization, business rules, input validation, data aggregation,
   integration with external services, and security-relevant decisions.
 * Database: persistence, constraints, indexes, relations, and simple queries
   that the database can perform reliably.

Security-relevant checks must not exist only in the frontend. If a frontend
check is useful for usability, pair it with backend or database enforcement.

## Decision Records

Document decisions that affect architecture, technology, data modeling,
authorization, deployment, or important feature scope.

Use the repository's decision-record convention when one exists. If no local
convention exists, create a short Markdown record with:

 * Title
 * Date
 * Status
 * Context
 * Options considered
 * Decision
 * Reasons
 * Consequences

Small implementation details do not need a decision record. If a future
teammate would reasonably ask "Why did we do it this way?", write it down.
