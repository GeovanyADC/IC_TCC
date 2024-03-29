from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import time
import threading
import psycopg2
import os

app = FastAPI()

# Request body type
class current_production(BaseModel):
    pc_to_produce_a: int
    pc_to_produce_b: int
    machine_list: list
 
current_production_dict = {
    "start_time": None,
    "total_time": None,
    "production_date": None,
    "total_produced_a": None,
    "total_produced_b": None,
    "event_list": None,
    "machine_list": None,
    "status": "stopped",
    "final_list_of_events": None,
}

mutex = threading.Lock()  # Mutex to protect dict from concurrent reads

# Route1: Production startup route
@app.post("/start_production")
def start_production(production: current_production):

    if (current_production_dict["status"] == "stopped") or (current_production_dict["status"] == "finished"):
        start = time.time()  # Initial production time of 'x' parts
        current_date = date.today()

        mutex.acquire()

        current_production_dict["start_time"] = start
        current_production_dict["production_date"] = current_date
        current_production_dict["total_produced_a"] = production.pc_to_produce_a
        current_production_dict["total_produced_b"] = production.pc_to_produce_b
        
        # Get the initial state
        state = ""
        with open('initialstate.txt') as init:
            state = init.read()
            print("Current state: ", state)

        # It starts the other scientific research
        os.system('python3 colonia.py {0} {1} {2}'.format(production.pc_to_produce_a, production.pc_to_produce_b, state))

        # It will get the list from other scientific research
        # Read the event list from ant alg
        list_of_events = []
        with open('list.txt') as f:
            file = f.read()
            file = file.split(" ")
            for i in file:
                list_of_events.append("{0}".format(i))

        init.close()
        f.close()

        print("List of events received from ant alg: ",list_of_events)

        current_production_dict["event_list"] = list_of_events

        current_production_dict["final_list_of_events"] = list_of_events.copy()
        
        # Production 1 
        # current_production_dict["event_list"] = ["B1_PRE", "B1_PRE_END", "B1_PREPARATION_A", "B1_POINT_OF_INTEREST_PRE_A",
        # "B1_FIN_A", "B1_FIN_A_END", "B1_POINT_OF_INTEREST_FIN_A","B2_PRE", "B2_PRE_END","B2_PREPARATION_B", "B2_POINT_OF_INTEREST_PRE_B","B1_STOP", "B1_STOP_END",
        # "B2_FIN_B", "B2_FIN_B_END","B2_POINT_OF_INTEREST_FIN_B","B2_STOP", "B2_STOP_END"]
        # current_production_dict["final_list_of_events""] = ["B1_PRE", "B1_PRE_END", "B1_PREPARATION_A", "B1_POINT_OF_INTEREST_PRE_A",
        # "B1_FIN_A", "B1_FIN_A_END", "B1_POINT_OF_INTEREST_FIN_A","B2_PRE", "B2_PRE_END","B2_PREPARATION_B", "B2_POINT_OF_INTEREST_PRE_B","B1_STOP", "B1_STOP_END",
        # "B2_FIN_B", "B2_FIN_B_END","B2_POINT_OF_INTEREST_FIN_B","B2_STOP", "B2_STOP_END"]

        current_production_dict["machine_list"] = production.machine_list
        current_production_dict["status"] = "started"
        mutex.release()

        return current_production_dict
    
    else:

        return "Production has already started, wait until to be finished"

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

        if current_production_dict["event_list"] == []:

            current_production_dict["status"] = "finished"
            end = time.time()

            current_production_dict["total_time"] = int(
                end - current_production_dict["start_time"]
            )

            insert_into_database()  # Insert current production data
            mutex.release()

            return {"message": "finished"}  # List successfully completed

        mutex.release()
        return {"message": "updated"}  # List updated successfully
    else:
        mutex.release()
        return {"message": "different"}  # Event other than head of queue


def insert_into_database():
    try:

        conn = psycopg2.connect(
            # host="localhost",
            host="postgres", # AWS
            port=5432,
            database="postgres",
            user="postgres",
            # password="postgres",
            password="5492200",
        )
        conn1 = psycopg2.connect(
            # host="localhost",
            host="postgres", # AWS
            port=5432,
            database="postgres",
            user="postgres",
            # password="postgres",
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
                    total_produced_a integer not null,
                    total_produced_b integer not null,
                    event_list text not null,
                    machine_list text not null
                )
                """
            )
            conn.commit()
        except:
            print("Table already exists")

        # Converting the two lists to strings
        a = (
            " ".join(current_production_dict["final_list_of_events"]),
        )
        b = " ".join(current_production_dict["machine_list"])

        cursor_insert_table.execute(
            """
                insert into production (total_time, production_date, total_produced_a, total_produced_b, event_list, machine_list)
                values({0}, cast('{1}' as date), {2}, '{3}', '{4}', '{5}')
            """.format(
                current_production_dict["total_time"],
                current_production_dict["production_date"],
                current_production_dict["total_produced_a"],
                current_production_dict["total_produced_b"],
                a[0],
                b,
            )
        )
        conn1.commit()
        conn.close()
        conn1.close()
    except:
    
        print("Problems when inserting data into postgresql")