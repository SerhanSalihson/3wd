# Power and Electronics BOM

This buying list captures the current 12S quadruped power plan. Exact fuse
values and cable lengths must be finalized from measured load current, motor
controller limits, cable routing, and the selected components' datasheets.

## Planned architecture

```text
12S LiPo (50.4 V maximum)
  -> main fuse beside the battery
  -> 500 A distribution block
      -> fused RO80/XDrive group A
      -> fused RO80/XDrive group B
      -> fused 48 V-to-12 V converter
          -> individually fused 12 V wiper motors
      -> fused electronics/Jetson converter
```

The distributor's 500 A rating is only its maximum carrying capacity. It does
not determine the main or branch fuse ratings.

## Buying list

| Qty | Item | Required specification | Status / sizing note |
| ---: | --- | --- | --- |
| 1 | 12S LiPo battery | 50.4 V fully charged; discharge rating and capacity suitable for the measured system load | Pack specification still to be confirmed |
| 1 | Main fuse holder | MEGA/AMG or ANL style; explicitly rated for at least 60 V DC; adequate interrupt rating for the battery | Mount as close to the battery positive terminal as practical |
| 2–3 | Main fuses | Same type as holder; include at least one spare | Start in the 80–100 A range with 16 mm² cable; use 100–125 A only if the selected cable and installation support it |
| 1 | Power distribution block | 500 A carrying rating; at least 60 V DC; covered, insulated terminals; studs compatible with selected lugs | The oversized current rating is acceptable |
| 2 | Motor-group fuse holders | At least 60 V DC; sized for the selected group cables and expected group current | One for each RO80/XDrive group |
| 2 sets | Motor-group fuses | At least 60 V DC; include one spare per rating | Choose from configured controller limits and group cable ampacity; do not assume the earlier 20–30 A per-controller estimate applies to an entire group |
| 1 | 48 V-to-12 V DC-DC converter | Input range includes the full 12S range, including 50.4 V; output power covers all 12 V loads and motor stall current | Converter model/power still to be confirmed |
| 1 | Converter-input fuse holder | At least 60 V DC | Install at the distribution end of the converter input cable |
| 2 | Converter-input fuses | Include one spare | Provisional range: 20–30 A; finalize from converter maximum input current and input cable |
| 1 | Electronics/Jetson DC-DC converter | Input range includes full 12S voltage; regulated output matches the exact Jetson and electronics requirements | Keep this rail separate from noisy motor loads |
| 1 | Electronics-input fuse holder | At least 60 V DC | Install at the distribution end of the input cable |
| 2 | Electronics-input fuses | Include one spare | Provisional range: 5–10 A; finalize from converter input current and cable |
| 1 per motor | 12 V motor fuse holder | Suitable for the 12 V wiper-motor circuit and measured stall current | Install on the 12 V side |
| 2 per rating | 12 V motor fuses | Include spares | Provisional range: 10–15 A per motor; finalize after measuring stall current |
| As measured | 16 mm² flexible copper cable, red and black | Voltage/temperature-rated insulation; short main battery runs | Current working choice for an approximately 80–100 A main feed |
| As measured | Branch cable in appropriate gauges and colors | Size each branch for its continuous current, routing, bundling, and temperature | Every branch fuse must protect the smallest downstream conductor |
| As required | Crimp lugs and terminals | Match conductor cross-section, stud diameter, and component terminals exactly | Do not trim strands to fit |
| As required | Adhesive-lined heat-shrink and insulating terminal covers | Voltage- and temperature-suitable | Cover every exposed high-current positive connection |
| As required | Cable sleeving, strain relief, clamps, and grommets | Abrasion- and temperature-resistant | Secure wiring against vibration and sharp chassis edges |
| 1 | High-current battery connector or service disconnect | At least 60 V DC and rated for the expected continuous current; touch-safe where possible | Must not be used to interrupt load unless explicitly rated to do so |
| 1 | Emergency power disconnect | DC-rated for the pack voltage and system current | Place where it can be reached without approaching moving legs |
| 1 set | Labels | Battery voltage, polarity, fuse ratings, and disconnect instructions | Label both ends of every major branch |

## Before ordering fixed fuse ratings

- Record the exact LiPo model, capacity, discharge rating, connector, and maximum
  short-circuit protection provided by the pack or BMS.
- Record the number and exact model of RO80/XDrive units and their configured
  continuous and peak current limits.
- Measure or obtain the stall current of every 12 V wiper motor.
- Confirm both DC-DC converters accept 50.4 V continuously, not merely a nominal
  48 V input.
- Measure every cable run and check ampacity using the cable maker's data for the
  actual insulation, bundling, ambient temperature, and routing.
- Select every fuse to protect the smallest conductor downstream. A device's
  current rating alone is not a fuse-sizing rule.
- Confirm every fuse and switch has a DC voltage rating and interrupt rating
  suitable for the battery. Automotive 32 V parts are not acceptable on 12S.
- Check connector, lug, fuse-holder, and busbar stud sizes before ordering.

## Procurement notes

Buy holders first only when their voltage, interrupt, stud, and cable-size
ratings are known. Buy fixed-value fuses after the current limits, converters,
motor stall currents, and cable ampacities are confirmed. Keep at least one
spare of every fuse value on the robot or in the field kit.

This document is a planning BOM, not a completed electrical safety review.
