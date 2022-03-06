from scripts.helpful_scripts import get_account
from brownie import interface, config, network

def main():
    getWeth()

def getWeth():
    """
    Mints WETH by depositing ETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from" : account, "value": 0.1 * 10 **17})
    tx.wait(1)
    print("0.01 weth recu")
    return tx