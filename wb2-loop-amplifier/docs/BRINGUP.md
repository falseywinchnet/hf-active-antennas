# WB-2 first-board bring-up procedure (rev B, after review-08)

Claude, 2026-10-01, for the board signed in review-07 (SHA-256 `877c82ec…`).

The test pads are listed in `pcb/kicad/tp_table.md` and mapped in `pcb/kicad/renders/tp_map.png` (`fab/plots/wb2-testpoints.pdf`). Coordinates are mm, origin at the board's bottom-left.

**Record with every RF result:** the C1 population (15 pF baseline or 33 pF option), the feed (jack or coax), the input condition, the output condition, and the probe and its loading.

## Ground and probe rules

- **System GND** means a TPG pad, J3, or the J4 braid. Instrument grounds connect only to system GND.
- **Not ground nodes:**
  - **RTN3:** U3's exposed pad and the R35/R36/C23 returns.
  - **CBL_GND:** the J5 sleeve.
  - **GCT:** TP3.
  - **The loop terminals** J1 and J2.
- **No clip leads to those nodes.** Never attach a grounded scope or analyser lead, or a clip ground, to any of them. A DMM may read them; a grounded instrument return must not.
- **The input is floating.** Drive it only from an **isolated** differential source, such as a battery-powered generator or a generator through an isolation or balun transformer. A differential probe does not isolate a grounded generator.
- **Single-ended RF probing:** spring-tip ground on the adjacent TPG, never a clip lead.
- **Probe loading:** record the probe's capacitance. A "high-impedance" probe can damp, or create, a VHF mode.

## Nominal DC values

From `python wb2.py op`: nominal devices, 27 °C, model values with no tolerance. With the extracted copper the voltages move by less than 1 mV.

| Pad | Net | Jack 12 V | Coax 12 V |
|---|---|---|---|
| TP17 (80.0, 20.6) | VDD | 11.11 V | 10.35 V |
| TP14 (61.0, 8.85) | REF | 0.498 V | 0.498 V |
| R4 pad 1 (62.4, 38.0) | GBIAS | 1.497 V | 1.497 V |
| TP15 (72.2, 25.8) | VBB | 5.01 V | 4.66 V |
| TP10 / TP11 | ESA / ESB | 0.498 V each | 0.498 V each |
| TP8 / TP9 | XA / XB | 1.366 V each | 1.363 V each |
| TP4 / TP5 | SA / SB | 1.687 V | 1.684 V |
| Q1–Q8 drain pads | DA / DB | 5.21 V | 4.87 V |
| TP12 / TP13 | CA / CB | 11.03 V | 10.28 V |
| TP16 | T2CT | 11.04 V | 10.28 V |
| — | supply current | 75.1 mA | 74.5 mA |

- **Sink current:** V(ESA)/14.7 Ω ≈ 33.9 mA is the emitter/resistor current; the collector current is lower by the base current. Use the measured value of R5/R6.
- **V_DS:** input/cascode V_DS is about 3.5 / 5.8 V on the jack feed and 3.2 / 5.4 V on the coax feed. Sink V_CE is about 0.87 V.
- **Stop criteria for the first board:**
  - supply current outside 65–90 mA;
  - the two sink currents differing by more than 2 mA;
  - VBB, REF or GBIAS more than 5 % from nominal.

## 0. Assembly inspection (unpowered)

1. **Fit and orientation:**
   - **D7/D8 or D12/D13:** fit D7/D8 (BAV99), never both pairs. D12/D13 are DNP.
   - **Transformers:** T1–T4 orientation per the assembly drawing, pin-1 dots.
   - **U3:** exposed pad soldered.
   - **C19:** polarity.
   - **C1:** record the value fitted.
2. **Remove C3 and C4** (or lift one end of each) for step 1 phasing.
3. **DMM checks:**
   - **J1–J2:** a fraction of an ohm (the loop windings).
   - **J1 or J2 to GND:** about **50 kΩ**. R1 and R2 are effectively in parallel through the windings; protection leakage and DMM polarity shift the reading.
   - **VDD to GND:** not a short; the C19 charge ramp is normal.
   - **RTN3 (C23 pad 2) to GND:** not a short. Internal circuitry gives a finite reading.
   - **J5 sleeve:** inspect the harness so that the sleeve reaches the board only at the J5 pad 2 landing. A low reading alone can't tell the L5 winding path from an unintended bypass.

## 1. Transformer phasing (power off, C3/C4 removed)

**Why:** review-01 procedure, repeated because of T4's double end-exchange. Wrong phasing still gives a 3× current ratio on a sweep but oscillates at about 2.8 MHz, so a sweep is no check.

1. Drive J1–J2 from an **isolated** source, for example 100 mV at 1 MHz, well below the BAV99 clamp. Measure the actual LA−LB differentially as the reference.
2. **GA−GCT** (TP1−TP3), differential: the same sign as LA−LB, about 2× the amplitude.
3. **GB−GCT** (TP2−TP3), differential: the opposite sign, about 2×.
4. **SAK (TP6) to system GND:** opposite in sign to LA−LB, about 1/6 of the amplitude.
5. **SBK (TP7) to system GND:** the same sign as LA−LB, about 1/6.
6. If any sign or ratio is wrong, stop. Do not fit C3/C4.

## 2. Current-limited power-up, nominal DC only

1. **Supply:** fit C3/C4. Bench supply on J5 at 12 V with a 120 mA limit; raise slowly from 0 V.
   - Watch whether the supply sits in current limit during C19 charging; that is normal for a short time.
   - Classify by the **settled** current: about 75 mA.
   - **Input and output:** terminate J1–J2 in a passive balanced 50 Ω (isolated) and the output in 75 Ω.
2. **Measure** the DC table at 12 V. Apply the stop criteria.

## 3. First stability check (immediately after step 2, before any other test)

1. **Spectrum analyser** on the output through a 75→50 Ω pad, or a transformer with known loss.
   - Search **100 kHz–300 MHz** at a stated sensitivity, then zoom with narrow RBW wherever there is any spur.
   - **Fixed-frequency spurs count.** Self-generated oscillation need not move with loop or cable changes.
   - Look particularly, but **not only**, at **40–60 MHz** (T1-leakage mode, see README "Layout back-annotation") and **1.5–3 MHz** (T2 magnetising mode, output open).
2. **Open-output check.** Disconnect the analyser and any load, so the output is genuinely open.
   - Watch **CA/CB (TP12/TP13, at (71, 36) / (71, 40))** with a characterised low-capacitance probe, differentially if possible, or with a calibrated non-contact pickup.
   - **TP16 (T2CT) is not a valid monitor:** it is near a virtual ground for the balanced mode.
3. **Discriminating oscillation from reception:** with an antenna connected, external stations are expected. Use passive dummy antennas, and a defined, repeatable perturbation with stated loading.
   - **Dummy antennas:** a 2.2 µH-class (1 m loop) dummy, and a 14.5 µH / 39 pF (2-turn loop) dummy.
   - **Perturbation:** for example, a fixed small capacitor on a test pad. **No fingertip tests.**
4. **Any oscillation:** stop and record the frequency, the conditions and C1.

## 4. Supply corners and protection

1. **Supply range:** repeat the DC table at 11.0 and 15.0 V. VDD should track, and the sink currents should not move.
2. **Overvoltage.** Thresholds are referred to **vp (TP18, at (70.2, 66.8))**, measured together with the jack voltage and **vpo (TP19, at (63.2, 60.4))**.
   - **Nominal:** off at 17.16 V rising, on at 16.02 V falling.
   - **Divider-only bounds** with ±1 % resistors and TI's published threshold limits: 16.56–17.92 V rising, 15.30–16.54 V falling.
   - The OR diode, PTC and choke make the jack voltage differ from vp, and the difference depends on load.
   - After cut-off, allow C18/C25/C19 to discharge before expecting vpo near 0 V. The settled supply current should be about 0.5 mA.
3. **Phantom feed.**
   - Disconnect J5 and feed 12 V up the coax through a receiver-side bias-T with a DC block to the analyser.
   - Expect VDD about 10.35 V.
   - Repeat the step-3 spectrum check on this feed.

## 5. Stability matrix (C1 decision, review-08 B2)

Run on the **same boards** with C1 = 15 pF, then again with C1 = 33 pF. Use the final post-wire harness, and measure the actual J1/J2 lead inductance.

| Axis | Conditions |
|---|---|
| Input | passive 2.2 µH-class dummy; the actual single-turn antenna; the 14.5 µH / 39 pF dummy; open; short; isolated 50 Ω |
| Output | 75 Ω; genuinely open (probe as in step 3); RG11 into a mismatch |
| Supply | jack and coax feeds; 11 and 15 V |
| Temperature | room, and the intended closed-box ambient up to about 70 °C |

**Record for each cell:**
- the 30–100 MHz region at a stated sensitivity;
- the full-span search;
- where the fixture allows, a small-signal network or return-ratio measurement, because the absence of a free-running spur doesn't measure phase margin.

**Then confirm the gain and NF cost of 33 pF** with calibrated fixtures before freezing C1. The simulated cost is +0.3 dB NF at 21 MHz and +0.36 dB at 30 MHz.

## 6. Small-signal performance

**Fixture:** a 50 Ω source through an isolated balanced input fixture (the model's source is floating), into a 75 Ω load. Budget the fixture loss and uncertainty.

**Model targets** with layout copper and C1 = 15 pF, for comparison only:

| | 1 MHz | 7 MHz | 14 MHz | 21 MHz | 28 MHz |
|---|---|---|---|---|---|
| Gt | 21.6 dB | 21.8 dB | 21.1 dB | about 19.0 dB | about 16.8 dB |
| NF | 0.2–0.4 dB to 14 MHz | | | about 0.8 dB | about 1.1 dB |

Also measure S22.

## 7. Large signal and temperature (planned measurements)

- **Linearity:** two-tone IIP3 at the low-level tones and with the −10 dBm blocker pair; single-tone P1dB.
- **Overload recovery:** after a 20 V/m-equivalent burst.
- **Closed-box soak:** recheck the DC table and the step-3/step-5 VHF region afterwards.

Compare with README "Hard pass". These are planned measurements, not demonstrated performance.

## Not covered

**Surge, ESD and HEMP qualification:** no rating is claimed for r1.
