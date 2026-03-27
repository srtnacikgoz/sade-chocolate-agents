# Testing Framework & Patterns

## Test Framework

### Current Setup
- **Framework:** pytest (version 8.0+, configured in `pyproject.toml`)
- **Coverage Tool:** pytest-cov (version 4.0+)
- **Linter:** Ruff for code quality

Configuration in `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Test Directory Structure
```
tests/
├── __init__.py          # Empty init file
└── (test files here)
```

Currently minimal test infrastructure exists. The `tests/__init__.py` exists but contains only:
```python
# Empty init for test package
```

## Test Structure

### Recommended Test Organization
Follow this pattern based on codebase organization:

```
tests/
├── __init__.py
├── test_agents/
│   ├── __init__.py
│   ├── test_base.py              # Test SadeAgent base class
│   ├── test_alchemist.py         # Test AlchemistAgent
│   ├── test_growth_hacker.py     # Test GrowthHackerAgent
│   ├── test_pricing_analyst.py   # Test PricingAnalystAgent
│   └── test_narrator.py          # Test NarratorAgent
├── test_skills/
│   ├── __init__.py
│   ├── test_alchemist_skills.py
│   ├── test_growth_skills.py
│   ├── test_pricing_skills.py
│   └── test_narrator_skills.py
├── test_config/
│   ├── __init__.py
│   └── test_settings.py
└── conftest.py                    # Shared fixtures
```

### Test File Naming
- Use `test_` prefix: `test_base.py`, `test_alchemist.py`
- Match module names being tested: `test_alchemist_skills.py` tests `alchemist_skills.py`
- Group related tests in test classes: `TestSadeAgent`, `TestAlchemistAgent`

### Basic Test Structure
```python
# tests/test_agents/test_base.py
"""Tests for SadeAgent base class."""

import pytest
from sade_agents.agents.base import SadeAgent


class TestSadeAgent:
    """Test suite for SadeAgent class."""

    def test_initialization_default_values(self):
        """Test agent initializes with correct defaults."""
        agent = SadeAgent(role="Test Agent", goal="Test goal")

        assert agent.brand_voice == "sessiz_luks"
        assert agent.department == "operations"
        assert agent.autonomy_level == "mixed"

    def test_initialization_custom_values(self):
        """Test agent initializes with custom values."""
        agent = SadeAgent(
            role="Test Agent",
            goal="Test goal",
            brand_voice="custom_voice",
            department="finance",
            autonomy_level="autonomous",
        )

        assert agent.brand_voice == "custom_voice"
        assert agent.department == "finance"
        assert agent.autonomy_level == "autonomous"

    def test_log_action_formats_correctly(self, caplog):
        """Test log_action outputs correct format."""
        agent = SadeAgent(role="Test Role", goal="Test goal", department="product")
        agent.log_action("test_action", "details")

        assert "[PRODUCT]" in caplog.text
        assert "Test Role" in caplog.text
        assert "test_action" in caplog.text
```

### Test Class Organization
- Use test classes to group related tests: `class TestAlchemistAgent:`
- One logical feature or method per test class
- Use descriptive test method names: `test_initialization_with_custom_department`

## Mocking Patterns

### Mock CrewAI Components
CrewAI Agent and Tool objects may need mocking:

```python
# tests/conftest.py
"""Shared test fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from crewai.tools import Tool


@pytest.fixture
def mock_tool():
    """Create a mock CrewAI tool."""
    tool = Mock(spec=Tool)
    tool.name = "test_tool"
    tool.description = "Test tool description"
    return tool


@pytest.fixture
def mock_agent():
    """Create a mock CrewAI agent."""
    agent = Mock()
    agent.role = "Test Agent"
    agent.goal = "Test goal"
    agent.backstory = "Test backstory"
    agent.tools = []
    return agent
```

### Mock Environment Variables
For settings testing:

```python
# tests/test_config/test_settings.py
"""Tests for configuration settings."""

import pytest
from unittest.mock import patch
from sade_agents.config import Settings


class TestSettings:
    """Test suite for Settings class."""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123'})
    def test_loads_api_key_from_env(self):
        """Test settings loads API key from environment."""
        settings = Settings()
        assert settings.openai_api_key == 'test-key-123'

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123', 'OPENAI_MODEL_NAME': 'gpt-4'})
    def test_loads_custom_model_name(self):
        """Test settings loads custom model name."""
        settings = Settings()
        assert settings.openai_model_name == 'gpt-4'

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_validate_api_key_success(self):
        """Test API key validation succeeds with valid key."""
        settings = Settings()
        assert settings.validate_api_key() is True

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'your-api-key-here'})
    def test_validate_api_key_fails_with_placeholder(self):
        """Test API key validation fails with placeholder."""
        settings = Settings()
        assert settings.validate_api_key() is False
```

### Mock Skill Tools
For skill function testing:

```python
# tests/test_skills/test_alchemist_skills.py
"""Tests for Alchemist skills."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from sade_agents.skills.alchemist_skills import (
    lezzet_pisileri,
    _get_ay_adi,
    _format_eslestirmeler,
)


class TestAlchemistSkills:
    """Test suite for Alchemist agent skills."""

    def test_lezzet_pisileri_flavor_pairing_mode(self):
        """Test lezzet_pisileri returns flavor pairing data."""
        result = lezzet_pisileri("bitter_cikolata", "eslestir")

        assert "🧪 Lezzet Laboratuvarı Raporu" in result
        assert "Bitter Cikolata" in result
        assert "klasik" in result.lower() or "cesur" in result.lower()

    def test_lezzet_pisileri_seasonal_mode(self):
        """Test lezzet_pisileri returns seasonal ingredients."""
        result = lezzet_pisileri("", "mevsim")

        assert "📅 Mevsimsel Malzemeler" in result
        assert "Gelecek ay" in result

    def test_lezzet_pisileri_invalid_chocolate_type(self):
        """Test lezzet_pisileri with invalid chocolate type."""
        result = lezzet_pisileri("unknown_chocolate", "eslestir")

        assert "Bilinmeyen çikolata tipi" in result
        assert "Geçerli:" in result

    def test_lezzet_pisileri_invalid_mode(self):
        """Test lezzet_pisileri with invalid mode."""
        result = lezzet_pisileri("bitter_cikolata", "invalid_mode")

        assert "Bilinmeyen mod" in result
        assert "eslestir, mevsim, bilgi, tumu" in result

    @patch('sade_agents.skills.alchemist_skills.datetime')
    def test_get_ay_adi_returns_current_month(self, mock_datetime):
        """Test _get_ay_adi returns current month name."""
        # Mock January
        mock_datetime.now.return_value.month = 1
        assert _get_ay_adi() == "ocak"

        # Mock July
        mock_datetime.now.return_value.month = 7
        assert _get_ay_adi() == "temmuz"

    def test_format_eslestirmeler_structure(self):
        """Test _format_eslestirmeler returns markdown table."""
        result = _format_eslestirmeler("bitter_cikolata")

        assert "| Kategori | Malzemeler |" in result
        assert "|----------|------------|" in result
        assert "Klasik" in result or "klasik" in result.lower()
```

## Coverage Configuration

### Coverage Setup
Add to `pyproject.toml` for coverage configuration:

```toml
[tool.coverage.run]
source = ["src/sade_agents"]
omit = [
    "*/site-packages/*",
    "*/distutils/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*Protocol.*:",
    "@abstractmethod",
]
precision = 2
```

### Running Coverage
```bash
# Run tests with coverage report
pytest --cov=sade_agents --cov-report=html tests/

# Generate HTML report in htmlcov/
# View with: open htmlcov/index.html
```

### Coverage Goals
- Aim for 80%+ coverage on core logic (agents, skills, config)
- Script files (`scripts/`) can have lower coverage (they're entry points)
- Use `pragma: no cover` for untestable lines (setup code, emergency exits)

## How to Write New Tests

### Step 1: Create Test File
Create file in appropriate subdirectory matching the module structure:
- Agent tests: `tests/test_agents/test_<agent_name>.py`
- Skill tests: `tests/test_skills/test_<skill_name>.py`
- Config tests: `tests/test_config/test_<module_name>.py`

### Step 2: Import Required Modules
```python
"""Tests for <module_name>."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sade_agents.<module_path> import ClassName, function_name
```

### Step 3: Create Test Class
Group related tests in a class:
```python
class TestClassName:
    """Test suite for ClassName."""

    # Tests go here
```

### Step 4: Write Test Methods
Follow pattern: `test_<what_is_being_tested>_<expected_outcome>`

```python
def test_initialization_with_valid_parameters(self):
    """Test initialization succeeds with valid parameters."""
    # Arrange
    param1 = "value1"
    param2 = "value2"

    # Act
    result = FunctionOrClass(param1, param2)

    # Assert
    assert result.property == expected_value
    assert result.method() == expected_output

def test_invalid_input_raises_error(self):
    """Test invalid input raises appropriate error."""
    # Arrange
    invalid_input = "bad_value"

    # Act & Assert
    with pytest.raises(ValueError):
        Function(invalid_input)
```

### Step 5: Test Agents
For agent testing, focus on initialization and configuration:

```python
# tests/test_agents/test_alchemist.py
"""Tests for AlchemistAgent."""

import pytest
from sade_agents.agents.alchemist import AlchemistAgent


class TestAlchemistAgent:
    """Test suite for AlchemistAgent."""

    def test_initialization(self):
        """Test AlchemistAgent initializes with correct attributes."""
        agent = AlchemistAgent()

        assert agent.role == "The Alchemist - Flavor Architect"
        assert agent.department == "product"
        assert agent.autonomy_level == "autonomous"
        assert agent.tools is not None
        assert len(agent.tools) > 0

    def test_inherits_from_sade_agent(self):
        """Test AlchemistAgent inherits from SadeAgent."""
        from sade_agents.agents.base import SadeAgent

        agent = AlchemistAgent()
        assert isinstance(agent, SadeAgent)
        assert hasattr(agent, 'log_action')
        assert hasattr(agent, 'brand_voice')
```

### Step 6: Test Skills
For skill testing, test the tool functions with various inputs:

```python
# tests/test_skills/test_growth_skills.py
"""Tests for Growth Hacker skills."""

import pytest
from sade_agents.skills.growth_skills import sosyal_nabiz


class TestSocialPulse:
    """Test suite for sosyal_nabiz skill."""

    def test_all_platforms_returns_complete_report(self):
        """Test requesting all platforms returns complete analysis."""
        result = sosyal_nabiz("tumu")

        assert "📡 Sosyal Nabız Raporu" in result
        assert "X (Twitter)" in result
        assert "Instagram" in result
        assert "Reddit" in result
        assert "Pazar Sinyalleri" in result
        assert "📊 Özet İstatistikler" in result

    def test_single_platform_returns_filtered_data(self):
        """Test requesting single platform returns only that data."""
        result = sosyal_nabiz("x_twitter")

        assert "X (Twitter)" in result
        assert "Instagram" not in result

    def test_invalid_platform_returns_error(self):
        """Test invalid platform returns helpful error message."""
        result = sosyal_nabiz("invalid_platform")

        assert "Bilinmeyen platform" in result
        assert "x_twitter, instagram, reddit, pazar, tumu" in result
```

### Step 7: Run Tests
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_agents/test_alchemist.py

# Run specific test class
pytest tests/test_agents/test_alchemist.py::TestAlchemistAgent

# Run specific test
pytest tests/test_agents/test_alchemist.py::TestAlchemistAgent::test_initialization

# Run with coverage
pytest --cov=sade_agents tests/
```

### Step 8: Use Pytest Features

#### Parametrized Tests (test multiple values)
```python
@pytest.mark.parametrize("chocolate_type,expected_in_result", [
    ("bitter_cikolata", "Bitter Cikolata"),
    ("sutlu_cikolata", "Sütlü Cikolata"),
    ("beyaz_cikolata", "Beyaz Cikolata"),
])
def test_format_supports_all_chocolate_types(self, chocolate_type, expected_in_result):
    """Test flavor formatting works for all chocolate types."""
    result = _format_eslestirmeler(chocolate_type)
    assert expected_in_result in result
```

#### Fixtures for Setup/Teardown
```python
@pytest.fixture
def alchemist_agent(self):
    """Create AlchemistAgent for testing."""
    agent = AlchemistAgent()
    yield agent
    # Cleanup if needed

def test_with_fixture(self, alchemist_agent):
    """Test using the fixture."""
    assert alchemist_agent.role == "The Alchemist - Flavor Architect"
```

#### Marking Tests
```python
@pytest.mark.slow
def test_expensive_operation():
    """Run with: pytest -m slow"""
    pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.xfail(reason="Known issue")
def test_broken_feature():
    pass
```

### Testing Checklist
- [ ] Module imports correctly
- [ ] Class initializes with defaults
- [ ] Class initializes with custom values
- [ ] Methods return expected types
- [ ] Error cases return helpful messages
- [ ] Edge cases are handled (empty inputs, None, etc.)
- [ ] Turkish language content is preserved
- [ ] All dependencies are mocked appropriately
- [ ] Test runs independently without side effects
- [ ] Test name clearly describes what is tested

## Integration Testing

### Script Testing
Test script entry points without actual API calls:

```python
# tests/test_scripts/test_run_alchemist.py
"""Tests for run_alchemist.py script."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path


class TestRunAlchemistScript:
    """Test suite for Alchemist runner script."""

    @patch('sade_agents.agents.alchemist.AlchemistAgent')
    def test_dry_run_imports_successfully(self, mock_agent):
        """Test dry-run mode validates imports."""
        # Would test the dry_run() function
        pass

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('sade_agents.agents.alchemist.AlchemistAgent')
    def test_run_creates_agent_with_correct_config(self, mock_agent):
        """Test agent is created with correct configuration."""
        pass
```

### Crew Testing
Test task and crew execution:

```python
# tests/test_integration/test_alchemist_crew.py
"""Integration tests for Alchemist crew."""

import pytest
from unittest.mock import MagicMock, patch


class TestAlchemistCrew:
    """Test suite for Alchemist crew execution."""

    @patch('crewai.Crew.kickoff')
    def test_crew_kickoff_returns_result(self, mock_kickoff):
        """Test crew execution returns result."""
        mock_kickoff.return_value = "Test output"
        # Test crew execution
        pass
```

## CI/CD Integration

### GitHub Actions Example
Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests with coverage
      run: |
        pytest --cov=sade_agents --cov-report=xml tests/
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Useful Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=sade_agents --cov-report=html tests/

# Run only specific test
pytest tests/test_agents/test_alchemist.py -v

# Run tests matching pattern
pytest -k "initialization" tests/

# Run tests marked as slow
pytest -m slow tests/

# Run with detailed output
pytest -vv tests/

# Stop on first failure
pytest -x tests/

# Show local variables in tracebacks
pytest -l tests/

# Drop into debugger on failure
pytest --pdb tests/

# Generate JUnit XML report
pytest --junit-xml=report.xml tests/
```
