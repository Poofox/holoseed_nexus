#!/data/data/com.termux/files/usr/bin/bash
# Brightness daemon - full on power, dim on battery
# Respects manual changes until state change
# Run with: nohup ~/brightness_daemon.sh &

BRIGHT_PLUGGED=255    # Full brightness when charging
BRIGHT_BATTERY=25     # Dim when on battery

last_state=""
manual_override=false

get_power_state() {
    dumpsys battery | grep -q "AC powered: true\|USB powered: true" && echo "plugged" || echo "battery"
}

set_brightness() {
    settings put system screen_brightness "$1"
    settings put system screen_brightness_mode 0  # Manual mode
}

echo "🔆 Brightness daemon started"
echo "   Plugged: $BRIGHT_PLUGGED | Battery: $BRIGHT_BATTERY"

while true; do
    state=$(get_power_state)

    if [ "$state" != "$last_state" ]; then
        echo "Power state changed: $state"
        if [ "$state" = "plugged" ]; then
            set_brightness $BRIGHT_PLUGGED
            echo "→ Brightness: FULL"
        else
            set_brightness $BRIGHT_BATTERY
            echo "→ Brightness: DIM"
        fi
        last_state="$state"
    fi

    sleep 10
done
