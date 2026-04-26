from .BioprintingPlugin import BioprintingPlugin


def getMetaData():
    return {}


def register(app):
    return {"extension": BioprintingPlugin()}
