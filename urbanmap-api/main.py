from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import List
import os

app = FastAPI()

# ------------------------
# Caricamento dati GTFS
# ------------------------
DATA_DIR = os.path.dirname(__file__)  # così funziona ovunque tu metta il file
stops = pd.read_csv(os.path.join(DATA_DIR, "stops.txt"))
trips = pd.read_csv(os.path.join(DATA_DIR, "trips.txt"))
stop_times = pd.read_csv(os.path.join(DATA_DIR, "stop_times.txt"))
shapes = pd.read_csv("shapes.txt", dtype={"shape_id": str})

routes = pd.read_csv(os.path.join(DATA_DIR, "routes.txt"))

@app.get("/")
def read_root():
    return {"message": "🚍 API Conerobus attiva! Visita /routes, /stops/{route_id}, /shapes/{shape_id}"}

# ------------------------
# API - Elenco linee
# ------------------------
@app.get("/routes")
def get_routes():
    return routes[["route_id", "route_long_name"]].to_dict(orient="records")


# ------------------------
# API - Fermate per linea
# ------------------------
@app.get("/stops/{route_id}")
def get_stops_by_route(route_id: str):
    # Trova i trip per quella route
    route_trips = trips[trips["route_id"] == route_id]
    if route_trips.empty:
        raise HTTPException(status_code=404, detail="Linea non trovata")

    trip_ids = route_trips["trip_id"].unique()
    stops_for_route = stop_times[stop_times["trip_id"].isin(trip_ids)]
    merged = stops_for_route.merge(stops, on="stop_id", how="left")

    merged = merged.sort_values("stop_sequence")
    merged["shape_id"] = route_trips["shape_id"].iloc[0]  # aggiunge shape_id alla risposta
merged = merged[["stop_id", "stop_name", "stop_lat", "stop_lon", "arrival_time", "shape_id"]].drop_duplicates()


    return merged.to_dict(orient="records")


# ------------------------
# API - Shape (percorso) per shape_id
# ------------------------
@app.get("/shapes/{shape_id}")
def get_shape(shape_id: str):
    shape = shapes[shapes["shape_id"] == shape_id]
    if shape.empty:
        raise HTTPException(status_code=404, detail="Percorso non trovato")

    shape = shape.sort_values("shape_pt_sequence")
    return shape[["shape_pt_lat", "shape_pt_lon"]].rename(
        columns={"shape_pt_lat": "lat", "shape_pt_lon": "lon"}
    ).to_dict(orient="records")



