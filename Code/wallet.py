import subprocess
import json
from dotenv import load_dotenv
import os
import pprint

from constants import *
# %run constants.py

from web3 import Web3
from eth_account import Account
conn = Web3.HTTPProvider("http://127.0.0.1:8545")
w3 = Web3(conn)

from bit import wif_to_key
key = wif_to_key("")
from bit import PrivateKeyTestnet
from bit import PrivateKey
from bit import Key
from bit.network import NetworkAPI

load_dotenv()
mnemonic=os.getenv("mnemonic")
print(mnemonic)

# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic=mnemonic, numderive=3):
    command = f'./derive -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

#create coins dictionary
coins = {
    "btc":derive_wallets(BTC),
    "eth":derive_wallets(ETH),
    "btc-test":derive_wallets(BTCTEST)}

#print dictionary
pprint.pprint(coins)

#You should now be able to select child accounts, (and thus, private keys) 
# by accessing items in the coins dictionary like so: 
# coins[COINTYPE][INDEX]['privkey']btc_privkey
btc_privkey = coins['btc'][0]['privkey']
eth_privkey = coins['eth'][0]['privkey']
btc_test_privkey = coins['btc-test'][0]['privkey']
print(btc_privkey)
print(eth_privkey)
print(btc_test_privkey)

#priv_key_to_account function to convert privkey strings to account objects that bit or web3.py can use to transact. 
# This function needs the following parameters:
# coin -- the coin type (defined in constants.py)
# priv_key -- the privkey string will be passed through here.
# eth(get address) https://web3js.readthedocs.io/en/v1.2.0/web3-eth-accounts.html#privatekeytoaccount
#btc/testnet(get address) https://ofek.dev/bit/dev/api.html
def priv_key_to_account(coin, priv_key):
    if coin == BTC:
        account_address = PrivateKey(priv_key).address
    elif coin == ETH:
        account_address = Account.privateKeyToAccount(priv_key).address
    elif coin == BTCTEST:
        account_address = PrivateKeyTestnet(priv_key).address
    return account_address

#test out the function here:
print('BTC Account Address: ' + (priv_key_to_account(BTC, btc_privkey)))

print('ETH Account Address: ' + (priv_key_to_account(ETH, eth_privkey)))

print('BTC-TEST Account Address: ' + (priv_key_to_account(BTCTEST,btc_test_privkey)))

#create_tx function; this function will create the raw, unsigned transaction that contains all metadata needed to transact.
# parameters: coin, account, to, amount
#You will need to check the coin type, then return one of the following functions based on the library:

def create_tx(coin, account, recipient, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        return {
            "from": account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": web3.eth.net.getID([callback])
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

    
# This function will call create_tx, sign the transaction, then send it to the designated network.
# parameters (coin, account,
def send_tx(coin, account, recipient, amount):
    tx = create_tx(account_address, recipient, amount)
    if coin == ETH:
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        tx = create_tx(account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        print(signed_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
        
        
#BTCTEST create, send tx to another BTCTEST account!
#get btctest account address
btctest_acc = priv_key_to_account(BTCTEST, btc_test_privkey)
recipient =  tb1ql7w62elx9ucw4pj5lgw4l028hmuw80sndtntxt

#create btctest tx (send to child account)
create_tx(BTCTEST, btctest_acc, recipient, 0.0015)

#send the tx
send_tx(BTCTEST, btctest_acc, recipient, 0.0015)
