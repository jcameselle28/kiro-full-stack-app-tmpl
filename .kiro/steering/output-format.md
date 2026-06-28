# Output and Reporting Format

Standardize how results are presented across all operations.

## Status Indicators
- ✅ Success / passing / done
- ⚠️ Warning / needs attention
- ❌ Failure / error / blocked
- 🔄 In progress / pending

## Change Reports

After any code or config change, report:
```
[status] Summary
- Action: what was done
- Files: affected files
- Verification: build/test/lint result
- Follow-ups: anything left to do (if any)
```

## Code & Commands
- Use code blocks for code, commands, and config
- Specify the language on every fenced block
- Keep commands copy-pasteable; avoid placeholders unless necessary

## Structured Data
- Use tables for lists of items (endpoints, env vars, dependencies)
- Include clear column headers
- Sort by the most relevant field
- Show totals/summaries at the bottom when applicable

## Error Reports
- Show the exact error message
- Identify the probable cause
- Suggest 2-3 actionable next steps
- Link to relevant documentation when helpful

## General Rules
- Keep output concise, no filler text
- Lead with the most important information first
- Group related information together
