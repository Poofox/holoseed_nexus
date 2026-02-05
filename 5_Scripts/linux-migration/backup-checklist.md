# Linux Migration Backup Checklist
> Run these from Windows before wiping. Target: external SSD mounted at /mnt/backup (or E:\backup on Windows)

## Pre-Flight
```bash
# Set your backup destination
BACKUP_DEST="/e/linux-migration-backup"
mkdir -p "$BACKUP_DEST"
```

## CRITICAL (Must Have)

### 1. Holoseed Nexus (THE SEED)
```bash
rsync -avh --progress ~/files/holoseed_nexus/ "$BACKUP_DEST/holoseed_nexus/"
# Size: ~4GB
```

### 2. Phone Backup
```bash
rsync -avh --progress ~/phone_backup/ "$BACKUP_DEST/phone_backup/"
# Size: ~10GB
```

### 3. Phone ROM (SM-G973N Recovery)
```bash
rsync -avh --progress ~/phone_rom/ "$BACKUP_DEST/phone_rom/"
# Size: ~5.1GB
```

### 4. SSH Keys
```bash
rsync -avh --progress ~/.ssh/ "$BACKUP_DEST/.ssh/"
chmod 700 "$BACKUP_DEST/.ssh"
# Size: small, but CRITICAL
```

### 5. Identity Files
```bash
cp ~/CLAUDE.md "$BACKUP_DEST/"
cp ~/CLAUDE.md.sha256 "$BACKUP_DEST/"
```

### 6. Claude CLI Config
```bash
rsync -avh --progress ~/.claude/ "$BACKUP_DEST/.claude/"
# Size: ~768MB
```

## HIGH PRIORITY

### 7. REAPER Configuration
```bash
rsync -avh --progress ~/AppData/Roaming/REAPER/ "$BACKUP_DEST/REAPER/"
# Size: ~3.1GB - scripts, routing templates, FX chains
```

### 8. Firefox Profile
```bash
rsync -avh --progress ~/AppData/Roaming/Mozilla/ "$BACKUP_DEST/Mozilla/"
# Size: ~776MB - bookmarks, extensions, sessions
```

### 9. Custom Scripts (bin)
```bash
# Exclude gradle (can re-download)
rsync -avh --progress --exclude='gradle*' ~/bin/ "$BACKUP_DEST/bin/"
# Size: ~40MB
```

### 10. Shell Configs
```bash
cp ~/.bashrc "$BACKUP_DEST/"
cp ~/.bash_profile "$BACKUP_DEST/"
cp ~/.profile "$BACKUP_DEST/" 2>/dev/null || true
```

### 11. WezTerm Config
```bash
rsync -avh --progress ~/.config/wezterm/ "$BACKUP_DEST/.config/wezterm/"
```

### 12. Git Config
```bash
cp ~/.gitconfig "$BACKUP_DEST/"
```

## MEDIUM PRIORITY

### 13. Documents (Audio Production Configs)
```bash
# This is big - do selectively if space is tight
rsync -avh --progress ~/Documents/ "$BACKUP_DEST/Documents/"
# Size: ~70GB
```

### 14. Signal Messages (if not cloud synced)
```bash
rsync -avh --progress ~/AppData/Roaming/Signal/ "$BACKUP_DEST/Signal/"
# Size: ~156MB
```

### 15. LibreChat Config
```bash
# Just the config, not the whole docker volume
cp ~/librechat/librechat.yaml "$BACKUP_DEST/"
cp ~/librechat/docker-compose.override.yml "$BACKUP_DEST/" 2>/dev/null || true
cp ~/librechat/.env "$BACKUP_DEST/librechat.env" 2>/dev/null || true
```

## SKIP (Already Backed Up / Regenerable)

- `~/Resilio Sync/` - synced elsewhere
- A: drive (AUDIO) - Resilio synced
- `~/AppData/Local/Docker/` - rebuild on Linux
- `~/AppData/Local/Ollama/` - re-pull models
- `~/Downloads/` - installers, re-download
- Discord/Spotify/Zoom caches

---

## Verification Checklist

After backup completes:

- [ ] `ls -la "$BACKUP_DEST/holoseed_nexus/"` shows content
- [ ] `ls -la "$BACKUP_DEST/.ssh/"` shows keys
- [ ] `cat "$BACKUP_DEST/CLAUDE.md"` shows identity
- [ ] `ls -la "$BACKUP_DEST/REAPER/Scripts/"` shows Lua scripts
- [ ] `ls -la "$BACKUP_DEST/Mozilla/"` shows Firefox folder

## Space Summary

| Category | Size |
|----------|------|
| Critical | ~20GB |
| High | ~4GB |
| Medium | ~70GB |
| **Total** | **~94GB** |

Make sure your backup drive has at least 100GB free.

---

## One-Liner (Full Critical + High)

```bash
BACKUP_DEST="/e/linux-migration-backup"
mkdir -p "$BACKUP_DEST/.config" "$BACKUP_DEST/.ssh"

rsync -avh --progress \
  ~/files/holoseed_nexus/ "$BACKUP_DEST/holoseed_nexus/" && \
rsync -avh --progress \
  ~/phone_backup/ "$BACKUP_DEST/phone_backup/" && \
rsync -avh --progress \
  ~/phone_rom/ "$BACKUP_DEST/phone_rom/" && \
rsync -avh --progress \
  ~/.ssh/ "$BACKUP_DEST/.ssh/" && \
rsync -avh --progress \
  ~/.claude/ "$BACKUP_DEST/.claude/" && \
rsync -avh --progress \
  ~/AppData/Roaming/REAPER/ "$BACKUP_DEST/REAPER/" && \
rsync -avh --progress \
  ~/AppData/Roaming/Mozilla/ "$BACKUP_DEST/Mozilla/" && \
rsync -avh --progress --exclude='gradle*' \
  ~/bin/ "$BACKUP_DEST/bin/" && \
rsync -avh --progress \
  ~/.config/wezterm/ "$BACKUP_DEST/.config/wezterm/" && \
cp ~/CLAUDE.md ~/CLAUDE.md.sha256 ~/.bashrc ~/.bash_profile ~/.gitconfig "$BACKUP_DEST/"

echo "Backup complete!"
```
