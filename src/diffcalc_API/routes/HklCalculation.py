from itertools import product
from typing import Dict, List, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.geometry import Position
from fastapi import APIRouter, Depends, HTTPException, Query

from diffcalc_API.models.HklCalculation import positionType
from diffcalc_API.utils import unpickleHkl

router = APIRouter(prefix="/calculate", tags=["hkl"])


singleConstraintType = Union[Tuple[str, float], str]

# ERROR CATCHING:
# diffcalc exceptions are thrown if hklCalc is not fully constrained or the
# combination of constraints is invalid. Catch these (perhaps by just querying
# hklCalc.constraints.is_fully_constrained() and ...is_current_mode_implemented())
# and throw your own error to properly constrain stuff. Maybe incl. a link to the
# docs here.

# diffcalc exceptions also thrown if resulting lab position doesn't map back to the
# same miller indices, same with virtual angles. This probably means there is something
# wrong with the hkl settings but unsure what...


@router.get("/{name}/position/lab")
async def lab_position_from_miller_indices(
    name: str,
    pos: Tuple[float, float, float] = Query(example=[0, 0, 1]),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    if sum(pos) == 0:
        raise HTTPException(
            status_code=401, detail="At least one of the hkl indices must be non-zero"
        )

    allPositions = hklCalc.get_position(*pos, wavelength)

    return {"payload": allPositions}


def validate_lab_position(pos: Position):
    return all((0 < pos.mu < 90, 0 < pos.nu < 90, -90 < pos.phi < 90))


# ERROR CATCHING:
@router.get("/{name}/position/hkl")
async def miller_indices_from_lab_position(
    name: str,
    pos: Tuple[float, float, float, float, float, float] = Query(
        default=[0, 0, 0, 0, 0, 0], example=[7.31, 0, 10.62, 0, 0, 0]
    ),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    hklPosition = hklCalc.get_hkl(Position(*pos), wavelength)
    return {"payload": tuple(np.round(hklPosition, 16))}


# ERROR CATCHING:
# it's possible that this fails, e.g. what happens if you do np.arange(0, -1, 1)?
def generate_axis(start, stop, inc):
    return np.arange(start, stop + inc, inc)


# ERROR CATCHING:
# implement a check where start, stop and inc are logical. i.e,
# if stop is less than start inc should be negative.

# same error catching as get hkl position from above.
@router.get("/{name}/scan/hkl")
async def scan_hkl(
    name: str,
    start: positionType = Query(..., example=(1, 0, 1)),
    stop: positionType = Query(..., example=(2, 0, 2)),
    inc: positionType = Query(..., example=(0.1, 0, 0.1)),
    wavelength: float = Query(..., example=1),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    valueOfAxes = [
        generate_axis(start[i], stop[i], inc[i]) if inc[i] != 0 else [0]
        for i in range(3)
    ]

    results = {}

    for h, k, l in product(*valueOfAxes):
        allPositions = hklCalc.get_position(h, k, l, wavelength)
        results[f"({h}, {k}, {l})"] = combine_lab_position_results(allPositions)

    return {"payload": results}


# ERROR CATCHING:
# implement a check where start, stop and inc are logical. i.e,
# if stop is less than start inc should be negative.

# same error catching as get hkl position from above.
@router.get("/{name}/scan/wavelength")
async def scan_wavelength(
    name: str,
    start: float = Query(..., example=1.0),
    stop: float = Query(..., example=2.0),
    inc: float = Query(..., example=0.2),
    hkl: positionType = Query(..., example=(1, 0, 1)),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    wavelengths = np.arange(start, stop + inc, inc)
    result = {}

    for wavelength in wavelengths:
        allPositions = hklCalc.get_position(*hkl, wavelength)
        result[f"{wavelength}"] = combine_lab_position_results(allPositions)

    return {"payload": result}


# ERROR CATCHING:
# implement a check where start, stop and inc are logical. i.e,
# if stop is less than start inc should be negative.

# same error catching as get hkl position from above.
@router.get("/{name}/scan/{constraint}")
async def scan_constraint(
    name: str,
    variable: str,
    start: float = Query(..., example=1),
    stop: float = Query(..., example=4),
    inc: float = Query(..., example=1),
    hkl: positionType = Query(..., example=(1, 0, 1)),
    wavelength: float = Query(..., example=1.0),
    hklCalc: HklCalculation = Depends(unpickleHkl),
):
    result = {}
    for value in np.arange(start, stop + inc, inc):
        setattr(hklCalc, variable, value)
        allPositions = hklCalc.get_position(*hkl, wavelength)
        result[f"{value}"] = combine_lab_position_results(allPositions)

    return {"payload": result}


def combine_lab_position_results(positions: List[Tuple[Position, Dict[str, float]]]):
    result = []

    for position in positions:
        result.append({**position[0].asdict, **position[1]})

    return result