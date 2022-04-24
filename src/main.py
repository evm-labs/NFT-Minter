from snipe_setup import generate_snipe_tx, sign_tx, send_tx, get_receipt, variables_for_listening, listen_and_release
from transact_setup import generate_transact_tx
from secrets import WALLETS
from config import WALLET, TYPE, Web3Instance
import asyncio


async def snipe():
    tx, starting_nonce, tx_error = generate_snipe_tx()
    if tx_error:
        raise RuntimeError(tx_error)
    signed_tx, signature_error = sign_tx(tx, WALLETS[WALLET]['private'])
    if signature_error:
        raise RuntimeError(signature_error)


    print("Transaction now generated and signed. Shall the process run? (y/n)")
    execute = input()
    if execute == 'n':
        raise RuntimeError("The process has now been stopped by user.")

    sent_tx, send_error = await send_tx(signed_tx)
    if send_error:
        raise RuntimeError(send_error)
    else:
        print("Transaction sent.")
    tx_receipt, tx_nonce, tx_fee = get_receipt(sent_tx.__dict__["result"]["txHash"])

    print(f"Transaction hash is {sent_tx.__dict__['result']['txHash']}")
    if tx_nonce - starting_nonce == 1:
        if tx_receipt.__dict__["status"] == 1:
            print(f"Successful transaction. Gas paid was {tx_fee} ETH.")
        else:
            print("Transaction was not successful, or not completed within 45 seconds.")
    else:
        print("Transaction was not successful, or not completed within 45 seconds.")


def transact():
    tx, starting_nonce, tx_error = generate_transact_tx()
    if tx_error:
        raise RuntimeError(tx_error)
    signed_tx, signature_error = sign_tx(tx, WALLETS[WALLET]['private'])
    if signature_error:
        raise RuntimeError(signature_error)
    sent_tx, send_error = send_tx(signed_tx)
    if send_error:
        raise RuntimeError(send_error)
    else:
        print("Transaction sent.")
    tx_receipt, tx_nonce, tx_fee = get_receipt(sent_tx)

    print(f"Transaction hash is {sent_tx}")
    if tx_nonce - starting_nonce == 1:
        if tx_receipt.__dict__["status"] == 1:
            print(f"Successful transaction. Gas paid was {tx_fee} ETH.")
        else:
            print("Transaction was not successful.")


if __name__ == '__main__':
    if TYPE == 'Snipe':
        asyncio.run(snipe())
    elif TYPE == 'Transact':
        transact()

