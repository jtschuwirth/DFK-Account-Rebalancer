import json

decimalsJson = open("data/decimals.json")
decimals = json.load(decimalsJson)

itemsJson = open("data/items.json")
items = json.load(itemsJson)

class Token:
    def __init__(self, item, chain, event_filter) -> None:
        self.name = item
        self.address = items[item][chain]
        self.decimals = decimals[item] if item in decimals else 0
        self.event_filter = event_filter