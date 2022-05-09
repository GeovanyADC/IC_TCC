from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import time
import threading

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
    "status": "stopped",
    "final_event_list": None,
}


produced_parts = 0  # Peças produzidas
force_end = False  # Força fim de produção
mutex = threading.Lock()  # Mutex para proteger o dict de leituras concorrentes

# Rota1: rota de inicialização de produção.
@app.post("/start_production")
def start_production(production: current_production):

    start = time.time()  # Tempo inicial da produção de 'x' peças

    current_date = date.today()  # Data atual
    current_date = current_date.strftime("%d/%m/%Y")

    mutex.acquire()

    # list_of_events = file.heuristica(production.pc_to_produce)
    current_production_dict["production_date"] = current_date
    current_production_dict["total_produced"] = production.pc_to_produce
    # current_production_dict["event_list"] = list_of_events
    current_production_dict["event_list"] = ["a", "b", "c"]
    current_production_dict["final_event_list"] = ["a", "b", "c"]
    current_production_dict["machine_list"] = production.machine_list
    current_production_dict["status"] = "started"
    mutex.release()

    return current_production_dict


@app.get("/get_event")
def send_event_to_client():

    if current_production_dict["status"] == "stopped":
        return {"message": "stopped"}  # Production has not started
    elif current_production_dict["status"] == "finished":
        return {"message": "finished"}  # Finished production
    else:  # Production is running -> return event to be triggered
        return {"message": current_production_dict["event_list"][0]}


@app.put("/confirm_event")
def update_event_list_controllable(event: str):

    mutex.acquire()

    event_from_list = current_production_dict["event_list"][0]

    if event == event_from_list:

        del current_production_dict["event_list"][0]

        mutex.release()

        return {"message": "updated"}  # Lista atualizada com sucesso
    else:
        mutex.release()
        return {"message": "different"}  # Evento diferente do início da fila


@app.put("/end_event")
def update_event_list_uncontrollable(event: str):

    mutex.acquire()

    if current_production_dict["event_list"] != []:

        event_from_list = current_production_dict["event_list"][0]

        if event == event_from_list:

            del current_production_dict["event_list"][0]

            if current_production_dict["event_list"] == []:

                current_production_dict["status"] = "finished"
                # insert_into_database(current_production_dict) # Inserir dados da produção atual

            mutex.release()
            return {"message": "updated"}  # Lista atualizada com sucesso
        else:
            mutex.release()
            return {"message": "different"}  # Evento diferente do início da fila
    else:
        mutex.release()
        return {"message": "finished"}  # Tentativa falha de atualização


# Implementar o insert_into_database
# Separar as rotas das funções
# event get successfull
# save the list before update
