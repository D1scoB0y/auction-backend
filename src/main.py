from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import config
import src.user.router as _auth_module
import src.auction.router as _auction_module


app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.CLIENT_ORIGIN, 'http://192.168.0.15:5173', 'http://localhost:4173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(_auth_module.router)
app.include_router(_auction_module.router)
