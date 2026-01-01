import sys
from io import StringIO
from typing import List

# Create a persistent namespace that will be shared across all executions
_persistent_namespace = {}
# List of module prefixes that should NOT be importable from the REPL (can be set by agent)
_RESTRICTED_IMPORT_PREFIXES: List[str] = []


def set_restricted_imports(prefixes: List[str]):
    """Set a list of module name prefixes which will be blocked from being imported in the REPL."""
    global _RESTRICTED_IMPORT_PREFIXES
    _RESTRICTED_IMPORT_PREFIXES = prefixes.copy() if prefixes else []


def _is_import_restricted(module_name: str) -> bool:
    for prefix in _RESTRICTED_IMPORT_PREFIXES:
        if module_name == prefix or module_name.startswith(prefix + "."):
            return True
    return False


def run_python_repl(command: str) -> str:
    """Executes the provided Python command in a persistent environment and returns the output.
    Variables defined in one execution will be available in subsequent executions.

    The REPL respects the module import restrictions set with `set_restricted_imports`.
    """

    def execute_in_repl(command: str) -> str:
        """Helper function to execute the command in the persistent environment."""
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        # Use the persistent namespace
        global _persistent_namespace

        # Quick static scan: block obviously forbidden import lines
        lowered = command.lower()
        for prefix in _RESTRICTED_IMPORT_PREFIXES:
            if f"import {prefix.lower()}" in lowered or f"from {prefix.lower()}" in lowered:
                return f"Error: Import of restricted module prefix '{prefix}' is blocked by agent policy."

        # Create a custom __import__ to enforce restrictions dynamically during execution
        import builtins as _builtins_module

        def _custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if _is_import_restricted(name):
                raise ImportError(f"Import of module '{name}' is restricted by agent configuration")
            return orig_import(name, globals, locals, fromlist, level)

        # Save original __import__ from the current builtins
        orig_import = _builtins_module.__import__

        # Prepare a modified builtins dict that uses the custom importer
        # Preserve original builtins content, but override __import__
        current_builtins = _persistent_namespace.get("__builtins__", _builtins_module)
        if isinstance(current_builtins, dict):
            builtins_copy = dict(current_builtins)
        else:
            builtins_copy = dict(vars(current_builtins))
        builtins_copy["__import__"] = _custom_import

        # Inject custom builtins for the duration of the exec
        _persistent_namespace["__builtins__"] = builtins_copy

        try:
            # Execute the command in the persistent namespace
            exec(command, _persistent_namespace)
            output = mystdout.getvalue()
        except Exception as e:
            output = f"Error: {str(e)}"
        finally:
            # Restore the original builtins if present
            _persistent_namespace["__builtins__"] = current_builtins
            sys.stdout = old_stdout
        return output

    command = command.strip("```").strip()
    return execute_in_repl(command)


def read_function_source_code(function_name: str) -> str:
    """Read the source code of a function from any module path.

    Parameters
    ----------
        function_name (str): Fully qualified function name (e.g., 'bioagentos.tool.support_tools.write_python_code')

    Returns
    -------
        str: The source code of the function

    """
    import importlib
    import inspect

    # Split the function name into module path and function name
    parts = function_name.split(".")
    module_path = ".".join(parts[:-1])
    func_name = parts[-1]

    try:
        # Import the module
        module = importlib.import_module(module_path)

        # Get the function object from the module
        function = getattr(module, func_name)

        # Get the source code of the function
        source_code = inspect.getsource(function)

        return source_code
    except (ImportError, AttributeError) as e:
        return f"Error: Could not find function '{function_name}'. Details: {str(e)}"


# def request_human_feedback(question, context, reason_for_uncertainty):
#     """
#     Request human feedback on a question.

#     Parameters:
#         question (str): The question that needs human feedback.
#         context (str): Context or details that help the human understand the situation.
#         reason_for_uncertainty (str): Explanation for why the LLM is uncertain about its answer.

#     Returns:
#         str: The feedback provided by the human.
#     """
#     print("Requesting human feedback...")
#     print(f"Question: {question}")
#     print(f"Context: {context}")
#     print(f"Reason for Uncertainty: {reason_for_uncertainty}")

#     # Capture human feedback
#     human_response = input("Please provide your feedback: ")

#     return human_response
