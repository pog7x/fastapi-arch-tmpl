import json
import random
from typing import Dict, List

from fastapi import FastAPI

app = FastAPI()

with open("./random_coffee.json", "r", encoding="utf-8") as coffee_file:
    json_data: List[Dict] = json.load(coffee_file)


@app.get("/random_coffee/")
def random_coffee():
    return random.choice(json_data)
