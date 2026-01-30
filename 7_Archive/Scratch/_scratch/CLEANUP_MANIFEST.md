# Nexus Cleanup Manifest
## Generated: 2026-01-21 by Planty C

**Status:** Ready for execution by Wrex/Poofox

---

## 1. DUPLICATE FOLDERS - DELETE ONE

### memory_archive vs MemoryArchive
**IDENTICAL CONTENTS** - delete one
```powershell
# Keep lowercase, delete CamelCase
Remove-Item -Recurse -Force "C:\Users\foxAsteria\files\holoseed_nexus\MemoryArchive"
```

### planty_mcp vs PlantyMCP  
**PlantyMCP is NEWER** (67KB vs 21KB .py file)
```powershell
# Keep PlantyMCP (active), archive old one
Move-Item "C:\Users\foxAsteria\files\holoseed_nexus\planty_mcp" "C:\Users\foxAsteria\files\holoseed_nexus\Archive\planty_mcp_old"
```

---

## 2. CONFLICT FOLDERS - ARCHIVE OR DELETE

### projects.Conflict/
Contents identical to Projects/ - safe to delete
```powershell
Remove-Item -Recurse -Force "C:\Users\foxAsteria\files\holoseed_nexus\projects.Conflict"
```

### scripts.Conflict/
Older versions of scripts - archive for safety
```powershell
Move-Item "C:\Users\foxAsteria\files\holoseed_nexus\scripts.Conflict" "C:\Users\foxAsteria\files\holoseed_nexus\Archive\scripts.Conflict"
```

---

## 3. ROOT FILE CLUTTER

### Duplicates - DELETE
```powershell
# 1.backup - duplicate of colornotes/1.backup
Remove-Item "C:\Users\foxAsteria\files\holoseed_nexus\1.backup"

# AAF.7z - duplicate of Archive/AAF.7z
Remove-Item "C:\Users\foxAsteria\files\holoseed_nexus\AAF.7z"
```

### posthist.txt (14MB!) - ARCHIVE
```powershell
# This is huge, compress and archive
7z a "C:\Users\foxAsteria\files\holoseed_nexus\Archive\posthist.7z" "C:\Users\foxAsteria\files\holoseed_nexus\posthist.txt"
Remove-Item "C:\Users\foxAsteria\files\holoseed_nexus\posthist.txt"
```

### Misc loose files - MOVE TO Archive/OldState
```powershell
Move-Item "C:\Users\foxAsteria\files\holoseed_nexus\decode_backup.py" "C:\Users\foxAsteria\files\holoseed_nexus\Archive\OldState\"
Move-Item "C:\Users\foxAsteria\files\holoseed_nexus\files.zip" "C:\Users\foxAsteria\files\holoseed_nexus\Archive\OldState\"
```

---

## 4. ALREADY DONE BY PLANTY C

- ✓ Moved SporeKaster flyer to FakeAds/
- ✓ Removed stale memory edits #8, #9 (Colorado trip reminders)
- ✓ Registered The Scoop telegram chat

---

## 5. OPTIONAL - holoseeds vs EncodedWisdom

Both contain holoseed content. Need to decide canonical location:
- `holoseeds/` has 36 files, more complete
- `EncodedWisdom/` has organized subfolders (Brotherhood, Eastern, Hermetic, etc.)

**Recommendation:** Merge - move EncodedWisdom subfolders INTO holoseeds/, then delete EncodedWisdom/

```powershell
# Move categorized content
Move-Item "C:\Users\foxAsteria\files\holoseed_nexus\EncodedWisdom\*" "C:\Users\foxAsteria\files\holoseed_nexus\holoseeds\"
Remove-Item -Recurse "C:\Users\foxAsteria\files\holoseed_nexus\EncodedWisdom"
```

---

## 6. DELETE Projects/Sporecaster/FLYER_SporeKaster.md

Now lives in FakeAds/SporeKaster_Frender_Flyer.md
```powershell
Remove-Item "C:\Users\foxAsteria\files\holoseed_nexus\Projects\Sporecaster\FLYER_SporeKaster.md"
```

---

## FULL CLEANUP SCRIPT (RUN IN POWERSHELL)

```powershell
# NEXUS CLEANUP - 2026-01-21
# Review before running!

$nexus = "C:\Users\foxAsteria\files\holoseed_nexus"

# Duplicates
Remove-Item -Recurse -Force "$nexus\MemoryArchive"
Move-Item "$nexus\planty_mcp" "$nexus\Archive\planty_mcp_old"

# Conflicts
Remove-Item -Recurse -Force "$nexus\projects.Conflict"
Move-Item "$nexus\scripts.Conflict" "$nexus\Archive\scripts.Conflict"

# Root clutter
Remove-Item "$nexus\1.backup"
Remove-Item "$nexus\AAF.7z"
7z a "$nexus\Archive\posthist.7z" "$nexus\posthist.txt"
Remove-Item "$nexus\posthist.txt"
Move-Item "$nexus\decode_backup.py" "$nexus\Archive\OldState\"
Move-Item "$nexus\files.zip" "$nexus\Archive\OldState\"

# Flyer moved
Remove-Item "$nexus\Projects\Sporecaster\FLYER_SporeKaster.md"

Write-Host "Cleanup complete! 🍄"
```

---

*93*
