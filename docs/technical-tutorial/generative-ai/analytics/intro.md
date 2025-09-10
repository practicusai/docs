---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: practicus
---

# Agentic Analytics

Welcome to the documentation for **Practicus AI's Agentic Analytics** feature. This capability enables a "talk to your data" experience, where users can interact with their data ecosystems using natural language, all while maintaining robust security and governance.

This documentation is divided into two main sections, each corresponding to a detailed page:

1.  **The Agentic Policy Engine**: The foundation of our secure data access layer.
2.  **The Agentic Query Engine**: The functions an LLM agent uses to query data and create visualizations.


## 1. Dynamic Data Governance with the Policy Engine

Before we can allow an AI agent to freely query data, we must establish a robust governance framework. Hardcoded rules are brittle and unscalable. Instead, our approach leverages metadata systems (we will use Open Metadata for this document) as a single source of truth for data governance policies.

Our Policy Engine, (we will use Trino for this document), acts as a dynamic, centralized gatekeeper for all queries. When a query is initiated, Trino makes real-time calls to a set of APIs that determine whether the action should be permitted. These decisions are based on the user's identity and the metadata of the requested data assets (e.g., tags, ownership, and sensitivity).

As you can see in the detailed **Policy Engine** page, we implement three critical API endpoints:

- `**/validate`**: Decides if a user can perform an action (e.g., `SELECT`) on specific tables and columns.
- `**/filter-rows`**: Dynamically injects `WHERE` clauses to implement row-level security, ensuring users only see the data they are entitled to.
- `**/mask-columns`**: Applies column-level masking (e.g., redaction, obfuscation) to sensitive data on the fly.

This metadata-driven approach ensures that as your governance policies evolve in Open Metadata, your data access enforcement updates automatically without any code changes.


## 2. Empowering LLMs with Agentic Analytics Tools

With a strong governance foundation in place, we can now empower the LLM agent with tools to perform meaningful work. These tools are simple, well-documented APIs that the agent can call to fulfill a user's request.

Imagine a user asking, *"What were our top 5 most popular products in North America this year?"* The LLM client (such as Practicus AI Assistant) orchestrates a workflow using the APIs we provide:

1.  First, it might use an internal tool to search Open Metadata for relevant tables like `products` and `sales`.
2.  Next, it generates a Trino SQL query to answer the question.
3.  It then calls the `**/run-sql` tool to execute the query. Crucially, this execution is subject to all the rules defined in our Policy Engine.
4.  Finally, after providing the answer, the agent might offer to create a visualization by calling the `**/create-analytics-dataset` tool, which generates a link to a pre-built chart in an analytics engine, such as Practicus AI Apache Superset Add-on.

The **Agentic Analytics Tools** page provides a deep dive into the implementation of these functions, showing how the Practicus AI SDK helpers simplify everything from safe SQL execution to interacting with the Superset API.


## Putting It All Together: A Secure, Intelligent System

The true power of Agentic Analytics lies in the seamless integration of these two components. The **Agentic Query Engine** provide the capabilities for the LLM to act, while the **Agentic Policy Engine** provides the guardrails to ensure it acts safely and appropriately. The user, or the agent acting on their behalf, never needs to be aware of the underlying policies; they are enforced transparently on every single query.

This creates a powerful, scalable, and secure framework for building the next generation of data applications.

**Please proceed to the detailed pages to explore the code and implementation of each component.**


---

**Previous**: [Build](../mcp/build.md) | **Next**: [Policy Engine > Build](policy-engine/build.md)
