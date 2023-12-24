class Account:
    def __init__(self, PK, RPCProvider) -> None:
        self.account = RPCProvider.w3.eth.account.from_key(PK)
        self.address = self.account.address
        self.key = self.account.key
        self.nonce = 0
    
    def update_nonce(self, RPCProvider):
        self.nonce = RPCProvider.w3.eth.get_transaction_count(self.address, "pending")
