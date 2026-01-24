# Directives

This directory contains Standard Operating Procedures (SOPs) for the AI agent (Antigravity). These directives define *what* to do, separating the goal from the deterministic *how* (stored in `execution/`).

## Architecture Overview

1.  **Directive (Layer 1)**: This folder. Markdown files defining goals and logic.
2.  **Orchestration (Layer 2)**: The AI reasoning and tool calling.
3.  **Execution (Layer 3)**: Python scripts in `../execution/` that perform deterministic work.

## Guidelines for New Directives

- Use clear, actionable headings.
- Specify inputs and expected outputs.
- List which execution scripts should be used.
- Include error handling and edge cases.
- Update directives with learnings as the system evolves (self-annealing).
