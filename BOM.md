# Quadruped Electrical BOM

This is the reference buying list for a **12-DOF quadruped** built around the
existing 12S LiPo, four CubeMars RO80 knee motors with MKS XDrive Mini
controllers, eight non-backdriveable 12 V brushed geared motors, and a Jetson
Orin Nano Super.

The diagram that inspired this list shows more brushed motors than a normal
12-DOF build. This BOM deliberately uses **4 RO80 + 8 brushed motors = 12
joints**.

## Design basis

| Load | Quantity | Planning value |
| --- | ---: | ---: |
| CubeMars RO80 | 4 | 48 V, about 490 W rated each |
| MKS XDrive Mini | 4 | One controller per RO80 |
| Brushed geared motor | 8 | 12 V, 10 A nominal and non-backdriveable; stall current still must be measured |
| Jetson Orin Nano Super developer kit | 1 | 19 V barrel input; 25 W Super power mode |
| Existing LiPo | 1 | 12S, 44.4 V nominal, 50.4 V fully charged |

The nominal loads total about 3.0 kW. That is roughly 68 A from a 44.4 V pack
before converter and wiring losses, so plan around **75–85 A continuous** and
larger short peaks. The 125 A main fuse is not permission to run every joint at
maximum current simultaneously: controller current limits are required.

## Electrical architecture

```text
Existing 12S LiPo
  -> 125 A Class-T fuse
  -> SB120 service connector
  +-> protected always-on low-power rails
  |    +-> battery monitor/BMS
  |    +-> 12 V safety rail -> precharge controller + contactor coil
  |    +-> 19 V rail -> Jetson Orin Nano Super
  |    `-> 5 V rail -> STM32 boards and sensors
  `-> precharge circuit -> normally-open main contactor -> 48 V motion bus
       +-> 4 x 40 A fused MKS XDrive Mini -> 4 x RO80
       `-> 60 A fused bidirectional 48/12 V converter -> 12 V motor bus
            -> 4 x 30 A fused dual H-bridge -> 8 x 15 A fused brushed motor
```

The emergency stop opens the motion-bus contactor while the Jetson, BMS, and
safety controller remain powered. The service connector is the full isolation
point. Do not use the connector or E-stop as a routine switch under load.

## A. Reuse and validate first

| Qty | Item | Requirement | Action |
| ---: | --- | --- | --- |
| 1 | Existing 12S LiPo | 50.4 V maximum; at least 100 A stated continuous discharge and about 150 A burst for this configuration | Reuse only after the battery checks below |
| 4 | CubeMars RO80 | 48 V / KV105 version assumed | Reuse if already owned; otherwise buy |
| 4 | MKS XDrive Mini | 12–56 V input; CAN control | Reuse if already owned; otherwise buy |
| 1 | Jetson Orin Nano Super developer kit | Complete carrier-board kit, not the bare module | Reuse if already owned; otherwise buy |

### Existing-battery hard gate

Do not connect the old pack if it is swollen, punctured, water-damaged, has
corroded leads, damaged balance wiring, or a cell that will not balance. Before
commissioning, record its model, capacity, C rating, age, connector, individual
cell voltages, and internal resistance. After balancing and resting, the cells
should be closely matched; investigate a spread above about 30 mV rather than
forcing the pack into service.

This design also requires the pack to accept regenerative charge current. Do
initial tests below full charge and configure the BMS/converter so regeneration
is stopped or dumped before any cell reaches its maximum voltage.

## B. Battery protection, isolation, and precharge

| Qty | Buy | Selected specification / example | Notes |
| ---: | --- | --- | --- |
| 1 | Main fuse | [Blue Sea 5113 Class-T, 125 A](https://www.bluesea.com/products/5113/Fuse_A3T___Class_T_125_Amp), 125 VDC, 20 kA interrupt rating | Place within about 200 mm of battery positive |
| 1 | Main fuse holder | [Blue Sea 5007100](https://www.bluesea.com/products/5007100/Class_T_Fuse_Block_with_Insulating_Cover_-_110_to_200A), for 110–200 A Class-T fuses | Covered holder; the visually similar 5502 is for larger 225–400 A fuses |
| 1 | Service connector | [Anderson SB120](https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/DS-SB120.pdf), red housing, contacts matched to 25 mm² / 4 AWG cable | Buy one complete mating pair plus two spare contacts |
| 1 | Main contactor | [Sensata GIGAVAC GV21](https://www.sensata.com/sites/default/files/a/sensata-gigavac-gv21-sereies-800v-contactors-datasheet.pdf), normally open, 12 V coil, auxiliary-contact option | Confirm the exact 12 V-coil suffix and cable termination before ordering |
| 1 | Precharge controller | [EV Power REL-PRECHG](https://www.ev-power.com.au/product/rel-prechg180/) or equivalent monitored precharge controller | Prevents the controller/DC-link capacitors from welding the contactor |
| 1 | Latching E-stop | [Schneider Harmony XB5AS8442](https://www.se.com/us/en/product/XB5AS8442/) plus one ZBE102 NC contact block, giving **2 NC contacts** | One contact in the contactor-enable chain; one to the safety controller |
| 1 | Safety-rail converter | [Mean Well RSD-30L-12](https://www.meanwell.com/Upload/PDF/RSD-30/RSD-30-spec.pdf), 18–72 V input, 12 V / 2.5 A output | Powers precharge/controller and the 12 V contactor coil |
| 1 | Battery monitor/BMS | [Orion Jr 2, 16-cell CAN version](https://www.orionbms.com/products/orion-jr-2-bms/) with a 175–200 A current sensor | Required if the existing pack has no trusted cell-level BMS; it does not replace the main fuse or contactor |
| 3 | Auxiliary fuse holders | Touch-safe 10x38 mm DIN holders, vibration-secured, rated at least 60 VDC | For BMS, safety converter, and Jetson converter feeds |
| 2 each | Auxiliary DC fuses | 1 A, 2 A, and 5 A, 10x38 mm, explicitly DC-rated above 50.4 V | One installed and one spare per rating |
| 1 | Insulated auxiliary enclosure | DIN rail, finger-safe cover, strain relief | Houses the small pre-contactor fuses; no exposed live metal |

If the old battery already contains a documented BMS with cell-voltage,
temperature, discharge-enable, and charge-enable protection, the Orion Jr 2 is
not duplicated. Verify that the existing BMS can command the contactor and that
its current sensor and limits suit this build.

## C. 48 V motion bus and RO80 branches

| Qty | Buy | Selected specification / example | Notes |
| ---: | --- | --- | --- |
| 1 | Covered 48 V PDM | [Littelfuse LX Series 880089/880089S](https://www.littelfuse.com/assetdocs/lx-datasheet?assetguid=9d63743d-aa43-4cfa-b82a-7828d3b17ecf), 60 VDC | Four MIDI positions feed the four XDrives; common negative return is included |
| 4 + 2 spare | XDrive branch fuse | [Littelfuse MIDI HP70V 4998040.M-M6](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-4998-midihp70v?assetguid=b72fcd7a-c66d-4916-844c-ac55ebed196c), 40 A / 70 VDC | One per XDrive; do not substitute ordinary 32 V MIDI fuses |
| 4 | MKS XDrive Mini | [Makerbase MKS XDrive Mini](https://github.com/makerbase-mks/ODrive-MKS) | One per RO80; use CAN and independently assigned node IDs |
| 4 | Brake resistor | 2 ohm, 100 W aluminum-housed, pulse-rated | One per XDrive AUX/brake output; mount to grounded metal away from battery and wiring |
| 4 | RO80 motor/encoder harness | Three phase conductors plus encoder wiring, locking connectors | Keep encoder wiring separated from phase leads |
| 1 set | CAN trunk parts | 120 ohm twisted pair, locking tees/connectors, two 120 ohm terminators | Terminate only at the two physical ends of the bus |

Initial conservative XDrive limits are **15–20 A DC-bus current continuous and
30 A peak per controller**. Tune torque/phase-current limits from the RO80 data
and thermal tests; phase current is not the same as battery-bus current.

MKS XDrive Mini firmware and configuration differ from a standard ODrive. With
multiple boards, assign every real axis a unique CAN node ID and move the unused
Axis1/ghost node to an unused ID such as 63. Do not flash stock ODrive firmware
without confirming board compatibility. See the
[community XDrive Mini guide](https://github.com/justlovescience/MKS-XDRIVE-MINI)
for board-specific setup details.

## D. 12 V brushed-motor system

| Qty | Buy | Selected specification / example | Notes |
| ---: | --- | --- | --- |
| 1 | Bidirectional 48/12 V converter | [Annren ATTD1K5-48B12N](https://www.annren.com/ec99/rwd1259/product.asp?prodid=bi-directional-1k5w), 30–60 V input, 1.5 kW, CAN | Order only with a supplier-confirmed 12.0–12.6 V motor-bus setpoint and charge-current control compatible with the BMS |
| 1 | Converter-input fuse holder | [Littelfuse MIDI Flex 04981038HXFC](https://www.littelfuse.com/assetdocs/midi-flex-datasheet?assetguid=49f6ff28-27e0-4fd5-b3d0-745c1502e03a), 58 VDC | Install at the 48 V PDM end of the input cable |
| 1 + 1 spare | Converter-input fuse | Littelfuse MIDI HP70V, 60 A / 70 VDC | Protects 10 mm² converter-input wiring |
| 1 | 12 V main fuse and holder | 125 A MEGA/AMG, at least 32 VDC, covered | Install at the converter output/bidirectional port |
| 1 | Positive busbar | Covered copper busbar, at least 150 A / 32 VDC | Feeds four driver branches |
| 1 | Negative busbar | [Blue Sea 2301](https://www.bluesea.com/products/2301/BusBar_-_10_Gang_Common_150A), 150 A | Star-return the four drivers to this bar |
| 2 | 12 V fuse block | [Blue Sea 5025](https://www.bluesea.com/products/5025), 6 circuits, 100 A block / 30 A circuit | Split the four drivers across two blocks; feed each block through its own 60 A fuse |
| 2 + 2 spare | Fuse-block feed fuse and holder | 60 A MIDI/MEGA, at least 32 VDC, covered | One between the positive busbar and each 100 A fuse block |
| 4 + 2 spare | Driver-input fuse | 30 A ATO/ATC, 32 VDC | One per dual driver |
| 4 | Dual brushed-motor driver | [Cytron MDDS30](https://www.cytron.io/p-30amp-7v-35v-smartdrive-dc-motor-driver-2-channels), 7–35 V, 30 A continuous per channel | One board per leg, two motors per board |
| 8 + 4 spare | Motor fuse and sealed holder | 15 A ATO/ATC, 32 VDC | Put one fuse in one lead of each reversible motor circuit |
| 8 | Joint encoder | AS5047P or AS5048A magnetic encoder assembly plus diametric magnet | Omit only where a motor/joint already has a usable absolute encoder |
| 8 | Brushed geared motor | Existing non-backdriveable 12 V / 10 A unit, mechanically suitable for joint load | Confirm that 10 A is nominal, not stall current |

The selected converter is bidirectional because the MDDS30 performs
regenerative braking. Cytron explicitly warns that a normal switching supply
which cannot absorb returned energy can be damaged or overvoltage the bus.
Do **not** substitute a generic unidirectional 48→12 V converter unless the 12 V
rail gains a correctly engineered buffer battery or active shunt/dump load.

The motors' non-backdriveable gearboxes greatly reduce regeneration caused by
an external load moving a joint. They do not eliminate energy returned by the
spinning motor rotor during commanded deceleration, reversal, or active
braking, so non-backdriveability is not used as the bus overvoltage protection.

The converter's public listing shows a nominal 14.5 V configuration. That is
too high to assume safe for unknown 12 V motors, so a written supplier
confirmation of the requested voltage range, regenerative direction, CAN
commands, current limits, and fault behavior is a procurement gate.

## E. Jetson, low-voltage control, and CAN

| Qty | Buy | Selected specification / example | Notes |
| ---: | --- | --- | --- |
| 1 | Jetson supply | [Victron Orion-Tr 48/24-5 Isolated](https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-DC-DC-converters-isolated-100-250-400W-EN.pdf), 32–70 V input, adjustable 18–30 V output | Set and meter-check **19.0 V before connecting** the Jetson barrel jack |
| 1 | Jetson power lead | Correct center-positive barrel plug, locking/strain-relieved at the robot harness | Add a 4 A output fuse; verify polarity twice |
| 1 | Logic converter | Mean Well RSD-30L-5, 18–72 V input, 5 V / 6 A output | Powers leg controllers and sensors, not motors |
| 4 | Leg controller | STM32 NUCLEO-G474RE or a derived protected board | One per leg: reads two brushed-joint encoders and commands one MDDS30 |
| 4 | CAN transceiver | 3.3 V high-speed CAN module based on SN65HVD230 or equivalent | Nucleo MCU has the controller but still needs a physical-layer transceiver |
| 1 | Jetson CAN adapter | Isolated USB-to-CAN adapter such as CANable Pro | Connects Jetson control software to the robot CAN trunk |
| 1 | Powered USB hub, optional | 19 V/5 V-compatible, locking power input | Only if cameras and other USB devices exceed Jetson port budget |
| As needed | Sensors | IMU, foot/contact sensors, limit/reference switches | Choose electrical interfaces before final harness manufacture |

NVIDIA specifies a 19 V barrel input for the developer kit, so the Jetson does
not share the high-current 12 V motor rail. The isolated converter also reduces
motor-noise coupling into the computer.

## F. Cable, terminals, and mechanical electrical hardware

Lengths depend on the CAD routing; measure the chassis and add 15–20% service
loop before ordering. Use fine-strand copper cable with documented temperature
and ampacity ratings.

| Circuit | Recommended starting cable | Fuse |
| --- | --- | ---: |
| Battery, main fuse, contactor, 48 V PDM | 25 mm² / 4 AWG red and black | 125 A Class-T |
| Each XDrive branch | 6 mm² / 10 AWG | 40 A MIDI HP70V |
| 48 V side of motor converter | 10 mm² / 8 AWG | 60 A MIDI HP70V |
| 12 V converter-to-bus wiring | 25 mm² / 4 AWG | 125 A MEGA/AMG |
| Each 12 V fuse-block feed | 10 mm² / 8 AWG | 60 A MIDI/MEGA |
| Each MDDS30 feed | 4 mm² / 12 AWG | 30 A ATO/ATC |
| Each brushed motor lead | 2.5 mm² / 14 AWG | 15 A ATO/ATC |
| Jetson converter input | 1.5 mm² / 16 AWG | 5 A DC auxiliary fuse |
| Safety and logic converter inputs | 1.0–1.5 mm² / 18–16 AWG | 2–3 A DC auxiliary fuse |

Also buy:

- Tinned-copper lugs matched exactly to every cable cross-section and stud size.
- A ratcheting hex crimper sized for the selected lugs, plus a pull-test sample
  allowance.
- Adhesive-lined heat-shrink in red, black, and branch-identification colors.
- Insulated terminal boots, P-clamps, braided sleeving, bulkhead grommets, and
  strain reliefs.
- Locking signal connectors, twisted-pair CAN cable, shielded encoder cable,
  and spare crimp contacts.
- Flame-resistant covered enclosures for the PDM, auxiliary fuses, and 12 V
  distribution.
- Labels for both ends of every cable and a fuse-rating label inside each cover.
- One spare main fuse, two spare fuses of every branch value, a contactor, and
  one spare XDrive and MDDS30 for field repair.

Cable sizes above are starting values for short chassis runs. Final acceptance
requires checking the chosen cable maker's ampacity and voltage-drop data for
the real length, insulation, bundling, ambient temperature, and motion/flexing.
Every fuse must protect the smallest downstream conductor.

## G. Bring-up sequence

1. Inspect and characterize the old 12S pack; do not proceed if it fails the
   battery hard gate.
2. Assemble and insulation-test the fuse, service disconnect, precharge, and
   contactor section with no controllers attached.
3. Set the Jetson converter to 19.0 V and verify the 12 V and 5 V rails with
   dummy loads before connecting electronics.
4. Bring up one XDrive/RO80 at low current. Verify encoder direction, motor
   direction, CAN ID, brake-resistor action, E-stop, and contactor opening.
5. Repeat one branch at a time; never attach four unconfigured XDrives to CAN.
6. Bench-test one MDDS30 and two motors. Log running, acceleration, stall, and
   regenerative current before accepting the 15 A/30 A fuse values.
7. Verify that the bidirectional converter obeys BMS charge limits and that a
   full battery cannot drive either DC bus above component ratings.
8. Perform a restrained, legs-off-ground test, then a tethered low-torque test.
   Record cable, connector, fuse-holder, converter, driver, and motor
   temperatures before raising current limits.

Never solve a nuisance-blown fuse by fitting a larger one without new current,
cable-ampacity, connector, and thermal evidence.

## Primary-source references

- [CubeMars RO80 product data](https://store.cubemars.com/products/ro80)
- [MKS ODrive/XDrive repository](https://github.com/makerbase-mks/ODrive-MKS)
- [NVIDIA Jetson Orin Nano Super announcement and 25 W mode](https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/)
- [NVIDIA Jetson Orin Nano developer-kit getting started guide](https://developer.nvidia.com/embedded/learn/get-started-jetson-orin-nano-devkit)
- [Sensata precharge application note](https://www.sensata.com/resources/application-note-pre-charge-circuits-and-capacitors)
- [Cytron MDDS30 documentation](https://www.cytron.io/p-30amp-7v-35v-smartdrive-dc-motor-driver-2-channels)
- [Orion Jr 2 specifications](https://www.orionbms.com/downloads/documents/orionjr2_specifications.pdf)

This BOM is a buildable reference architecture, not a substitute for validation
by a qualified power-electronics engineer. The remaining hard unknown is the
old battery's real condition/rating and the exact brushed-motor stall current.
