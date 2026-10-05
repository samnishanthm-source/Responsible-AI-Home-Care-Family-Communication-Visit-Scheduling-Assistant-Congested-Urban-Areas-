# Live Traffic Disruption → Notification Cascade (Phase 2)

Simulated a sudden 'severe traffic' disruption event on 25 active visits and recomputed the Responsible AI pipeline for every active family recipient.

- Total recipients evaluated: 53
- Recipients whose message actually changed (re-notified): 33 (62.3%)
- Recipients NOT re-notified (message unchanged — avoids alert fatigue): 20

## Example Cascades

### Visit V1266
Confidence band: High → Low
- **F053** (renotify=True): "Your scheduled care visit is delayed. Expected arrival: 2026-09-28T12:05:00. Reason: Light traffic is affecting travel time." → "Your scheduled care visit is delayed. The arrival time is currently uncertain due to traffic conditions. Please contact the care coordinator for the latest update. Reason: Severe traffic is affecting travel time."

### Visit V1107
Confidence band: Low → Low
- **F249** (renotify=False): "The latest visit information could not be confirmed with confidence. Please contact the care coordinator for the most accurate update." → "The latest visit information could not be confirmed with confidence. Please contact the care coordinator for the most accurate update."
- **F250** (renotify=False): "The latest visit information could not be confirmed with confidence. Please contact the care coordinator for the most accurate update." → "The latest visit information could not be confirmed with confidence. Please contact the care coordinator for the most accurate update."
- **F251** (renotify=False): "You are not authorised to receive information about this visit. Please contact the care coordinator if you believe this is in error." → "You are not authorised to receive information about this visit. Please contact the care coordinator if you believe this is in error."

### Visit V1382
Confidence band: High → Low
- **F006** (renotify=True): "Reason: Light traffic is affecting travel time. No medical information is included in this update." → "Reason: Severe traffic is affecting travel time. No medical information is included in this update."
- **F007** (renotify=True): "Reason: Light traffic is affecting travel time. No medical information is included in this update." → "Reason: Severe traffic is affecting travel time. No medical information is included in this update."
- **F008** (renotify=True): "Reason: Light traffic is affecting travel time. No medical information is included in this update." → "Reason: Severe traffic is affecting travel time. No medical information is included in this update."