# Contributing to `flux-cli`

First off, thank you for considering contributing to `flux-cli`! 🎉

This document outlines the guidelines and step-by-step instructions for setting up your development environment, creating issues, and submitting pull requests.

---

## 🚀 Getting Started

### Prerequisites
- **Python:** 3.10 or higher
- **Git**

### Local Development Setup

1. **Fork & Clone the Repository**
   ```bash
   git clone https://github.com/manmit-s/flux-cli.git
   cd flux-cli
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv

   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Package in Editable Mode**
   We use Python's standard `src/` layout. Install the package locally in editable mode:
   ```bash
   pip install -e .
   ```

4. **Verify Installation**
   Run the CLI locally:
   ```bash
   flux
   ```

## 📁 Repository Layout

All core Python source code resides inside `src/flux_cli/`:

```
src/flux_cli/
├── agent/       # Core agent execution engine
├── client/      # LLM provider clients & response handling
├── config/      # Configuration management & loaders
├── context/     # Context compaction & loop detection
├── hooks/       # Event hooks system
├── prompts/     # System prompts
├── safety/      # User approval & guardrails
├── tools/       # Built-in tools & MCP integration
├── ui/          # Rich TUI implementation
├── utils/       # Common helper functions and error handling
└── main.py      # Entry point executable
```

**Note on Imports:** All module imports within the project must be prefixed with `flux_cli.`.

*Example:* `from flux_cli.agent.agent import Agent`

---

## 🛠️ Making Changes & Submitting a PR

1. **Create a Feature Branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make Your Changes**
   - Keep changes focused and well-structured.
   - Follow standard Python PEP 8 formatting style.

3. **Test Your Changes**
   Verify that your code executes cleanly without breaking existing imports or CLI execution:
   ```bash
   python -m build
   ```

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat(module): brief description of changes"
   git push origin feat/your-feature-name
   ```

5. **Open a Pull Request**
   - Go to GitHub and open a Pull Request against the `main` branch.
   - Fill out the PR template completely.

---

## 🐛 Reporting Bugs & Suggesting Features

- Search existing Issues before submitting a new one.
- Use our [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) or [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) templates when opening an issue.

---

Thank you for helping make `flux-cli` better! 🚀