# AI Healer Framework

An intelligent self-healing automation testing framework that uses AI and rule-based engines to automatically recover from locator failures in Playwright tests.

## Overview

The AI Healer Framework provides a sophisticated solution for handling test failures caused by changed DOM selectors. When a Playwright locator fails to find an element, the framework automatically:

1. **Captures** the failure context and page snapshot
2. **Analyzes** the DOM using LLM-powered techniques to find alternative locators
3. **Evaluates** candidates against rule-based policies
4. **Validates** locator uniqueness and quality metrics
5. **Heals** the test by automatically recovering with a new locator

This approach significantly reduces test maintenance overhead and improves test reliability in dynamic UI environments.

## Architecture

The framework is organized into modular components:

### Core Components

- **`adapter/selfheal/`** - Self-healing adapter for Playwright integration
  - `self_healer.py` - Main healing orchestrator implementing the healing strategy
  - `page_proxy.py` - Proxy wrapper around Playwright's Page class to intercept locator failures
  - `healer_interface.py` - Interface defining the healing contract
  - `orchestrator.py` - Central orchestration engine that coordinates all healing steps
  - `reporter.py` - Failure normalization and context extraction
  - `score_engine.py` - Locator ranking and scoring algorithm
  - `validator.py` - Locator validation and uniqueness checking
  - `locator_proxy.py` - Proxy for Playwright locators to enable self-healing
  - `locator_transformer.py` - Converts between locator formats
  - `snapshot_helper.py` - Captures and manages page snapshots
  - `models.py` - Data models for locators and validation results
  - `retry.py` - Retry logic and locator building utilities
  - `roles.py` - Role-based locator identification

- **`analyzer/`** - AI-powered analysis engine
  - `llm_analyzer.py` - LLM integration using Ollama/LangChain for intelligent locator discovery
  - `confidence.py` - Confidence scoring and analysis
  - Sanitizes LLM-generated JSON responses for reliable parsing

- **`rule_engine/`** - Policy-based decision engine
  - `execution_engine.py` - Evaluates failure contexts against defined rules
  - `rule_loader.py` - Loads healing policies from YAML configuration
  - `rules.yaml` - Declarative rules defining which failures can be auto-healed
  - `models.py` - Rule and context data structures
  - `match.py` - Rule matching logic

### Test Integration

- **`tests/`** - Test suite demonstrating framework usage
  - `playwright/test_login.py` - Example Playwright tests with healing enabled
- **`conftest.py`** - Pytest configuration and fixtures providing healing-enabled page objects

## Features

✨ **Intelligent Locator Recovery** - Uses LLM to analyze DOM and generate alternative locators  
📋 **Rule-Based Policy Engine** - Declarative YAML rules control which failures to heal  
🎯 **Confidence Scoring** - Ranks candidate locators by reliability and uniqueness  
🔄 **Automatic Validation** - Ensures healed locators uniquely identify target elements  
📸 **Snapshot Capture** - Preserves DOM and accessibility information for analysis  
🔌 **Playwright Native** - Drop-in replacement for Playwright's page object  

## Installation

```bash
# Install from source
pip install -e .

# Or with pip directly
pip install ai-healer-framework
```

### Dependencies

- **Python** ≥ 3.13
- **Playwright** ≥ 1.57.0 - Browser automation framework
- **LangChain** ≥ 1.2.0 - LLM orchestration framework
- **LangChain Ollama** ≥ 1.0.1 - Local LLM integration
- **Pydantic** ≥ 2.12.5 - Data validation
- **FastAPI** ≥ 0.125.0 - REST framework
- **PyYAML** ≥ 6.0.3 - Configuration parsing

## Usage

### Basic Setup

1. **Initialize Playwright and healing support:**

```python
from playwright.sync_api import sync_playwright
from adapter.selfheal.page_proxy import HealingPage
from adapter.selfheal.self_healer import SimpleSelfHealer

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Wrap page with healing capability
    healer = SimpleSelfHealer()
    healing_page = HealingPage(page, healer)
    
    # Use healing_page exactly like a normal Playwright page
    healing_page.goto("https://example.com")
    healing_page.locator("input#email").fill("user@example.com")
```

### Using with Pytest

The framework includes pytest fixtures for seamless integration:

```python
# In your test file
def test_login(healer):
    """Test using the healing-enabled page fixture"""
    healer.goto("https://example.com/login")
    healer.get_by_label("Email").fill("user@example.com")
    healer.get_by_label("Password").fill("password")
    healer.get_by_role("button", name="Login").click()
    assert healer.url == "https://example.com/dashboard"
```

The `healer` fixture provides a `HealingPage` instance with an active `SimpleSelfHealer`.

### Configuring Healing Policies

Edit `rule_engine/rules.yaml` to define which failures should be healed:

```yaml
policies:
  - id: locator_healing_policy
    rules:
      - id: ALLOW_LOCATOR_NOT_FOUND
        priority: 10
        when:
          tool: playwright
        match:
          failure_type: LOCATOR_NOT_FOUND
        action:
          type: ALLOW
        confidence:
          score: 1.0
        explain: >
          Locator-not-found errors are safe to heal.
      
      - id: DENY_PAGE_LOAD_TIMEOUT
        priority: 10
        match:
          failure_type: PAGE_LOAD_TIMEOUT
        action:
          type: DENY
        confidence:
          score: 1.0
        explain: >
          Page load timeouts indicate infrastructure issues
          and must not be auto-healed.
```

## How It Works

### Healing Flow

```
Test Failure (Locator Not Found)
    ↓
Capture Failure Context & Page Snapshot
    ↓
Rule Engine Decision (Is this failure healable?)
    ↓ (If ALLOW)
LLM Analysis (Find alternative locators)
    ↓
Candidate Locator Ranking
    ↓
Locator Uniqueness Validation
    ↓
Return Healed Locator & Retry
    ↓
Test Continues
```

### Key Workflow Steps

1. **Failure Detection**: `HealingLocatorProxy` intercepts locator failures
2. **Context Normalization**: `normalize_failure()` extracts failure details
3. **Rule Evaluation**: `ExecutionEngine` checks if healing is permitted
4. **LLM Analysis**: `analyze_with_llm()` generates candidate locators
5. **Scoring**: `rank_locators()` evaluates candidates by reliability
6. **Validation**: `validate_locator_uniqueness()` ensures selector accuracy
7. **Recovery**: `build_locator()` constructs and returns the healed locator

## Configuration

### Environment Variables

- `OLLAMA_MODEL` - LLM model to use (default: `llama3.1:8b`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### Logging

Configure logging via `logging_config.py`:

```python
from logging_config import setup_logging
setup_logging(level=logging.DEBUG)
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run specific tests:

```bash
pytest tests/playwright/test_login.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Commit: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature/your-feature`
6. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on the repository.

## Roadmap

- [ ] Support for XPath and CSS selector analysis
- [ ] Web driver integration (Selenium, etc.)
- [ ] Enhanced LLM model support
- [ ] Visual locator matching using image analysis
- [ ] Healing metrics and analytics dashboard
- [ ] Failure prediction and proactive locator updates
