# Versioning

X-Ray exposes algorithm version fields on valid engine outputs to support reproducibility and auditability.

## Current Version Fields

Valid outputs include:

```python
{
    "rf_version": "v1_heuristic",
    "rf_token_version": "v1_token_overlap_cl100k_multiset_curr_norm",
    "contribution_version": "v2_softnorm_floor",
    "validation_version": "v2_continuity",
    "tokenizer_version": "cl100k_base"
}
```

Invalid fail-safe outputs intentionally do not include version fields.

## Why Versioning Exists

Version fields make it possible to:

- audit which algorithms produced a result
- detect behavioral changes across releases
- compare regression fixture outputs
- preserve deterministic infrastructure contracts

## Field Meanings

### `rf_version`

Tracks the redundancy-factor implementation used for contribution calculations.

Current value:

```text
v1_heuristic
```

### `rf_token_version`

Tracks the token-level RF diagnostic implementation.

Current value:

```text
v1_token_overlap_cl100k_multiset_curr_norm
```

### `contribution_version`

Tracks contribution normalization and floor behavior.

Current value:

```text
v2_softnorm_floor
```

### `validation_version`

Tracks execution-validity behavior.

Current value:

```text
v2_continuity
```

### `tokenizer_version`

Tracks the tokenizer used for token-level diagnostics.

Current value:

```text
cl100k_base
```

## Auditability Rule

If any algorithmic behavior changes, the corresponding version field should change in the same release.

Documentation and regression fixtures must be updated with the changed version behavior.

