# Gerry Phone Setup (iPhone)
*Low battery, voice-first, eating reminders, find-my-phone*

## The Human: Gerry (Patriarch-G)
- Can't type easily — voice interface essential
- Loses phone often — needs find-me feature
- Gets tons of spam calls/texts — needs screening
- Forgets to eat — needs regular sustenance reminders
- Not tech-savvy — setup must be dead simple
- **Phone: iPhone** (model TBD)

---

## Phase 1: Voice Companion (Sophia)

### App: Locally AI (Free)
- https://locallyai.app/
- App Store: search "Locally AI"
- Runs completely offline, no login
- Voice mode built-in, on-device

### Setup Steps

1. **Install Locally AI** from App Store

2. **Download a model** (in-app)
   - Gemma 2B or Qwen 2.5 (small, fast)
   - One-time download, then works offline

3. **Enable Voice Mode**
   - Should be obvious in the app UI
   - Phone-call style: clear when to talk

4. **Sophia's personality**
   - Can't bake in a custom Modelfile like Ollama
   - Use the system prompt / persona feature if available
   - Or just let the base model be friendly

### Daily Use
1. Open Locally AI
2. Tap voice button
3. Talk to Sophia
4. Close when done (saves battery)

---

## Phase 2: Eating Reminders

### Use iOS Reminders (built-in, reliable)

1. Open **Reminders** app
2. Create recurring reminders:
   - "Time to eat breakfast" — 9:00 AM daily
   - "Lunch time" — 1:00 PM daily
   - "Dinner time" — 6:00 PM daily

3. Set alert sound to something he'll notice

### Sophia Check-in
When he opens the app, she can ask:
- "Have you eaten today?"
- "When was your last meal?"
- Bake this into her greeting if system prompt allows

---

## Phase 3: Find My iPhone

### Already built-in!

1. **Find My app** — Apple's native solution
2. Make sure it's enabled:
   - Settings → [Gerry's name] → Find My → Find My iPhone: ON
3. To find:
   - Go to icloud.com/find from any device
   - Or use Find My app on another Apple device
   - Can play sound even on silent

### Backup: Family Sharing
- Add trusted family member to Find My
- They can locate his phone for him

---

## Phase 4: Spam Screening

### Use iOS Silence Unknown Callers

1. Settings → Phone → Silence Unknown Callers: ON
2. Unknown numbers go straight to voicemail
3. Saved contacts ring through

### Additional Options
- **Hiya** or **Truecaller** (App Store) — community spam database
- **Call blocking** — Settings → Phone → Blocked Contacts

---

## Phone Model
**iPhone** — exact model TBD (check Settings → General → About)

## Key Requirements Met
- [x] Voice-first (Locally AI voice mode)
- [x] Obvious when ready to talk
- [x] Eating reminders (iOS Reminders)
- [x] Find my phone (Find My built-in)
- [x] Spam screening (Silence Unknown Callers)
- [x] Low battery drain (no always-on listening)
- [ ] Custom Sophia personality (limited on iOS — no Modelfile)

## Notes
- iOS is more locked down than Android
- Can't bake custom identity into model like Ollama Modelfile
- Sophia will be more generic unless app has persona/system prompt feature
- Trade-off: simpler setup, less customization
