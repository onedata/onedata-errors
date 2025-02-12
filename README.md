# Error Definitions

## Table of Contents
- [Overview](#overview)
- [Structure](#structure)
- [Error Definition Guide](#error-definition-guide)
  - [File Location and Naming](#file-location-and-naming)
  - [Error Definition Structure](#error-definition-structure)
  - [Examples](#examples)
  - [Best Practices](#best-practices)
- [Type System](#type-system)
  - [Available Types](#available-types)
  - [Adding New Types](#adding-new-types)
- [Code Generation](#code-generation)
  - [Erlang](#erlang)

## Overview

This repository provides a framework for defining and handling errors across Onedata services:
- Standardized error definitions in YAML format
- Code generation for consistent error handling
- Uniform error responses in REST APIs

The workflow:
1. Define errors in YAML files
2. Generate code using provided generators 
3. Use generated code in your service

## Structure

Error definitions are stored in `definitions/` directory, organized by categories

## Error Definition Guide

### File Location and Naming

New error definitions should be added to appropriate category under `definitions/` 
directory following these conventions:
- Use snake_case for filenames
- Name should reflect the error condition
- Extension must be `.yaml`

Example: `definitions/auth/invalid_credentials.yaml`

### Error Definition Structure

Each error definition may include the following fields:

```yaml
# (required) Unique identifier of the error (camelCase)
id: invalidCredentials

# (optional) List of arguments used in description and returned in error details
args:
  # May be referenced in description
  - name: token
    # Argument type (see Type System for available types)
    type: TokenType
    # (optional, defaults to false) Specifies if argument can be null/missing
    nullable: false
    # (optional) Text to show in description when value is null/missing
    print_if_null: no details available

# (required) Human-readable error description with {argName} placeholders
description: >-
  Invalid credentials provided. Token: {token}

# (required) HTTP status code for REST API responses
http_code: 401

# (optional, defaults to EINVAL) POSIX error number
errno: EACCES
```
### Examples

#### Simple Error
```yaml
id: serviceUnavailable
http_code: 503
description: The service is temporarily unavailable. Please try again later.
```

#### Complex Error
```yaml
id: tokenCaveatUnverified
args:
  - name: caveat
    type: UnverifiedCaveat
  - name: requiredPermission
    type: Binary
description: |-
  Token verification failed.
  Unverified caveat: {caveat}
  Required permissions: {requiredPermission}
http_code: 403
```

### Best Practices

#### Description Formatting
- **Preferred** Use `>-` for folding text block into a single line (newlines are converted to spaces).
- Use `|-` for multiline descriptions to preserve formatting (newlines are kept).
- Use `{argumentName}` for argument placeholders in descriptions. The actual values for these arguments will be inserted according to the `print_encoding_strategy`, which can be found in the respective argument type classes.
- Use `"` as quotes instead of `'`.
- Consider message readability.

## Type System

Each type must be implemented for all supported generators to work properly. 
For example, Erlang generator type implementations can be found in 
`./generators/erlang/error_args/types/`.

### Available Types
- `AaiService` - AAI service type  
- `AaiSubject` - AAI subject type
- `AtmDataType` - ATM data type
<!--- TODO VFS-12587 Replace with List<AtmDataType> -->
- `AtmDataTypes` - List of ATM data types
- `AtmStoreTypes` - List of ATM store types
- `AtmTaskArgumentValueBuilderType` - ATM task argument value builder type
<!--- TODO VFS-12587 Replace with List<AtmTaskArgumentValueBuilderType> -->
- `AtmTaskArgumentValueBuilderTypes` - List of ATM task argument value builder types
- `AtmWorkflowSchemaIds` - List of ATM workflow schema IDs
<!--- TODO VFS-12588 Replace with Enum type with concrete set of values -->
- `Atom` - Erlang atom
- `Binaries` - List of binary strings
- `Binary` - Binary string (default)
- `DnsServers` - List of DNS servers
- `GriEntityType` - GRI entity type
- `Integer` - Integer number
- `InviteTokenType` - Invite token type
- `Json` - JSON value
- `OnedataError` - Onedata error
<!--- TODO VFS-12589 Remove this type -->
- `Path` - File system path
- `ProviderSupportStage` - Provider support stage
- `StorageSupportStage` - Storage support stage
- `TokenType` - Token type
- `TscLayout` - Time series collection layout
- `TscMetricConfig` - Time series collection metric configuration
- `UnverifiedCaveat` - Unverified caveat

### Adding New Types

Each type must be implemented separately for every supported generator. 
Below is an example of implementing a new type for the Erlang generator.

To handle a new argument type in Erlang generator:

1. Create file in `generators/erlang/error_args/types/`
2. Define class inheriting from `ErrorArgType`:

```python
from typing import ClassVar
from ..base import ErrorArgType
from ..expressions import SimpleExpression
from ..translation_strategies import CustomStrategy

class MyType(ErrorArgType):
    """My custom type."""
    
    fmt_control_sequence: ClassVar[str] = "~ts"
    json_encoding_strategy: ClassVar[JsonEncodingStrategy] = CustomStrategy(
        SimpleExpression("my_module:to_json({var})")
    )
```

Required class variables:
- `fmt_control_sequence`: Erlang format string
- Optional strategies:
  - `json_encoding_strategy`
  - `json_decoding_strategy`
  - `print_encoding_strategy`

## Code Generation

### Erlang

Requirements:
- Python >= 3.8

Usage:
```bash
make erlang
```

Generated components:
- `errors.hrl`
  - Error macros (?ERR_*)
  - Record definitions
- `errors.erl`
  - Error interface module
- `od_error.erl`
  - Behaviour specification
  - Common types
  - Utility functions
- `types/*.erl`
  - Type-specific handling
  - Custom formatting
