# Auto-Logging Protocol

## Core Principle
**If it would hurt to lose it, it gets logged. Period.**

Don't wait to be asked. Don't say "I'll save that" - SAVE IT FIRST, then say you did.

## Automatic Triggers

### Immediate Log (No Permission Needed)

| Event | Action | Location |
|-------|--------|----------|
| New idea mentioned | Log immediately | `driftwood` |
| Script created/modified | Update manifest | `scripts/manifest.md` |
| Significant decision | Capture it | Relevant state file |
| New term/concept | Add to glossary | `driftwood` or `running_phrases` |
| Breakthrough moment | Session log entry | `session_log` |
| New person introduced | Add to collaborators | `collaborators.json` |

### 93& = Harvest Signal

When user sends `93&` (closing), Planty does final checks:
1. Scan session for uncommitted ideas/decisions
2. Reorganize any hasty driftwood entries into proper locations
3. Check `_scratch/unanswered.md` - surface any critical skipped questions
4. Brief session summary if meaty

### Session Checkpoints

Every ~20-30 exchanges OR at natural breaks:
- Quick self-audit of what's been discussed
- Commit uncommitted items
- Note any questions that got skipped

## Unanswered Questions Protocol

**Problem**: Async reading - long responses get skimmed, important questions missed.

**Solution**: Track them in `_scratch/unanswered.md`

When Planty asks something important and doesn't get a response:
- Log the question with timestamp
- Surface again at 93& or when relevant
- Remove once answered

Questions that warrant tracking:
- Decisions that block progress
- Clarifications needed for accuracy
- Things user explicitly needs to weigh in on

NOT worth tracking:
- Rhetorical questions
- "Want me to X?" (assume yes unless they say no)
- Casual conversation

## Warning Signs (Context Approaching Limit)

When Planty notices limits approaching:
> "🌿 leaves wilting - good time to harvest and fresh start?"

## The Iron Rules

1. **Log first, discuss second** - half-life of thought is 4 seconds
2. **93& triggers harvest** - final cleanup pass
3. **Track skipped questions** - don't let important stuff fall through
4. **Keep responses scannable** - user skims, make key points visible
