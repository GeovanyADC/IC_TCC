from fastapi import FastAPI, Request
import json
from pydantic import BaseModel
from datetime import date
import time

app = FastAPI()

# Request body type
class current_production(BaseModel):
    pc_to_produce: int
    machine_list: list


current_production_dict = {
    "total_time": None,
    "production_date": None,
    "total_produced": None,
    "event_list": None,
    "machine_list": None,
}


# Peças produzidas
produced_parts = 0

# Força fim de produção
force_end = False


# Rota1: rota de inicialização de produção.
@app.post("/start_production")
def start_production(production: current_production):

    # Tempo inicial da produção de 'x' peças
    start = time.time()

    # Data atual
    current_date = date.today()
    current_date = current_date.strftime("%d/%m/%Y")

    # Lista de eventos
    # list_of_events = file.heuristica(production.pc_to_produce)
    # global current_production_dict

    current_production_dict["production_date"] = current_date
    current_production_dict["total_produced"] = production.pc_to_produce
    # current_production_dict["event_list"] = list_of_events
    current_production_dict["machine_list"] = production.machine_list

    return current_production_dict


@app.get("/")
def read_main():
    return {"message": "Hello World of FastAPI HTTPS"}
