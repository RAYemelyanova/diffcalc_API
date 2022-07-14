from pathlib import Path
from typing import Callable, Dict, Union

from diffcalc.hkl.calc import HklCalculation
from diffcalc.hkl.constraints import Constraints

from diffcalc_API.config import constraintsWithNoValue
from diffcalc_API.errors.Constraints import check_constraint_exists
from diffcalc_API.persistence import HklCalculationRepository


async def set_constraints(
    name: str,
    constraintDict: Dict[str, Union[float, bool]],
    repo: HklCalculationRepository,
) -> None:
    hkl_calc = await repo.load(name)

    booleanConstraints = set(constraintDict.keys()).intersection(constraintsWithNoValue)
    for constraint in booleanConstraints:
        constraintDict[constraint] = bool(constraintDict[constraint])

    hkl_calc.constraints = Constraints(constraintDict)
    await repo.save(name, hkl_calc)


def remove_constraint(
    name: str,
    property: str,
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    check_constraint_exists(property)
    setattr(hklCalc.constraints, property, None)
    persist(hklCalc, name)
    return


def set_constraint(
    name: str,
    property: str,
    value: Union[float, bool],
    hklCalc: HklCalculation,
    persist: Callable[[HklCalculation, str], Path],
):
    check_constraint_exists(property)

    if property in constraintsWithNoValue:
        value = bool(value)

    setattr(hklCalc.constraints, property, value)
    persist(hklCalc, name)
    return