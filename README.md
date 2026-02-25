# LLM Semantic Syntax Evaluation

Evaluating how well large language models generate semantically correct programs that combine arithmetic logic with graphical rendering. We prompt LLMs to reconstruct simple board games in Python using pygame, then automatically test the generated code for syntax errors, semantic correctness, and game logic accuracy.

## Key Findings

- **Syntax correctness does not predict semantic correctness.** GPT-4o-mini and Claude 3 Sonnet achieved 99–100% syntax pass rates but semantic/logic accuracy ranged from 0% to 100% depending on game complexity.
- **Gemini 2.0 Flash struggled with pygame code generation,** passing syntax checks only ~8% of the time — primarily due to non-ASCII characters and malformed indentation in generated code blocks.
- **Game complexity affects pass rates non-uniformly.** Ball Bouncing (simple physics) hit 100% for GPT-4o-mini and Claude, while Tic-Tac-Toe hit 0% — largely due to models deviating from the expected `check_win(board, player)` function signature.

## Results

Aggregate pass rates across all five games:

| Model | N | Syntax | Semantic | Game Logic |
|-------|---|--------|----------|------------|
| GPT-4o-mini | 100 | 99.0% | 57.0% | 57.0% |
| Claude 3 Sonnet | 100 | 100.0% | 60.0% | 60.0% |
| Gemini 2.0 Flash | 500 | 8.4% | 7.4% | 5.4% |

Per-game breakdown:

| Game | Model | Syntax | Semantic | Game Logic |
|------|-------|--------|----------|------------|
| Tic-Tac-Toe | GPT-4o-mini | 100% | 0% | 0% |
| | Claude 3 Sonnet | 100% | 0% | 0% |
| | Gemini 2.0 Flash | 9% | 8% | 5% |
| Connect Four | GPT-4o-mini | 100% | 90% | 90% |
| | Claude 3 Sonnet | 100% | 60% | 60% |
| | Gemini 2.0 Flash | 8% | 7% | 6% |
| Snakes & Ladders | GPT-4o-mini | 100% | 55% | 55% |
| | Claude 3 Sonnet | 100% | 90% | 90% |
| | Gemini 2.0 Flash | 8% | 7% | 6% |
| Snake | GPT-4o-mini | 95% | 40% | 40% |
| | Claude 3 Sonnet | 100% | 50% | 50% |
| | Gemini 2.0 Flash | 9% | 7% | 5% |
| Ball Bouncing | GPT-4o-mini | 100% | 100% | 100% |
| | Claude 3 Sonnet | 100% | 100% | 100% |
| | Gemini 2.0 Flash | 8% | 8% | 5% |

## How It Works

The evaluation pipeline tests LLM-generated code in three stages:

1. **Syntax validation** — `ast.parse()` and `py_compile.compile()` catch parse-time errors before execution.
2. **Semantic checking** — Generated code is dynamically loaded as a module. Game-specific checkers verify required components exist and have correct interfaces (e.g., `check_win` for Tic-Tac-Toe, `Snake` class for Snake).
3. **Game logic testing** — AST transformations strip blocking game loops and `if __name__` blocks. Pygame is mocked for headless execution. Game functions are called with known inputs to verify correctness (e.g., testing win detection against a board state that should be a win).

## Games

| Game | Key Logic Tested |
|------|-----------------|
| Tic-Tac-Toe | Win detection (rows, columns, diagonals), turn alternation |
| Connect Four | Gravity-based piece dropping, 4-in-a-row detection |
| Snake | Continuous movement, self-collision, growth mechanics |
| Ball Bouncing | Velocity physics, wall collision and reflection |
| Snakes & Ladders | Board traversal, ladder/snake mapping, dice mechanics |

## Project Structure

```
llm-semantic-syntax/
├── games/                  # Reference game implementations
├── testing/                # Evaluation framework
│   ├── syntax_checker.py       # AST + compile validation
│   ├── semantic_checker.py     # Module loading + component checks
│   ├── game_logic_checker.py   # Headless logic testing with AST transforms
│   ├── runtime_checker.py      # Runtime error detection
│   └── evaluator.py            # Pipeline orchestration
├── prompts/                # LLM prompt templates
├── tests/                  # pytest suite for the framework itself
├── experiment_results_full_openai.json
├── experiment_results_full_anthropic.json
├── experiment_results_full_gemini.json
├── main.py                 # Test reference implementations
├── gather_results.py       # Run experiments against LLM APIs
└── consolidate_results.py  # Aggregate results into summary format
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Test reference implementations
```bash
python main.py
```

### Run experiments against LLM APIs
```bash
# Set API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# Gather results (20 repetitions per game per model)
python gather_results.py openai
python gather_results.py anthropic
python gather_results.py openai,anthropic

# Run with game logic testing (Gemini)
python run_with_game_logic.py
```

### Consolidate and view results
```bash
python consolidate_results.py
```

### Run framework tests
```bash
pytest tests/
```

## Experiment Parameters

| Parameter | Value |
|-----------|-------|
| Repetitions per game | 20 (OpenAI/Anthropic), 100 (Gemini) |
| Temperature | 0.75 |
| Models | GPT-4o-mini, Claude 3 Sonnet (2024-02-29), Gemini 2.0 Flash |

## Limitations

- **Rigid semantic checking**: The Tic-Tac-Toe 0% semantic rate for GPT-4o-mini and Claude was caused by requiring a specific `check_win(board, player)` signature. Many valid implementations used alternative names or signatures. More flexible function discovery would improve accuracy.
- **Single prompt per game**: Results may vary significantly with different prompting strategies or few-shot examples.
- **Model versions**: Results are specific to the model versions tested and may not generalize to newer releases.
- **Sample size imbalance**: Gemini was tested with 5x more samples than OpenAI/Anthropic, providing different confidence levels.

## Tech Stack

Python, pygame, numpy, AST manipulation, dynamic module loading (`importlib`), OpenAI API, Anthropic API, Google Generative AI API, pytest