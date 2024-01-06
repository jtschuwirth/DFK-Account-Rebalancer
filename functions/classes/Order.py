class Order:
    def __init__(self, id, token, side, price, amount) -> None:
        self.orderId = id
        self.token = token
        self.side = side
        self.price = price
        self.amount = amount