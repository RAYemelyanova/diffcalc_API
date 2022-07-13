import json
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import numpy as np
from diffcalc.hkl.calc import HklCalculation
from fastapi import APIRouter, Body, Depends, Query

from diffcalc_API.controllers import UBCalculation as controller
from diffcalc_API.errors.UBCalculation import (
    check_params_not_empty,
    check_property_is_valid,
)
from diffcalc_API.examples import UBCalculation as examples
from diffcalc_API.fileHandling import supplyPersist, unpickleHkl
from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)

router = APIRouter(
    prefix="/ub",
    tags=["ub"],
    dependencies=[Depends(unpickleHkl), Depends(supplyPersist)],
)


@router.put("/{name}/reflection")
async def add_reflection(
    name: str,
    params: addReflectionParams = Body(..., example=examples.addReflection),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.add_reflection(name, params, hklCalc, persist)
    return {"message": f"added reflection for UB Calculation of crystal {name}"}


@router.patch("/{name}/reflection")
async def edit_reflection(
    name: str,
    params: editReflectionParams = Body(..., example=examples.editReflection),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.edit_reflection(name, params, hklCalc, persist)
    return {
        "message": (
            f"reflection with tag/index {params.tagOrIdx} edited to: "
            f"{hklCalc.ubcalc.get_reflection(params.tagOrIdx)}."
        )
    }


@router.delete("/{name}/reflection")
async def delete_reflection(
    name: str,
    tagOrIdx: Union[str, int] = Body(..., example="refl1"),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.delete_reflection(name, tagOrIdx, hklCalc, persist)
    return {"message": f"reflection with tag/index {tagOrIdx} deleted."}


@router.put("/{name}/orientation")
async def add_orientation(
    name: str,
    params: addOrientationParams = Body(..., example=examples.addOrientation),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.add_orientation(name, params, hklCalc, persist)
    return {"message": f"added orientation for UB Calculation of crystal {name}"}


@router.patch("/{name}/orientation")
async def edit_orientation(
    name: str,
    params: editOrientationParams = Body(..., example=examples.editOrientation),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.edit_orientation(name, params, hklCalc, persist)
    return {
        "message": (
            f"orientation with tag/index {params.tagOrIdx} edited to: "
            f"{hklCalc.ubcalc.get_orientation(params.tagOrIdx)}."
        )
    }


@router.delete("/{name}/orientation")
async def delete_orientation(
    name: str,
    tagOrIdx: Union[str, int] = Body(..., example="plane"),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.delete_orientation(name, tagOrIdx, hklCalc, persist)
    return {"message": f"reflection with tag or index {tagOrIdx} deleted."}


@router.patch("/{name}/lattice")
async def set_lattice(
    name: str,
    params: setLatticeParams = Body(example=examples.setLattice),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
    _=Depends(check_params_not_empty),
):
    controller.set_lattice(name, params, hklCalc, persist)
    return {"message": f"lattice has been set for UB calculation of crystal {name}"}


@router.patch("/{name}/{property}")
async def modify_property(
    name: str,
    property: str,
    targetValue: Tuple[float, float, float] = Body(..., example=[1, 0, 0]),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
    _=Depends(check_property_is_valid),
):
    controller.modify_property(name, property, targetValue, hklCalc, persist)
    return {"message": f"{property} has been set for UB calculation of crystal {name}"}


@router.get("/{name}/UB")
async def calculate_UB(
    name: str,
    firstTag: Optional[Union[int, str]] = Query(default=None, example="refl1"),
    secondTag: Optional[Union[int, str]] = Query(default=None, example="plane"),
    hklCalc: HklCalculation = Depends(unpickleHkl),
    persist: Callable[[HklCalculation, str], Path] = Depends(supplyPersist),
):
    controller.calculate_UB(name, firstTag, secondTag, hklCalc, persist)
    return json.dumps(np.round(hklCalc.ubcalc.UB, 6).tolist())
