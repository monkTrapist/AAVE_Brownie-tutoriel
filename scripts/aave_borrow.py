from brownie import config, network, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import getWeth
from web3 import Web3

amount = Web3.toWei(0.01, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork-dev2"]:
        getWeth()
    # ABI
    # ADDRESS
    lending_pool = get_lending_pool()
    print(lending_pool)
    # Confirmation du token ERC20 token
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("En train de deposer ...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Depose")
    # combien
    borrowableETH, total_debt = get_borrowable_data(lending_pool, account)
    print("Emprunt DAI")
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowableETH * 0.95)
    print(f"Montant qui sera emprunte {amount_dai_to_borrow} ")
    # emprunt
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("DAI emprunte")
    get_borrowable_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)
    print("Deposer, emprunter, repayer avec AAVE, BROWNIE et Chainlink")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayé")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"Prix DAI/ETH {converted_latest_price}")
    return float(latest_price)


def approve_erc20(amount, spender, erc20_address, account):
    print("Confirmation ERC20 token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approuvé")


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"Vous avez une valeur de  {total_collateral_eth} ETH déposé.")
    print(f"Vous avez une valeur de {total_debt_eth} ETH emprunté.")
    print(f"Vous pouvez emprunter une valeur de {available_borrow_eth} ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_addresses = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_addresses)
    return lending_pool
