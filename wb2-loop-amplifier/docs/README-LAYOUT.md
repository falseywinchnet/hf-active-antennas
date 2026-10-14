# WB-2 layout (KiCad 10): r1, revised to r2 after design review 06

Bob Wilder (Claude), 2026-10-01. Prototype layout of the final hard-pass circuit (T2 = WB5-1T, no peaking, 470 Ω source beads).

**Build:** everything is generated, nothing is hand-edited in the GUI.
- `make_fplib.py` → `wb2.pretty`, `wb2.3dshapes`
- `build_wb2.py` → `wb2.kicad_pcb` (imports `route_wb2.py`, which imports `place_wb2.py`)
- `run.sh` rebuilds, runs DRC and dumps `geom.json`
- `plot_board.py`, `metrics.py` and `make_bom.py` produce the review plots, `layout_metrics.md` and the BOM
- **Inputs:** `../netlist.csv` and `../footprints.csv`, both written by `python wb2.py pcb`.

**Status:**
- **DRC (KiCad 10):** 0 unconnected, 0 clearance, 0 courtyard. Two cosmetic silk overlaps, between the DNP BAV23 outlines.
- **Fabrication set** in `fab/`:
  - Gerbers and Excellon (separate PTH/NPTH) with drill maps
  - pick-and-place (`wb2-pos.csv`, `wb2-cpl.csv`)
  - BOM (`wb2-bom.csv`/`.md`)
  - layer PDFs/SVGs and the assembly drawing
  - STEP model
- **Not fabrication-approved.** The board still needs a layout review (task 03).

## Board and enclosure

**Enclosure:** Hammond **1554F2GY**, polycarbonate, IP66.
- Inside dimensions: 112.9 × 80.9 × 54.5 mm.
- The PCB is **96 × 76 mm, 1.6 mm FR-4, 2 layers, 1 oz copper**.
- It mounts on the box's M3 brass-insert pattern (77 × 68 mm, holes H1–H4) with 10 mm standoffs.
- The four corner bites (R 8.8 mm) clear the lid-screw columns at 107 × 77.

**Connectors.** All are on the walls, wired to board landings:
- **Left wall:** binding posts J1 (LOOP A), J3 (GND, the surge return) and J2 (LOOP B).
- **Right wall:** J4, an F bulkhead (RG-179 pigtail ≤ 50 mm, to a centre-plus-braid landing), and J5, a sealed 2.1 mm DC jack.

**Frame.** Coordinates are mm in the design frame: origin at the board's bottom-left, y up. The generator's KiCad frame is X = 40 + x, Y = 140 − y.

## r2 changes (review-06, reply-06)

- **C24 local to U3 IN.** C24 is now at (66.6, 59.2), 3.8 mm routed to U3 IN.
- **SP4022 grounds:** two vias each.
- **Probe grounds:** 21 GND probe pads, each within 1.4–3 mm of its signal pad, except REF at 4.1 mm. They are mapped in `renders/tp_map.png` and `tp_table.md`.
- **Corridor bridge stitching:** vias at (62.0 / 66.6, 36.9 / 39.1).
- **D14:** second anode via.
- **T4 double end-exchange** in `wb2.py`: 1 = LB, 3 = LA, 4 = SBK, 6 = GND. Each A-side path now has an equal B-side partner, with a three-spine mirror-symmetric loop distribution:
  - **outer spine, x 21.6:** LA below the axis, LB above;
  - **LA up-spine, x 23.0** and **LB down-spine, x 24.4:** each crosses its partner once on B.Cu;
  - **routed lengths:** 15.34 / 20.52 / 35.44 mm per side; SAK = SBK = 8.49 mm.
- **C19 frozen:** Panasonic EEU-FC1V221B.
- **Mechanical handoff drawing:** `renders/mech_drawing.png` and `fab/plots/wb2-mech.pdf`.
- **One-command rebuild:** `make_all.sh`.

## Netlist changes made for the layout (in `wb2.py`)

1. **T2 secondary ends swapped.**
   - Change: pin 1 = CBt and pin 3 = CAt, previously the reverse. The SPICE model now follows the physical pins, so the dots are unchanged.
   - Why: side A sits in the lower half of the board, so CAt lands on T2's lower-left pad without CA and CB crossing.
   - Effect: the output is inverted, which is irrelevant for a receive amplifier. T2 is outside the zero-flux loop.
   - Check: `wb2.py ac` reproduces the hard-pass Gt and NF exactly (19.2 dB / 0.75 dB at 21 MHz, 16.4 dB / 1.22 dB at 30 MHz).
2. **J5 is now a panel jack, Switchcraft 721AU (IP68, 2.1 mm), wired to a 2-pad landing**, replacing the board-edge PJ-102AH.
   - Why: on the insert pattern the board edge sits about 8 mm behind the wall, so a board-edge jack cannot mate.
   - Unchanged: pad 1 = vin, pad 2 = CBL_GND, and the switch terminal is left unconnected at the jack.

## Floorplan

The signal flows left to right along the axis y = 38. Side A (T3, Q1–Q4, Q9–Q12, sink A) is below the axis and side B mirrors it above.

| x (mm) | what |
|---|---|
| 0–19 | posts (J1 at y 28, J3 at 38, J2 at 48). LAP and LBP rails (1.2 mm) run straight through GDT1/2 and D1–D6 pad 1. All protection grounds face the axis, so the region around J3 is the surge-return copper (pours on both layers plus a via field). L9/L10 links at x 19.5. |
| 20–28 | (r2) outer spine at x 21.6 (LA below, LB above), LA up-spine at x 23.0 and LB down-spine at x 24.4. The two crossings are on B.Cu at (24.4, 30.3 → 25.7) and (23.0, 45.7 → 50.3), each with 0.8/0.4 vias. R1/R2 bleeds sit on the outer spine. The R3 + C1 snubber is a vertical chain at x 26.1 between T1 pads 6 and 4. |
| 24–41 | T3 (32.3, 16), T1 (34.2, 38, rotated 180°) and T4 (32.3, 60). Loop windings face the spines. T1's gate column (GA 35.46, GCT 38, GB 40.54) faces the rows; the T3/T4 low-turn pins face their source buses. |
| 41–49 | gate clamps. D7/D8 BAV99 straddle the GA/GB buses with pin 3 on GCT. The DNP alternatives D12/D13 BAV23 sit beside them; the diagonal 1+3 / 2+4 joins run under the body. GCT runs along the axis to C2 (49.9) and R4 (61.6). |
| 49–62 | input rows Q1–Q4 / Q5–Q8 at a 3.5 mm pitch. Gates face the axis on the GA/GB buses (y 34.48 / 41.52). Drains feed into the DA/DB channel under the SOT-23 bodies (y 33.3 / 42.7; SOT-23_WB heels give a 1.36 mm channel). Sources go out through the FB1–FB8 beads to the SA/SB buses (y 29.05 / 46.95). |
| 62–66 | DC corridor: B.Cu lanes GBIAS 63.2, VDD 64.0, XB 64.8, VBB 65.6. |
| 64–78 | cascode rows Q9–Q12 / Q13–Q16 flipped: S/D toward the axis (S into the DA/DB channel, D up to the CA/CB buses at y 36.0 / 40.0), gates outboard through the R16–R23 stoppers to the BA/BB buses (y 28.97 / 47.03), with R24/C12 and R25/C13 hanging off them. The strip between CA and CB is GND pour plus five stitching vias. |
| 78–95 | L3/L4 0 Ω links stand vertically in the strip end and feed T2 (87.6, 38). T2CT leaves pad 2 under the T2 body, to C15 (83.8, 32.6), C14 and R26 below T2. OUTH from pad 6 runs to R29, whose ground pad sits next to the J4 braid pad, then to C16 and the J4 landing (91, 49.2; braid pad toward the wall). |
| bottom centre | L1 (52.4, 24) leaves the SA bus outward; C3 (42.6, 24.2) to T3 pad 6. XA bus at y 21.2 with C5/C7. Sink A (Q17 rot 180, R5, R7) sits left of U1 (61, 12) and sink B (Q18, R8, R6) right of it. REF joins U1 pins 3 and 5 under the body, with C9/R10/R11 beneath. The TL431 block (U2, R9, R12, R13, C10) runs along the bottom edge. The VBB divider (R14, R15, C11) is under the BA bus. VDD is distributed along y 20.6. |
| top centre/right | L2 / C4 / C6 / C8 mirror the A side; XB leaves by via. Power: J5 → L5 (86.4, 64.4) → D9 → vor ← D10 ← FB9 ← L7 ← L6‖R27 ← RFO; then F1 → vp (D11, C24) → U3 (63.4, 64, rot 180; R33–R35 right, R36/C23 left) → vpo (C18, D14) → L8 → vq (C25) → R28 → VDD (C20, C19 radial at 42.2, 70.4). |

**Ground (K-board style):**
- Solid GND pours on both layers, connected solidly to pads, with a via at every ground pad edge and no ground stubs.
- 338 stitching vias.
- **RTN3:** a B.Cu island (57.4–70.2 × 62.4–66.4) carries U3 pad 11's thermal vias and the R35/R36/C23 returns through vias. The pin 5 to pad 11 join is on top.
- **No-pour rule area** under the cable side of L5 and J5 (x ≥ 88.3, y 60.3–70.4). CBL_GND is a single trace.

**Test pads:** 1 mm round, on the net copper with no stubs:
- signals: GA, GB, GCT, SA, SB, SAK, SBK, XA, XB, ESA, ESB, CA, CB, REF, VBB, T2CT, VDD, vp, vpo;
- six GND pads.

## What I want challenged

1. **The DC corridor.**
   - Four B.Cu lanes slice the bottom pour between y ≈ 3 and 59. XB and VDD also run diagonally from the L2 / R28 area.
   - The top pour bridges the slot in the strip and outside the rows, but the bottom reference under both rows is split at x ≈ 63–66.
   - **Alternatives I see:**
     - move U1 and the references into the top half, which trades one crossing set for another;
     - a second op-amp so each sink is local, which is a part change;
     - accept it, because only DC crosses there and the lanes run perpendicular to the RF buses.
2. **LA/LB topology.**
   - The two-spine crossover is planar and nearly symmetric in structure, but LA is 75 mm against 60 mm for LB, with about 37 versus 30 mΩ of total tree copper.
   - The loop-path share is what matters for noise: about 0.46 dB per 0.1 Ω.
   - Is there an arrangement with equal lengths and no B.Cu hop?
3. **T1 snubber position.** R3/C1 sit at T1's loop pads rather than at the posts. That position was chosen for the VHF mode the snubber damps (T1 leakage); confirm.
4. **SAK vs SBK** (8.5 vs 13.6 mm). This is the T3/T4 low-turn side: T4 keeps the original pin map, so its SBK pad is the far one.
5. **T2CT under the T2 body.** It is AC ground and carries 67 mA of DC. Acceptable, or should the strip carry it instead?
6. **Gate clamps** with DNP alternatives side by side on GA/GB. The BAV23 diagonal join runs under the SOT-143 body.
7. **Surge-return geometry around J3** against rule 1.
8. **Mechanical fit and connector placement on the walls.**

## Not done / not claimed

- No field-solver extraction of the layout parasitics yet. The hard-pass models assumed lumped 5 nH gate/drain leads and a ~15 pF snubber node. A parasitic back-annotation (as `lna/parasitic2.py` did for K-boards) is the next simulation step once the placement is settled.
- No thermal simulation.
- No surge test.
- No priced BOM.
- The 3D bodies for the Coilcraft WB parts and the F pigtail are simple boxes (`wb2.3dshapes`). L5 has no model.
