# Synthetic data dictionary

| Field | Type | Meaning |
|---|---|---|
| `participant_id` | string | Opaque synthetic ID with `SYN-P` prefix. |
| `session_id` | string | Opaque synthetic cluster ID with `SYN-S` prefix. |
| `block` | enum | Pre-treatment randomization stratum B1–B4. |
| `cell_id` | string | Frozen treatment-matrix cell. |
| `assignment_order` | integer | Concealed manifest order. |
| `round` | integer | Task round. |
| `independent_source_acquisition` | 0/1 | Primary acquisition outcome. |
| `truthful_report` | 0/1 | Primary truthfulness outcome. |
| `action_obedience` | 0/1 | Primary recommendation-obedience outcome. |
| `public_signal_use` | proportion | Team share of actions using the public clue. |
| `one_reader_alignment` | 0/1 | Exactly one role conditions on the public clue. |
| `off_signal_rescue` | 0/1 | Discovery by an action differing from the public clue. |
| `contrarian_action` | proportion | Team share choosing the registered third option on disagreement. |
| `synthetic_only` | boolean | Must always be true in this repository phase. |

No direct identifiers or free-form personal fields are permitted.
