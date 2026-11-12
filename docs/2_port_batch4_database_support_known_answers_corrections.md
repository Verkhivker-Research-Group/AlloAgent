# Dated corrections to the port batch 4 known answers

**Dated 2026-10-23.** Per the standing rule the criteria file
`docs/2_port_batch4_database_support_known_answers.md` is NOT edited;
the corrections are recorded here, each with the evidence that forced it.

The batch was implemented and run once. Three expectations in that file
were wrong.

## C-8 — F-10: `importlib.import_module` is NOT blocked

F-10 states that the command
`"import importlib; importlib.import_module('os')"` is refused with
`"Error: Import of module 'os' is restricted by agent configuration"`.

**Evidence** (in-container run, 2026-10-23):

```
E  assert False
E   +  where False = <built-in method startswith of str object at 0x560546357d20>(
E   +      "Error: Import of module 'os' is restricted by agent configuration")
E   +    +  where False = ''.startswith
```

The output was the empty string: the import **succeeded**.

**Correction.** `importlib.import_module` does not go through
`builtins.__import__`; it calls the import machinery directly, so the
custom importer installed for the execution never sees it. The old code
had exactly the same gap -- it installed the same `__import__` override
-- so this is not a regression, but F-10 asserted a stronger guarantee
than the tool ever provided.

The blocked forms are the ones the tool actually refuses:

- `import os` and `from os import path` are caught by the static scan
  (F-7, F-8);
- `import os.path` is caught by the static scan (F-9);
- a direct `__import__('os')` call goes through the replaced importer
  and is refused with
  `"Error: Import of module 'os' is restricted by agent configuration"`.

**What changed.** The test now asserts the direct `__import__` form
(F-10), which is the dynamic guarantee the tool does provide, and the
tool card states the limit explicitly: the restriction is a prefix list
enforced on the REPL's imports, **not a sandbox**; `importlib`'s
direct machinery call is not intercepted.

## C-9 — F-13: the error text is the exception's message, not its type

F-13 states the output starts `"Error: ZeroDivisionError"`.

**Evidence:**

```
E  AssertionError: assert False
E   +  where False = <built-in method startswith of str object at 0x7f688769c20>(
E   +      "Error: ZeroDivisionError")
E   +    +  where False = 'Error: division by zero'.startswith
```

**Correction.** The output is `"Error: division by zero"`. The old code
built the message as `f"Error: {str(e)}"`, which is the exception's
*message*, not its type name; the port keeps that.

## C-10 — F-15 / F-16: the OpenTargets Genetics API host no longer exists

F-15 and F-16 state that a live GraphQL query against
`https://api.genetics.opentargets.org/graphql` returns
`__typename == "Query"`.

**Evidence** (in-container run, and confirmed from the host):

```
E  AssertionError: {'error': 'API error: HTTPSConnectionPool(
E      host=\'api.genetics.opentargets.org\', port=443): Max retries
E      exceeded with ... https://api.genetics.opentargets.org/graphql\',
E      \'method\': \'POST\'}', ...}
```

and from the host:

```
https://api.genetics.opentargets.org/graphql -> ERROR: The remote name
  could not be resolved: 'api.genetics.opentargets.org'
```

**Correction.** The hostname does not resolve. The OpenTargets Genetics
API was retired and its content folded into the OpenTargets **Platform**
API, which this repo's `query_opentarget` already uses. The port is
faithful -- it issues exactly the query the old tool issued -- but the
upstream service is gone.

**What changed.** The known-answer test now asserts the contract the
tool can actually honour: the call returns a dict, and either it
succeeds with `result.data.__typename == "Query"`, or it fails with a
structured `error` that names the endpoint. As of 2026-10-23 the second
branch is the live one, and the error text is checked to name the
endpoint so a silent hang or a wrong URL cannot pass for a failure.

**Disposition.** `query_opentarget_genetics` is ported and registered,
but it is **not exposed to arm D** and is recorded in
the old-tool review (moved out of this tree to ../alloagent_private/docs/old_tool_review/SUMMARY.md) as PARTIAL with the reason "the
OpenTargets Genetics API host no longer resolves".
