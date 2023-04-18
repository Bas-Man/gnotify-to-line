def nichinoken(name: str, data: dict) -> str:
   return (f"{name} Nichinoken.\n"
           f"{data['date']} at {data['time']}"
          )

def train(name: str, data: dict) -> str:
    if data['enterexit'] == "入場":
        status = "Entered"
    else:
        status = "Exited"
    return (f"{name} Train Notification.\n"
            f"{data['date']} at {data['time']}\n"
            f"{status} {data['station']}"
           )

def bus(name: str, data: dict) -> str:
    return (f"{name} boarded \n"
            f" the {data['busname']} bound for \n"
            f"{data['destination']} at stop: {data['stop']}\n"
            f"at {data['time']} on {data['date']}"
            )

def gate(name: str, data: dict) -> str:
    return (f"{name} passed the school gate.\n"
            f"{data['date']} at {data['time']}"
            )

def kidzduo(name: str, data: dict) -> str:
    return (f"{name} KidzDuo notification.\n"
            f"{data['date']} at {data['time']}\n"
            f"KidzDuo{data['enterexit']}"
            )

def institution(name: str, data: dict) -> str:
    return (f"{data['location']} notification\n"
            f"{data['date']} {data['enterexit']}"
            )
