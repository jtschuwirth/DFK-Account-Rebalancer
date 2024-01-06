class Token:
    def __init__(self, item, chain, address, decimals, event_filter) -> None:
        self.name = item
        self.chain = chain
        self.address = address
        self.decimals = decimals
        self.event_filter = event_filter
    