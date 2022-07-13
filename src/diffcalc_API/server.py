from diffcalc.util import DiffcalcException
from fastapi import FastAPI, Request, responses

from diffcalc_API import errorDefinitions
from diffcalc_API.errors.Constraints import responses as responsesConstraints
from diffcalc_API.errors.HklCalculation import responses as responsesHkl
from diffcalc_API.errors.UBCalculation import responses as responsesUb
from diffcalc_API.fileHandling import createPickle, deletePickle

from . import routes

app = FastAPI(responses=errorDefinitions.responses)

app.include_router(routes.UBCalculation.router, responses=responsesUb)
app.include_router(routes.Constraints.router, responses=responsesConstraints)
app.include_router(routes.HklCalculation.router, responses=responsesHkl)

#######################################################################################
#                              Middleware for Exceptions                              #
#######################################################################################


@app.exception_handler(DiffcalcException)
async def diffcalc_exception_handler(request: Request, exc: DiffcalcException):
    return responses.JSONResponse(
        status_code=400,
        content={"message": exc.__str__(), "type": str(type(exc))},
    )


@app.exception_handler(errorDefinitions.DiffcalcAPIException)
async def http_exception_handler(
    request: Request, exc: errorDefinitions.DiffcalcAPIException
):
    return responses.JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "type": str(type(exc))},
    )


@app.middleware("http")
async def server_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here

        return responses.JSONResponse(
            status_code=500,
            content={"message": e.__str__(), "type": str(type(e))},
        )


#######################################################################################
#                                    Global Routes                                    #
#######################################################################################


@app.post("/{name}")
async def create_hkl_object(name: str):
    pickleLocation = createPickle(name)

    return {"message": f"file created at {pickleLocation}"}


@app.delete("/{name}")
async def delete_hkl_object(name: str):
    pickleLocation = deletePickle(name)

    return {"message": f"file at location {pickleLocation} deleted"}
