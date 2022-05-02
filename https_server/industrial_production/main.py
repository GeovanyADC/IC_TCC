from fastapi import FastAPI, Request
import json
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


class current_production(BaseModel):
    start_date: datetime
    total_time: str
    total_produced: int
    event_list: list
    machine_list: list


# Peças produzidas
produced_parts = 0

# Força fim de produção
force_end = False


# Rota1: rota de inicialização de produção.
@app.post("/start_production")
def start_production(production: current_production):

    return production


@app.get("/")
def read_main():
    return {"message": "Hello World of FastAPI HTTPS"}
