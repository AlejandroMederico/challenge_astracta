import datetime
from langchain.tools import tool


@tool
def clock():
    """Obtiene la hora actual || gets the current time"""
    return str(datetime.datetime.now())
