# Phone Backup Checklist
> Before any destructive operation (flash, wipe, reset)

## MUST Backup

### Media
- [ ] DCIM/ (photos, videos)
- [ ] Downloads/
- [ ] Screenshots/
- [ ] WhatsApp/Media/ (if applicable)

### Data
- [ ] Contacts → export to VCF or sync to account
- [ ] SMS/MMS → use SMS Backup & Restore app
- [ ] Call history
- [ ] Browser bookmarks (each browser separately)
- [ ] Browser saved passwords (export or sync)

### Apps
- [ ] List installed apps: `adb shell pm list packages -3 > app_list.txt`
- [ ] App-specific data (check each critical app)
- [ ] 2FA app backup codes (Aegis export, etc.)
- [ ] Any local-only app data

### System
- [ ] WiFi passwords (if rooted: /data/misc/wifi/)
- [ ] Custom ringtones/notifications
- [ ] Wallpapers

## Verify Before Proceeding

```bash
# Check backup location has expected files
ls -la ~/phone_backup/

# Verify file counts
find ~/phone_backup/ -type f | wc -l

# Check total size makes sense
du -sh ~/phone_backup/
```

## What's NOT Being Backed Up

**ALWAYS STATE EXPLICITLY** what is NOT included:
- Cloud-synced data (Google, Samsung Cloud) — assumed safe
- Apps that will reinstall from store
- Specific apps: [list them]

## Post-Backup Verification

- [ ] Can you open a photo from backup?
- [ ] Is contacts VCF readable?
- [ ] Are SMS messages in the backup file?
- [ ] Did you note what's NOT backed up?

---

*The phone backup on 2026-02-03 missed contacts, SMS, browser data, app configs. This checklist exists because of that.*
