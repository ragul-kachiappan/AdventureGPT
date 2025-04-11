from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def hello_world(request):
    """Simple hello world endpoint"""
    return JSONResponse({"message": "Welcome to Colossal Adventure!"})


# Create the Starlette application
app = Starlette(
    routes=[
        Route("/", hello_world),
    ]
)
