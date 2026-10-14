# WB-2 sourcing and lifecycle check (2026-10-01)

**Rules** (user, 2026-10-01): no NXP transistors; prefer onsemi; active production only, never EOL, LTB or obsolete. Nexperia is NXP's former standard-products business, so ask before using it.

**Status source:** distributor or manufacturer listings found on 2026-10-01. Recheck at order time.

**Changes made:** Q17/Q18 moved from Nexperia BC817-25 to **onsemi BC817-25LT1G**, and D7/D8 from Nexperia BAV99 to **onsemi BAV99LT1G**. The pinouts and the SOT-23 lands are identical, so the board copper is unchanged.

| Ref | Part | Status | Note |
|---|---|---|---|
| Q1–Q16 | Linear Systems LSBF862 (SOT-23) | active, long-term availability; factory stock to about 8 weeks | buy direct; Vgs-selected per README |
| T1 | Coilcraft WB16-6TSLD | catalog | stock and lead time to confirm |
| T3, T4 | Coilcraft WB36-1SLD | catalog | stock and lead time to confirm |
| T2 | Coilcraft WB5-1TSLD | catalog | stock and lead time to confirm |
| Q17, Q18 | onsemi BC817-25LT1G | active | replaces Nexperia (rule) |
| D7, D8 | onsemi BAV99LT1G | active | replaces Nexperia |
| D12, D13 (DNP) | Nexperia BAV23 (SOT-143B) | **kept, DNP (user, 2026-10-01)** | evaluation footprint only; onsemi has no SOT-143B equivalent |
| D14 | Nexperia PMEG4020ER | **kept (user, 2026-10-01)** | onsemi SS24FL was considered and not adopted |
| D9, D10 | onsemi SS14 | active | |
| D1–D6 | Littelfuse SP4022-01FTG-C | active | |
| GDT1, GDT2 | Bourns GDT25-09-S1-RP | active | |
| D11 | Littelfuse SMBJ26A | mainstream | |
| U1 | TI LM358BIDR | TI production | |
| U2 | TI TL431BIDBZR | active | |
| U3 | TI TPS26621DRCR | active | |
| F1 | Bourns MF-MSMF020/60-2 | active | |
| L5 | Würth 744222 (WE-SL2) | active | 2 × 1 mH, 207 mΩ |
| L1, L2, L7 | TDK B82442T1105K000 | stocked, current series | the H-series is obsolete; the T-series is the replacement |
| L6, L8 | TDK B82442T1104K000 | stocked, current series | |
| FB1–FB8 | Murata BLM18PG471SN1D | active | |
| FB9 | Murata BLM18KG601SN1D | active | |
| L9, L10, L3, L4 | Vishay WFZ0603 / WFZ0805 metal-foil jumpers | catalog | about 0.5 mΩ; AEC-Q200 |
| C19 | Panasonic EEU-FC1V221B | to confirm at order | |

**Sources:**
- onsemi BC817-25LT1G: [lioncircuits](https://lioncircuits.com/parts/BC817-25LT1G), [findchips](https://blog.findchips.com/?p=5802)
- BAV99LT1G: [DigiKey](https://www.digikey.gr/en/products/detail/onsemi/BAV99LT1G/918327)
- SS14: [Octopart](https://octopart.com/part/onsemi/SS14)
- SS24FL: [onsemi](https://www.onsemi.com/products/discrete-power-modules/schottky-diodes-schottky-rectifiers/ss24fl)
- TPS26621DRCR: [DigiKey](https://punchouttest.digikey.ca/en/products/detail/texas-instruments/TPS26621DRCR/9692669)
- GDT25-09-S1-RP: [DigiKey](https://punchouttest.digikey.ca/en/products/detail/bourns-inc/GDT25-09-S1-RP/13583216)
- SP4022-01FTG-C: [Littelfuse](https://m.littelfuse.com/products/tvs-diode-arrays/lightning-surge-protection/sp4022/sp4022_01ftg_c.aspx)
- LSBF862: [audioXpress](https://audioxpress.com/news/linear-integrated-systems-introduces-superior-lower-noise-n-channel-jfet-replacement-for-discontinued-nxp-bf862)
- WFZ: [Vishay datasheet](https://www.vishay.com/docs/30432/wfz-jumper.pdf)
- BLM18PG471SN1D: [DigiKey](https://www.digikey.com/en/products/detail/murata-electronics/BLM18PG471SN1D/1948328)
- BLM18KG601SN1D: [element14](https://kr.element14.com/murata/blm18kg601sn1d/ferrite-bead-0603-600r-1-3a/dp/1781094)
- B82442T1105K000: [element14](https://my.element14.com/epcos/b82442t1105k000/inductor-1mh-1-8mhz-2220/dp/3580419)
- MF-MSMF020/60-2: [findchips](https://origin-www.findchips.com/detail/mf-msmf020%2f60-2/Bourns-Inc)
- 744222: [elexess](https://www.elexess.com/part/20213/w-rth/744222)
- TL431BIDBZR: [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/TL431BIDBZR/863704)
- Coilcraft WB SMT: [Coilcraft](https://www.coilcraft.com/en-us/products/transformers/wideband-rf-transformers/smt/wb_smt/)
- Hammond 1554: [Hammond](https://www.hammfg.com/electronics/small-case/plastic/1554)
