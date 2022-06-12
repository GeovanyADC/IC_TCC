from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import time
import threading
import psycopg2

app = FastAPI()

# Request body type
class current_production(BaseModel):
    pc_to_produce: int
    machine_list: list

current_production_dict = {
    "start_time": None,
    "total_time": None,
    "production_date": None,
    "total_produced": None,
    "event_list": None,
    "machine_list": None,
    "status": "stopped",
    "final_event_list": None,
}

mutex = threading.Lock()  # Mutex para proteger o dict de leituras concorrentes

# Rota1: rota de inicialização de produção.
@app.post("/start_production")
def start_production(production: current_production):

    start = time.time()  # Tempo inicial da produção de 'x' peças
    current_date = date.today()  # Data atual

    mutex.acquire()

    # list_of_events = file.heuristica(production.pc_to_produce)
    current_production_dict["start_time"] = start
    current_production_dict["production_date"] = current_date
    current_production_dict["total_produced"] = production.pc_to_produce
    # current_production_dict["event_list"] = list_of_events
    current_production_dict["event_list"] = ["B1_SOURCE", "b", "c"]
    current_production_dict["final_event_list"] = ["aa", "b", "c"]
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

    print("eveto--", event)

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
                end = time.time()

                current_production_dict["total_time"] = int(
                    end - current_production_dict["start_time"]
                )

                insert_into_database()  # Inserir dados da produção atual

            mutex.release()
            return {"message": "finished"}  # Lista atualizada com sucesso
        else:
            mutex.release()
            return {"message": "different"}  # Evento diferente do início da fila
    else:
        mutex.release()
        return {"message": "finished"}  # Tentativa falha de atualização


def insert_into_database():

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="5492200",
    )
    conn1 = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="5492200",
    )

    cursor_create_table = conn.cursor()
    cursor_insert_table = conn1.cursor()

    try:
        cursor_create_table.execute(
            """
            create table production (
                user_id serial primary key,
                total_time varchar(20) not null,
                production_date date not null,
                total_produced integer not null,
                event_list text not null,
                machine_list text not null
            )
            """
        )
        conn.commit()
    except:
        print("Table already exists")

    # Convertendo as duas listas em strings
    a = (
        " ".join(current_production_dict["final_event_list"]),
    )  # Transforma a lista em string
    b = " ".join(current_production_dict["machine_list"])

    cursor_insert_table.execute(
        """
            insert into production (total_time, production_date, total_produced, event_list, machine_list)
            values({0}, cast('{1}' as date), {2}, '{3}', '{4}')
        """.format(
            current_production_dict["total_time"],
            current_production_dict["production_date"],
            current_production_dict["total_produced"],
            a[0],
            b,
        )
    )
    conn1.commit()
    conn.close()
    conn1.close()
