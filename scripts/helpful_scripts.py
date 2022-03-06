from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENVIRONMENT = ["development", "ganache-local","ganache", "hardhat", "mainnet-fork-dev2"]

def get_account(index=None, id=None):
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT
    ):
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])

    return None