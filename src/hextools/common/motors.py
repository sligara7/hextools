"""HEX motor-PV inventories for position metadata.

Readback PV lists for the MCA (accelerator-side) and MCF (endstation-side)
motion groups, ported **verbatim** from
``hex-acq-pyepics/lib/lib_device_control.py``. The legacy
scripts read every PV in a group at save time to record where each motor
was ("stage 5" metadata); these constants preserve that inventory for the
Bluesky-side plans.

Two quirks are deliberate and mirror the source exactly:

* Three entries in :data:`MCF8_MOTORS` end in ``.VAL`` rather than ``.RBV``
  (``OPT:1-Ax:Focus1``, ``OPT:2-Ax:Focus``, ``OPT:2-Ax:CamRot``).
* Some PVs appear in more than one group (``MC:1-Ax:7``/``MC:1-Ax:8`` in
  both MCF1 and MCF2; ``OPT:1-Ax:A1``/``OPT:1-Ax:Z0`` in both MCF2 and
  MCF3).
"""

from __future__ import annotations

MCA1_MOTORS: tuple[str, ...] = (
    "XF:27IDA-OP:1{Slt:1-Ax:HG}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:HC}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:VG}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:VC}Mtr.RBV",
    "XF:27IDA-OP:1{Fltr:1-Ax:Yu}Mtr.RBV",
    "XF:27IDA-OP:1{Fltr:1-Ax:Yd}Mtr.RBV",
    "XF:27IDA-OP:1{Fltr:2-Ax:Y}Mtr.RBV",
    "XF:27IDA-OP:3{Fltr:3-Ax:Y}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:I}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:O}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:B}Mtr.RBV",
    "XF:27IDA-OP:1{Slt:1-Ax:T}Mtr.RBV",
)

MCA2_MOTORS: tuple[str, ...] = (
    "XF:27IDA-OP:2{Fltr:4-Ax:Y}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:Z2}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:Z2RBK}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:ZC}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:P}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C1A}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C1B}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C2A}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C2B}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C1Bend}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C1Twist}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C2Bend}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C2Twist}Mtr.RBV",
)

MCA3_MOTORS: tuple[str, ...] = (
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C2R}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C1Y}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C1P}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:C2P}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:BS}Mtr.RBV",
    "XF:27IDA-OP:1{Mono:DCLM-Ax:FS}Mtr.RBV",
)

MCF1_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{Slt:2-Ax:HG}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:HC}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:VG}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:VC}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:I}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:O}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:B}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:2-Ax:T}Mtr.RBV",
    "XF:27IDF-OP:1{MC:1-Ax:7}Mtr.RBV",
    "XF:27IDF-OP:1{MC:1-Ax:8}Mtr.RBV",
)

MCF2_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{OPT:1-Ax:X2}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Y2}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Rx3}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Ry3}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:X3}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Y3}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Ry4}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:X4}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:A1}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Z0}Mtr.RBV",
    "XF:27IDF-OP:1{MC:1-Ax:7}Mtr.RBV",
    "XF:27IDF-OP:1{MC:1-Ax:8}Mtr.RBV",
)

MCF3_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{SHLD:1-Ax:X}Mtr.RBV",
    "XF:27IDF-OP:1{SHLD:1-Ax:Vx}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:A1}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Z0}Mtr.RBV",
)

MCF4_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{SMPL:1-Ax:Rx}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:Y}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:Rz}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:X1}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:Z1}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:Y1}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:Y2}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:Y3}Mtr.RBV",
)

MCF5_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{SMPL:1-Ax:Z2}Mtr.RBV",
    "XF:27IDF-OP:1{SMPL:1-Ax:X2}Mtr.RBV",
    "XF:27IDF-OP:1{MC:5-Ax:4}Mtr.RBV",
    "XF:27IDF-OP:1{EDXD:1-Ax:X}Mtr.RBV",
    "XF:27IDF-OP:1{EDXD:1-Ax:Y}Mtr.RBV",
    "XF:27IDF-OP:1{EDXD:1-Ax:Z}Mtr.RBV",
    "XF:27IDF-OP:1{EDXD:1-Ax:Rx}Mtr.RBV",
)

MCF6_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{Slt:CMT-Ax:I}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:CMT-Ax:O}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:CMT-Ax:B}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:CMT-Ax:T}Mtr.RBV",
    "XF:27IDF-OP:1{CMT:1-Ax:X}Mtr.RBV",
    "XF:27IDF-OP:1{CMT:1-Ax:Yc}Mtr.RBV",
    "XF:27IDF-OP:1{CMT:1-Ax:Yf}Mtr.RBV",
    "XF:27IDF-OP:1{Slt:CMT-Ax:Pitch}Mtr.RBV",
)

MCF7_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{IMG:1-Ax:X}Mtr.RBV",
    "XF:27IDF-OP:1{IMG:1-Ax:Y}Mtr.RBV",
    "XF:27IDF-OP:1{IMG:1-Ax:Z}Mtr.RBV",
    "XF:27IDF-OP:1{DIFF:1-Ax:X}Mtr.RBV",
    "XF:27IDF-OP:1{DIFF:1-Ax:Y}Mtr.RBV",
    "XF:27IDF-OP:1{DIFF:1-Ax:Z}Mtr.RBV",
    "XF:27IDF-OP:1{SHLD:1-Ax:PHx}Mtr.RBV",
    "XF:27IDF-OP:1{SHLD:1-Ax:PHy}Mtr.RBV",
)

MCF8_MOTORS: tuple[str, ...] = (
    "XF:27IDF-OP:1{OPT:1-Ax:CamRot}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:ObjSel}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Focus2}Mtr.RBV",
    "XF:27IDF-OP:1{OPT:1-Ax:Focus1}Mtr.VAL",
    "XF:27IDF-OP:1{OPT:2-Ax:Focus}Mtr.VAL",
    "XF:27IDF-OP:1{OPT:2-Ax:CamRot}Mtr.VAL",
    "XF:27IDF-OP:1{SMPL:1-Ax:Ry1}Mtr.RBV",
)

MOTOR_GROUPS: dict[str, tuple[str, ...]] = {
    "MCA1": MCA1_MOTORS,
    "MCA2": MCA2_MOTORS,
    "MCA3": MCA3_MOTORS,
    "MCF1": MCF1_MOTORS,
    "MCF2": MCF2_MOTORS,
    "MCF3": MCF3_MOTORS,
    "MCF4": MCF4_MOTORS,
    "MCF5": MCF5_MOTORS,
    "MCF6": MCF6_MOTORS,
    "MCF7": MCF7_MOTORS,
    "MCF8": MCF8_MOTORS,
}


def motor_pvs(group: str) -> tuple[str, ...]:
    """Return the motor PVs for a named group (e.g. ``'MCF8'``)."""
    try:
        return MOTOR_GROUPS[group]
    except KeyError:
        valid = ", ".join(MOTOR_GROUPS)
        raise KeyError(
            f"Unknown motor group {group!r}; valid groups: {valid}"
        ) from None
