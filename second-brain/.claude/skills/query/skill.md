# /query — Ask Questions Across the Vault

Synthesise knowledge from across the vault to answer business questions.

## When to use

Run any time you need to answer a question about Onelife Health by pulling together information from multiple vault pages.

## How it works

1. **Receive question** — The user asks a natural-language question about the business.

2. **Identify relevant pages** — Scan MANIFEST.md files across all three pillars to identify which knowledge pages are relevant. Read them.

3. **Synthesise answer** — Combine information from multiple sources into a coherent answer. Always cite your sources using `[[wikilinks]]`.

4. **Generate synthesis page** (optional) — For complex questions, create a new page:
   - Save to `Intelligence/Knowledge/reports/query-{slug}.md`
   - Include frontmatter with `source: query`, the question asked, and date
   - Link to all source pages used

5. **Update memory.md** — Record the question and key findings.

## Example queries

- "Which store has the best margin performance?"
- "What's our exposure to DSI if they stop delivering?"
- "Which products should we promote online next month?"
- "Give me a supplier risk assessment"
- "What are the top 3 things we should fix this week?"

## Answer format

```markdown
## Answer

[2-3 paragraph synthesis with bold key figures]

## Sources

- [[Business/Knowledge/stores/centurion]]
- [[Operations/Knowledge/stock/double-down]]
- ...

## Confidence

[High / Medium / Low] — based on data freshness and coverage
```

## Rules

- Never invent data. If the vault doesn't have the answer, say so.
- Always state the data period when citing figures.
- Flag when data might be stale (>30 days old).
- Prefer insight over data dump — answer the "so what?" not just the "what."
