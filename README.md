# Error Definitions

This repository contains YAML-based error definitions and code generators 
for Onedata services.

## Structure

Error definitions are stored in `definitions/` directory, organized by categories:
- `auth/` - authentication and authorization errors
- `connection/` - network connectivity errors 
- `data_validation/` - data validation errors
- `general/` - common system errors
- `graph_sync/` - graph sync protocol errors
- `onepanel/` - Onepanel specific errors
- `op_worker/` - Oneprovider worker specific errors
- `oz_worker/` - Onezone worker specific errors
- `posix/` - POSIX errors

Each error definition contains:
- `id` - unique identifier of the error
- `args` - list of arguments returned in `details` field of the error response as well as used in `description`
- `description` - error description with placeholders for `args`
- `http_code` - HTTP status code to be returned in REST API response for the error
- `errno` - POSIX error number associated with the error (optional)


## Adding New Errors

Add new YAML definition file in appropriate category under `definitions/` directory. 

Caveats:
1. When writing a `description` for an error, consider whether new lines should 
be preserved in the generated code. If so, always remember to use `|-` in the 
description. For example, if the description is:

```yaml
description: |-
    You must authenticate yourself to perform this operation. 
    {authError}
```

2. `args` is a list of objects with the following fields:
   - `name`: string() - the name of the argument
   - `nullable`: boolean(), default: `false` - indicates whether the field is 
     optional and as such appears as null in details or is absent. Such an 
     argument should be the last in the list.
   - `type`: default: `Binary` - specifies the type. Currently implemented types are:
     - `AaiConsumer`
     - `AaiService`
     - `Atom`
     - `AtmDataType`
     - `AtmDataTypes`
     - `AtmStoreSchemaIds`
     - `AtmTaskArgumentValueBuilderType`
     - `AtmTaskArgumentValueBuilderTypes`
     - `AtmWorkflowSchemas`
     - `Binary`
     - `Binaries`
     - `ByteSize`
     - `CaveatUnverified`
     - `DnsServers`
     - `ErlangTerm`
     - `GriEntityType`
     - `GriEntityTypeAsAtom`
     - `Integer`
     - `InviteTokenTypeWithAny`
     - `Json`
     - `MetricConfig`
     - `OnedataError`
     - `Path`
     - `ProviderSupportStage`
     - `StorageSupportStage`
     - `TokenType`
     - `TscLayout`


## Code Generation

Currently supported languages:
- [erlang](###Erlang)

Generated code will be placed in `generated/{language}` directory.

### Erlang

Requirements:
- Python >= 3.8

To generate Erlang code run:

```bash
make erlang
```

Generated Erlang components:
- `errors.hrl` - Error macros definitions
- `errors.erl` - Main error interface module  
- `od_error.erl` - Behaviour specification for error types
- `types/*.erl` - Generated error type modules
