# NeurIPS Google Code Golf Championship 2025 - Self-Verifying Generation Pipeline

An automated pipeline with **iterative refinement** for generating and validating code solutions for the NeurIPS 2025 Google Code Golf Championship using LLM (Groq).

## Overview

### Team Members:

- [Muhammad Faheem](faheemgurkani@gmail.com)
- Hunain Maqbool

### Ranking: (Unranked)

(**Note:** Unfortunately, we could not complete the implementations for all 400 programs in time and hence remained unranked. We truly regret this missed oppourtunity.)

This pipeline automates the entire process of:

1. Loading task data (train/test examples from JSON files)
2. Generating Python solutions using LLM (Groq API with reasoning models)
3. **Iterative refinement**: Learning from previous failed attempts
4. Validating code syntax and correctness
5. Saving only verified solutions

## Features

- **Iterative Refinement**: Model learns from previous failed attempts
- **Reasoning Model Support**: Uses reasoning models for complex pattern discovery
- **Automated Validation**: Every generated solution is automatically tested
- **Syntax Checking**: Catches invalid Python code before validation
- **Functional Testing**: Tests solutions on training examples using `code_golf_utils`
- **Failed Attempt Tracking**: Saves failed code for debugging and analysis
- **Progress Tracking**: CSV logs with detailed statistics
- **Smart Retry Logic**: Passes previous errors to model for targeted fixes
- **Rate Limiting**: Built-in delays to respect API limits
- **Modular Design**: Easy to extend and customize

## Directory Structure

```
neurips-google-code-golf-championship-2025/
├── pipeline/
│   ├── modules/              # Core pipeline modules
│   │   ├── task_manager.py   # Manages task file loading
│   │   ├── task_parser.py    # Parses JSON task data
│   │   ├── prompt_builder.py # Builds LLM prompts (with iterative refinement)
│   │   ├── llm_generator.py  # Groq API integration
│   │   ├── output_parser.py  # Extracts code from LLM output
│   │   ├── code_validator.py # Validates syntax & correctness
│   │   ├── file_writer.py    # Saves validated solutions
│   │   └── progress_tracker.py # Logs progress to CSV
│   ├── tests/                # Test suite
│   │   └── test_pipeline.py  # Component tests
│   ├── output/               # Generated solutions (.py files)
│   │   └── failed/           # Failed attempts for debugging
│   └── logs/                 # Progress logs (CSV)
├── data/
│   └── google-code-golf-2025/ # Task data files (task001.json - task400.json)
├── run_pipeline.py           # Main orchestrator (with iterative refinement)
├── setup.sh                  # Setup script
├── requirements.txt          # Dependencies
├── .env.template             # Environment template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup Environment

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your Groq API key
# Get one from: https://console.groq.com/
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Step 3: Create Output Directories

```bash
# Run setup script
bash setup.sh
```

Or manually:

```bash
mkdir -p pipeline/output pipeline/output/failed pipeline/logs
```

### Step 4: Test the Pipeline

```bash
python pipeline/tests/test_pipeline.py
```

Expected output:

```
All modules imported successfully
TaskManager found 5 task files
TaskParser loaded task with examples
PromptBuilder created prompt
CodeValidator working correctly
OutputParser extracted code
```

See [Running Tests](#-running-tests) section for more testing options.

### Step 5: Run on a Single Task (Testing)

```bash
# Test on task 1 only (recommended first run)
python run_pipeline.py --start 1 --end 1 --max-calls 5
```

This will:

- Generate solutions for task 1
- Automatically retry up to 3 times with **iterative refinement**
- Each retry learns from the previous failed attempt
- Validate each solution
- Save validated solution to `pipeline/output/`
- Save failed attempts to `pipeline/output/failed/` for debugging
- Log progress to `pipeline/logs/progress.csv`

### Step 6: Run on a Small Subset

```bash
# Process tasks 1-10
python run_pipeline.py --start 1 --end 10 --max-calls 50
```

### Step 7: Process All Tasks

```bash
# Process all tasks 1-400 (adjust max-calls based on your API limit)
python run_pipeline.py --start 1 --end 400 --max-calls 1200
```

## Output

### Generated Solutions

Each validated solution is saved as:

```
pipeline/output/task001.py
pipeline/output/task002.py
...
```

### Failed Attempts (for Debugging)

Failed attempts are saved for analysis in `pipeline/output/failed/`:

```
pipeline/output/failed/task001_attempt1.py
pipeline/output/failed/task001_attempt2.py
...
```

**Debugging Commands:**

```bash
# See all attempts for a task
ls -lh pipeline/output/failed/task001_*

# Compare attempts to see how the model evolved
diff pipeline/output/failed/task001_attempt1.py pipeline/output/failed/task001_attempt2.py

# Count how many tasks failed all attempts
ls pipeline/output/failed/*attempt3.py | wc -l
```

### Progress Logs

CSV logs are saved to `pipeline/logs/progress.csv` with columns:

- `timestamp`: When the event occurred
- `task_id`: Task identifier
- `status`: Status (validated_success, syntax_error, failed_validation, etc.)
- `code_length`: Size of generated code in bytes
- `validation_passed`: Boolean
- `details`: Additional information

### Monitor Progress

```bash
# Watch the log file in real-time
tail -f pipeline/logs/progress.csv

# Check the output directory
ls -lh pipeline/output/

# Count successes
grep "validated_success" pipeline/logs/progress.csv | wc -l
```

## Configuration

### Environment Variables

See [Step 2: Setup Environment](#step-2-setup-environment) in Quick Start for detailed setup instructions.

The `.env` file should contain:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Command Line Arguments

```bash
python run_pipeline.py \
  --start 1 \
  --end 100 \
  --max-calls 300 \
  --model openai/gpt-oss-20b
```

| Option        | Default              | Description                         |
| ------------- | -------------------- | ----------------------------------- |
| `--start`     | `1`                  | Starting task number                |
| `--end`       | `100`                | Ending task number                  |
| `--max-calls` | `100`                | Max API calls (tasks × max_retries) |
| `--model`     | `openai/gpt-oss-20b` | Groq model to use                   |

**Note**: `--max-calls` limits the total number of API calls, not tasks. With 3 attempts per task, processing 100 tasks could use up to 300 API calls.

### Available Models

**Recommended (Reasoning Models)**:

- `openai/gpt-oss-20b` **(default)** - GPT-4 OSS reasoning model, excellent for complex patterns
- `llama-3.3-70b-versatile` - High quality, versatile model

**Fast Models**:

- `llama-3.1-8b-instant` - Fastest, good for simple tasks
- `mixtral-8x7b-32768` - Balanced speed and quality

## How It Works

### Pipeline Stages with Iterative Refinement

```
1. Task Manager → Finds and loads task files
2. Task Parser → Extracts train/test examples
3. Prompt Builder → Creates LLM prompt with examples
   ├─ Attempt 1: Generic pattern discovery prompt
   ├─ Attempt 2: Includes previous failed code + error
   └─ Attempt 3: Includes previous failed code + error
4. LLM Generator → Calls Groq API to generate code
5. Output Parser → Extracts Python code from response
6. Code Validator → Checks syntax and tests on training data
   ├─ If PASS: Continue to step 7
   └─ If FAIL: Store error, go back to step 3 (next attempt)
7. File Writer → Saves validated solutions
8. Progress Tracker → Logs all results
```

### Iterative Refinement Process

For each task, the pipeline tries up to 3 times:

**Attempt 1 (Initial)**:

- Uses a generic prompt focused on pattern discovery
- Analyzes dimensions, tiling patterns, transformations
- No prior context

**Attempt 2 (Refinement)**:

```
Previous failed code → Analyze what went wrong → Generate improved solution
```

- Receives the failed code from Attempt 1
- Gets the specific error message
- Model analyzes the failure and corrects its approach

**Attempt 3 (Final Refinement)**:

```
Previous failed code → Analyze what went wrong → Generate improved solution
```

- Receives the failed code from Attempt 2
- Gets the specific error message
- Final attempt with all learned context

### Validation Process

For each generated solution:

1. **Syntax Check**

   ```python
   ast.parse(code)  # Must be valid Python
   ```

2. **Module Import**

   ```python
   module = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(module)
   program = getattr(module, 'p')
   ```

3. **Functional Test**

   ```python
   for example in train_examples:
       result = program(copy.deepcopy(example["input"]))
       assert np.array_equal(result, example["output"])
   ```

4. **Save if Valid**
   - Only saves if 100% pass rate on training examples
   - Logs all results to CSV

## Module Details

### TaskManager (`modules/task_manager.py`)

- Manages task file paths (task001-task400)
- Handles task numbering
- Validates file existence

### TaskParser (`modules/task_parser.py`)

- Loads JSON task files
- Extracts train/test examples
- Formats examples for prompts

### PromptBuilder (`modules/prompt_builder.py`)

- **Dual prompt system**: Initial + Refinement templates
- **Initial prompt**: Generic pattern discovery with dimension analysis
- **Refinement prompt**: Includes previous failed code and error message
- Optimized for code golf constraints
- Includes train and test examples

### LLMCodeGenerator (`modules/llm_generator.py`)

- Groq API integration
- Configurable model (see [Available Models](#available-models) for options)
- Configurable temperature/model
- High token limit (8000) for reasoning space
- Built-in rate limiting
- Tracks API call count

### OutputParser (`modules/output_parser.py`)

- Extracts code from markdown blocks
- Handles various LLM output formats
- Cleans whitespace/formatting

### CodeValidator (`modules/code_validator.py`)

- Syntax validation using AST parsing
- Functional testing on training data
- Uses numpy for array comparison

### FileWriter (`modules/file_writer.py`)

- Saves validated solutions
- Organizes by task ID
- Tracks file existence

### ProgressTracker (`modules/progress_tracker.py`)

- CSV logging
- Statistics tracking
- Real-time progress monitoring

## Example Usage

### Programmatic Usage with Iterative Refinement

```python
from pipeline.modules import (
    TaskManager, TaskParser, PromptBuilder,
    LLMCodeGenerator, CodeValidator, FileWriter,
    OutputParser
)

# Initialize components
script_dir = Path(__file__).parent
data_dir = script_dir / 'data' / 'google-code-golf-2025'
tm = TaskManager(data_dir, 1, 10)
tp = TaskParser()
pb = PromptBuilder()
llm = LLMCodeGenerator(model='openai/gpt-oss-20b')
cv = CodeValidator()
fw = FileWriter('pipeline/output')
op = OutputParser()

# Process a task with iterative refinement
task_path = data_dir / 'task001.json'
train, test = tp.load_task(task_path)
task_data = {"train": train, "test": test}

previous_code = None
previous_error = None
max_attempts = 3

for attempt in range(max_attempts):
    # Build prompt (with previous attempt info if available)
    if attempt == 0:
        prompt = pb.build_prompt(1, train, test)
    else:
        prompt = pb.build_prompt(
            1, train, test,
            previous_code=previous_code,
            error_message=previous_error
        )

    # Generate code
    raw_output = llm.generate(prompt)
    code = op.extract_code(raw_output)

    # Validate
    if cv.is_syntax_valid(code):
        passed, message = cv.passes_training_examples(task_data, code)
        if passed:
            fw.save_code(1, code)
            print(f"Success on attempt {attempt + 1}")
            break
        else:
            # Store for next attempt
            previous_code = code
            previous_error = message
    else:
        previous_code = code
        previous_error = "Syntax error"
```

## Statistics

The pipeline tracks:

- Successful validations
- Syntax errors
- Validation failures
- Exceptions
- Skipped (already solved)

## Example Output

```
================================================================================
Google Code Golf 2025 - Self-Verifying Generation Pipeline
================================================================================
Data directory: /path/to/data/google-code-golf-2025
Output directory: /path/to/pipeline/output
Tasks: 1 to 10
Model: openai/gpt-oss-20b
Max API calls: 100
================================================================================

Found 10 task files

================================================================================
[1/10] Processing Task 001
================================================================================
Train examples: 5
Test examples: 1
Generating code... (attempt 1/3) [Initial]
[LLM] API call #1 completed
Generated code (0 bytes)
Validating syntax...
Validating functionality...
Validation failed: Function p() not found
Retrying with previous solution feedback...
Generating code... (attempt 2/3) [Refinement]
[LLM] API call #2 completed
Generated code (305 bytes)
Validating syntax...
Validating functionality...
Validation passed! Passed 5/5 train examples
Saved validated solution for task 001 (305 bytes)

Waiting 2s before next task...

================================================================================
[2/10] Processing Task 002
================================================================================
Train examples: 5
Test examples: 1
Generating code... (attempt 1/3) [Initial]
[LLM] API call #3 completed
Generated code (187 bytes)
Validating syntax...
Validating functionality...
Validation passed! Passed 5/5 train examples
Saved validated solution for task 002 (187 bytes)

...

================================================================================
PIPELINE SUMMARY
================================================================================
Successful: 8
Syntax errors: 0
Validation failed: 2
Exceptions: 0
Skipped: 0
API calls made: 28
================================================================================
```

**Key Features Shown**:

- `[Initial]` vs `[Refinement]` labels on attempts
- Shows when retrying with previous solution feedback
- Tracks API calls across all attempts
- Displays validation results for each attempt

## Best Practices

1. **Start Small**: Test on task 1 first, then 1-10
2. **Monitor Logs**: Check `pipeline/logs/progress.csv` regularly
3. **Analyze Failures**: Review `pipeline/output/failed/` to understand why attempts failed
4. **Compare Attempts**: Use `diff` to see how the model evolved between attempts
5. **Adjust Temperature**: Lower (0.1) for consistency, higher (0.3) for creativity
6. **Use Reasoning Models**: `openai/gpt-oss-20b` works best for complex ARC patterns
7. **Check API Limits**: Monitor your Groq API usage (each task uses up to 3 calls)
8. **Budget API Calls**: Set `--max-calls` to `tasks × 3` for full retry coverage

## Troubleshooting

### ModuleNotFoundError

```bash
# Make sure you're in the pipeline directory
cd pipeline

# And that Python can find modules
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### API Key Not Found

```bash
# Check your .env file
cat .env | grep GROQ_API_KEY

# Verify key works
curl https://api.groq.com/v1/models -H "Authorization: Bearer $GROQ_API_KEY"
```

### Rate Limit Exceeded

- Wait a few minutes between runs
- Reduce `--max-calls` parameter
- Use a higher quality model but call less frequently

### Validation Failures

- Check task examples manually
- Try different models
- Adjust temperature (0.1-0.3)
- Enable retries in run_pipeline.py

## Running Tests

```bash
# Run all tests
python pipeline/tests/test_pipeline.py

# Test specific component
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('pipeline') / 'modules'))
from pipeline.modules import TaskManager, TaskParser
tm = TaskManager('data/google-code-golf-2025', 1, 1)
paths = tm.get_task_paths()
tp = TaskParser()
data = tp.load_task(paths[0])
print(f'Task has {len(data[\"train\"])} train examples')
"
```

## Next Steps

1. **Start with a single task** (see [Step 5](#step-5-run-on-a-single-task-testing))
2. **Review the output** in `pipeline/output/` and check logs in `pipeline/logs/progress.csv`
3. **Analyze failed attempts** using the debugging commands in the [Output section](#failed-attempts-for-debugging)
4. **Process a subset** (see [Step 6](#step-6-run-on-a-small-subset)) to validate your setup
5. **Scale up to all tasks** (see [Step 7](#step-7-process-all-tasks)) when ready
6. **Submit validated solutions** to Kaggle

For detailed information on how iterative refinement works, see [Iterative Refinement Process](#iterative-refinement-process).

## Development

### Adding New Modules

1. Create module in `modules/`
2. Import in `modules/__init__.py`
3. Update `run_pipeline.py`
4. Test with `tests/test_pipeline.py`
5. Update documentation

### Debugging

Enable verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

See the parent directory README for license information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions, please open a GitHub issue.

---
