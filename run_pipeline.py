"""
Google Code Golf 2025 - Self-Verifying Generation Pipeline
Main orchestrator script
"""

import os
import sys
import time
from pathlib import Path

# Add pipeline/modules to path
pipeline_dir = Path(__file__).parent / 'pipeline'
sys.path.insert(0, str(pipeline_dir / 'modules'))

from pipeline.modules import (
    TaskManager,
    TaskParser,
    PromptBuilder,
    LLMCodeGenerator,
    OutputParser,
    CodeValidator,
    FileWriter,
    ProgressTracker
)


def run_pipeline(
    data_dir: str,
    output_dir: str,
    log_dir: str = "logs",
    start: int = 1,
    end: int = 100,
    max_api_calls: int = 100,
    model: str = "openai/gpt-oss-20b",
    retry_on_failure: bool = True,
    max_retries: int = 2
):
    """
    Run the complete pipeline for generating and validating code solutions.
    
    Args:
        data_dir: Path to data directory with task JSON files
        output_dir: Directory to save validated solutions
        log_dir: Directory for log files
        start: Starting task number
        end: Ending task number
        max_api_calls: Maximum LLM API calls to make
        model: Groq model to use
        retry_on_failure: Whether to retry failed generations
        max_retries: Maximum number of retry attempts
    """
    print("=" * 80)
    print("🚀 Google Code Golf 2025 - Self-Verifying Generation Pipeline")
    print("=" * 80)
    print(f"📁 Data directory: {data_dir}")
    print(f"💾 Output directory: {output_dir}")
    print(f"📊 Tasks: {start} to {end}")
    print(f"🤖 Model: {model}")
    print(f"🔄 Max API calls: {max_api_calls}")
    print("=" * 80)
    print()
    
    # Initialize components
    task_manager = TaskManager(data_dir, start, end)
    task_parser = TaskParser()
    prompt_builder = PromptBuilder()
    llm_generator = LLMCodeGenerator(model=model, temperature=0.2)
    output_parser = OutputParser()
    code_validator = CodeValidator()
    file_writer = FileWriter(output_dir)
    progress_tracker = ProgressTracker(os.path.join(log_dir, "progress.csv"))
    
    # Get task paths
    task_paths = task_manager.get_task_paths()
    print(f"📋 Found {len(task_paths)} task files\n")
    
    stats = {
        'success': 0,
        'syntax_error': 0,
        'validation_failed': 0,
        'exception': 0,
        'skipped': 0
    }
    
    # Process each task
    for idx, task_path in enumerate(task_paths[:max_api_calls], 1):
        if llm_generator.api_calls >= max_api_calls:
            print(f"\n⛔ Reached maximum API call limit ({max_api_calls})")
            break
        
        try:
            task_id = task_manager.get_task_num_from_path(task_path)
            
            # Check if already solved
            if file_writer.file_exists(task_id):
                print(f"[{idx}/{len(task_paths)}] Task {task_id:03d} - Already solved, skipping")
                stats['skipped'] += 1
                continue
            
            print(f"\n{'=' * 80}")
            print(f"[{idx}/{len(task_paths)}] Processing Task {task_id:03d}")
            print(f"{'=' * 80}")
            
            # Load task data
            task_data = task_parser.load_task(task_path)
            train_examples, test_examples = task_parser.get_train_test(task_data)
            
            print(f"📚 Train examples: {len(train_examples)}")
            print(f"🧪 Test examples: {len(test_examples)}")
            
            # Try generation (with retries)
            success = False
            previous_code = None
            previous_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Build prompt (with previous attempt info for refinement)
                    if attempt == 0:
                        print(f"🤖 Generating code... (attempt {attempt + 1}/{max_retries + 1}) [Initial]")
                        prompt = prompt_builder.build_prompt(
                            task_id, train_examples, test_examples
                        )
                    else:
                        print(f"🤖 Generating code... (attempt {attempt + 1}/{max_retries + 1}) [Refinement]")
                        prompt = prompt_builder.build_prompt(
                            task_id, train_examples, test_examples,
                            previous_code=previous_code,
                            error_message=previous_error
                        )
                    
                    # Generate code
                    raw_output = llm_generator.generate(prompt)
                    
                    # Parse output
                    code = output_parser.extract_code(raw_output)
                    print(f"📝 Generated code ({len(code)} bytes)")
                    
                    # Validate syntax
                    print("🔍 Validating syntax...")
                    if not code_validator.is_syntax_valid(code):
                        print("❌ Syntax error detected")
                        stats['syntax_error'] += 1
                        progress_tracker.log(task_id, 'syntax_error', len(code), False)
                        
                        # Store for next attempt
                        previous_code = code
                        previous_error = "Syntax error: Code has invalid Python syntax"
                        
                        if retry_on_failure and attempt < max_retries:
                            print(f"🔄 Retrying with error feedback...")
                            continue
                        break
                    
                    # Validate functionality
                    print("✅ Validating functionality...")
                    passed, message = code_validator.passes_training_examples(task_data, code)
                    
                    if passed:
                        print(f"✅ Validation passed! {message}")
                        file_writer.save_code(task_id, code)
                        progress_tracker.log(
                            task_id, 'validated_success', 
                            len(code), True, 
                            f"api_calls={llm_generator.api_calls},attempt={attempt+1}"
                        )
                        stats['success'] += 1
                        success = True
                        break
                    else:
                        print(f"❌ Validation failed: {message}")
                        stats['validation_failed'] += 1
                        
                        # Save failed attempt for debugging
                        failed_dir = Path(output_dir) / "failed"
                        failed_dir.mkdir(exist_ok=True, parents=True)
                        failed_file = failed_dir / f"task{task_id:03d}_attempt{attempt+1}.py"
                        with open(failed_file, 'w') as f:
                            f.write(code)
                        
                        # Store for next attempt
                        previous_code = code
                        previous_error = message
                        
                        progress_tracker.log(
                            task_id, 'failed_validation', 
                            len(code), False, 
                            message
                        )
                        if retry_on_failure and attempt < max_retries:
                            print(f"🔄 Retrying with previous solution feedback...")
                            continue
                        break
                        
                except Exception as e:
                    print(f"❌ Exception during generation: {e}")
                    stats['exception'] += 1
                    
                    # Store for next attempt
                    previous_error = f"Exception: {str(e)}"
                    if previous_code:  # Keep previous code if available
                        pass
                    
                    progress_tracker.log(
                        task_id, f'exception', 
                        0, False, 
                        str(e)
                    )
                    if retry_on_failure and attempt < max_retries:
                        print(f"🔄 Retrying with error feedback...")
                        continue
                    break
            
            if not success:
                print(f"❌ Failed to generate valid solution for task {task_id:03d}")
            
            # Add delay between tasks to avoid rate limiting
            if idx < len(task_paths):
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error processing task: {e}")
            import traceback
            traceback.print_exc()
            stats['exception'] += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 PIPELINE SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {stats['success']}")
    print(f"❌ Syntax errors: {stats['syntax_error']}")
    print(f"❌ Validation failed: {stats['validation_failed']}")
    print(f"❌ Exceptions: {stats['exception']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print(f"📞 API calls made: {llm_generator.api_calls}")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate and validate code solutions for Google Code Golf 2025"
    )
    parser.add_argument(
        '--data-dir',
        default='data/google-code-golf-2025',
        help='Path to data directory with task files'
    )
    parser.add_argument(
        '--output-dir',
        default='pipeline/output',
        help='Directory to save validated solutions'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Starting task number'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=10,
        help='Ending task number'
    )
    parser.add_argument(
        '--max-calls',
        type=int,
        default=100,
        help='Maximum API calls to make'
    )
    parser.add_argument(
        '--model',
        default='openai/gpt-oss-20b',
        help='Groq model to use (openai/gpt-oss-20b - reasoning model)'
    )
    
    args = parser.parse_args()
    
    # Adjust paths to be relative to script location
    script_dir = Path(__file__).parent
    data_dir = script_dir / args.data_dir
    output_dir = script_dir / args.output_dir
    log_dir = script_dir / "pipeline" / "logs"
    
    run_pipeline(
        data_dir=str(data_dir),
        output_dir=str(output_dir),
        log_dir=str(log_dir),
        start=args.start,
        end=args.end,
        max_api_calls=args.max_calls,
        model=args.model
    )

