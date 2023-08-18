"""
Document me
"""
from typing import Optional

def call_function(name: Optional[str], data: dict) -> Optional[str]:
    """
    Document me
    """
    func = globals().get(data['notifier'])
    if callable(func):
        return func(name, data)
    return None

def nichinoken(name: Optional[str], data: dict) -> str:
    """
    Document me
    """
    return (
        f"Nichinoken Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} at {data['time']}"
           )

def train(name: Optional[str], data: dict) -> str:
    """
    Document me
    """
    if data['enterexit'] == "入場":
        status = "Entered"
    else:
        status = "Exited"
    return (
        f"Train Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} at {data['time']}\n"
        f"{status} {data['station']}"
           )

def bus(name: Optional[str], data: dict) -> str:
    """
    Document me
    """
    return (f"{name} boarded \n"
            f" the {data['busname']} bound for \n"
            f"{data['destination']} at stop: {data['stop']}\n"
            f"at {data['time']} on {data['date']}"
            )

def gate(name: Optional[str], data: dict) -> str:
    """
    Document me
    """
    return (f"{name} passed the school gate.\n"
            f"{data['date']} at {data['time']}"
            )

def kidzduo(name: Optional[str], data: dict) -> str:
    """
    Document me
    """
    return (
        f"KidzDuo Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} at {data['time']}\n"
        f"KidzDuo{data['enterexit']}"
            )

def tokyoinstitute(name: Optional[str], data: dict) -> str:
    """
    Document me
    """
    return (
        f"{data['location']} Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} {data['enterexit']}"
            )
