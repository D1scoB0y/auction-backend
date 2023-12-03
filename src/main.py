from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.user.router as _auth_module
import src.auction.router as _auction_module


app = FastAPI(openapi_url='')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'https://www.fotojager.ru',
        'https://fotojager.ru',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(_auth_module.router)
app.include_router(_auction_module.router)
