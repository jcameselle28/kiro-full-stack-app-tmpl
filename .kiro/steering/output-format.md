---
inclusion: always
---

# Output and Reporting Format

Standardize how results are presented across all operations.

## Status Indicators
- ✅ Success / healthy / compliant
- ⚠️ Warning / degraded / needs attention
- ❌ Failure / critical / non-compliant
- 🔄 In progress / pending

## Operation Reports

After any mutation or state change, report:
```
[status] Operation Summary
- Action: what was done
- Resource: affected resource identifier
- Previous state: before the change
- Current state: after the change
- Rollback: how to revert if needed
```

## Query Results
- Use tables for structured data (instances, costs, resources)
- Include column headers: ID, Name/Tag, Status, Type, Region
- Sort by most relevant field (status for health checks, cost for billing)
- Show totals/summaries at the bottom when applicable

## Cost Reports
- Always show amounts in USD with 2 decimal places
- Include percentage of total when showing breakdowns
- Flag items above a reasonable threshold with ⚠️
- Show date range covered by the report

## Error Reports
- Show the exact error message
- Identify probable cause
- Suggest 2-3 actionable next steps
- Include relevant AWS documentation links when helpful

## General Rules
- Keep output concise, no filler text
- Use code blocks for CLI commands and JSON
- Group related information together
- Lead with the most important information first
