"""
Test script to verify pipeline components work correctly
"""

import sys
from pathlib import Path

# Add modules to path (go up one directory from tests/)
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    try:
        from modules import (
            TaskManager,
            TaskParser,
            PromptBuilder,
            LLMCodeGenerator,
            OutputParser,
            CodeValidator,
            FileWriter,
            ProgressTracker
        )
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_task_manager():
    """Test TaskManager"""
    print("\nTesting TaskManager...")
    try:
        from modules import TaskManager
        tm = TaskManager('../../data/google-code-golf-2025', 1, 5)
        paths = tm.get_task_paths()
        print(f"✓ TaskManager found {len(paths)} task files")
        return len(paths) > 0
    except Exception as e:
        print(f"✗ TaskManager failed: {e}")
        return False

def test_task_parser():
    """Test TaskParser"""
    print("\nTesting TaskParser...")
    try:
        from modules import TaskParser
        tp = TaskParser()
        
        # Try to load a task
        task_path = '../../data/google-code-golf-2025/task001.json'
        if Path(task_path).exists():
            data = tp.load_task(task_path)
            train, test = tp.get_train_test(data)
            print(f"✓ TaskParser loaded task with {len(train)} train and {len(test)} test examples")
            return True
        else:
            print("✗ Task file not found")
            return False
    except Exception as e:
        print(f"✗ TaskParser failed: {e}")
        return False

def test_prompt_builder():
    """Test PromptBuilder"""
    print("\nTesting PromptBuilder...")
    try:
        from modules import PromptBuilder
        pb = PromptBuilder()
        
        # Create mock examples
        train_examples = [
            {"input": [[0, 1], [1, 0]], "output": [[1, 0], [0, 1]]}
        ]
        test_examples = []
        
        prompt = pb.build_prompt(1, train_examples, test_examples)
        print(f"✓ PromptBuilder created prompt ({len(prompt)} chars)")
        return True
    except Exception as e:
        print(f"✗ PromptBuilder failed: {e}")
        return False

def test_code_validator():
    """Test CodeValidator"""
    print("\nTesting CodeValidator...")
    try:
        from modules import CodeValidator
        
        # Test syntax validation
        valid_code = "def p(g):\n    return g[::-1]"
        invalid_code = "def p(g:\n    return invalid"
        
        cv = CodeValidator()
        assert cv.is_syntax_valid(valid_code) == True
        assert cv.is_syntax_valid(invalid_code) == False
        
        print("✓ CodeValidator working correctly")
        return True
    except Exception as e:
        print(f"✗ CodeValidator failed: {e}")
        return False

def test_output_parser():
    """Test OutputParser"""
    print("\nTesting OutputParser...")
    try:
        from modules import OutputParser
        
        # Test markdown extraction
        raw_with_md = "```python\ndef p(g):\n    return g\n```"
        raw_no_md = "def p(g):\n    return g"
        
        op = OutputParser()
        
        code1 = op.extract_code(raw_with_md)
        code2 = op.extract_code(raw_no_md)
        
        print(f"✓ OutputParser extracted code from both formats")
        return True
    except Exception as e:
        print(f"✗ OutputParser failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Pipeline Component Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_task_manager,
        test_task_parser,
        test_prompt_builder,
        test_code_validator,
        test_output_parser
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} raised exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

