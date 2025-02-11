from web3 import AsyncWeb3, AsyncHTTPProvider
from config import (
    rpc_url,
    UNISWAP_ROUTER_CONTRACT_ADDRESS_V3,
    UNISWAP_ROUTER_CONTRACT_ABI_V3,
    UNISWAP_ROUTER_CONTRACT_ADDRESS_V2,
    UNISWAP_ROUTER_CONTRACT_ABI_V2,
    AMOUNT_TO_SWAP,
    WETH_CONTRACT_ADDRESS
)
import time
from loguru import logger


class Sniper:
    def __init__(self, private_key: str):
        self.rpc = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.uniswap_instance_v3 = self.rpc.eth.contract(
            address=UNISWAP_ROUTER_CONTRACT_ADDRESS_V3,
            abi=UNISWAP_ROUTER_CONTRACT_ABI_V3
        )
        self.uniswap_instance_v2 = self.rpc.eth.contract(
            address=UNISWAP_ROUTER_CONTRACT_ADDRESS_V2,
            abi=UNISWAP_ROUTER_CONTRACT_ABI_V2
        )
        self.private_key = private_key
        self.account = self.rpc.eth.account.from_key(self.private_key)

    async def snipe_token_v3(self, token_address):
        try:
            params = {
                'tokenIn': AsyncWeb3.to_checksum_address(WETH_CONTRACT_ADDRESS),
                'tokenOut': AsyncWeb3.to_checksum_address(token_address),
                'fee': 10000,
                'recipient': self.account.address,
                'deadline': int(time.time()) + 300,
                'amountIn': self.rpc.to_wei(AMOUNT_TO_SWAP, 'ether'),
                'amountOutMinimum': 0,
                'sqrtPriceLimitX96': 0,
            }

            block_data = await self.rpc.eth.get_block('latest')
            base_fee = block_data['baseFeePerGas']
            max_fee_per_gas = 6 * base_fee
            max_priority_fee_per_gas = int(0.5 * (max_fee_per_gas - base_fee))

            txn = await self.uniswap_instance_v3.functions.exactInputSingle(params).build_transaction({
                'from': self.account.address,
                'value': self.rpc.to_wei(AMOUNT_TO_SWAP, 'ether'),
                'maxFeePerGas': int(max_fee_per_gas),
                'maxPriorityFeePerGas': int(max_priority_fee_per_gas),
                'gas': 300000,
                'nonce': await self.rpc.eth.get_transaction_count(self.account.address)
            })
            logger.info(f"Trying to snipe with v3")
            estimate_gas = await self.rpc.eth.estimate_gas(txn)
            txn.update({'gas': int(estimate_gas * 1.2)})

            signed_txn = self.rpc.eth.account.sign_transaction(txn, self.private_key)
            txn_hash = await self.rpc.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = await self.rpc.eth.wait_for_transaction_receipt(txn_hash, timeout=360)
            
            if receipt['status'] == 1:
                logger.success(f"Transaction successful! Hash: {txn_hash.hex()}")
            else:
                logger.error(f"Transaction failed! Hash: {txn_hash.hex()}")
                raise
            return txn_hash.hex()
        except Exception as e:
            logger.error(f"Problem while sniping with v3")
            raise e

    async def snipe_token_v2(self, token_address):
        try:
            block_data = await self.rpc.eth.get_block('latest')
            base_fee = block_data['baseFeePerGas']
            max_fee_per_gas = 6 * base_fee
            max_priority_fee_per_gas = int(0.5 * (max_fee_per_gas - base_fee))

            txn = await self.uniswap_instance_v2.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                0,
                [AsyncWeb3.to_checksum_address(WETH_CONTRACT_ADDRESS),
                 AsyncWeb3.to_checksum_address(token_address)],
                self.account.address,
                int(time.time()) + 300
            ).build_transaction({
                'from': self.account.address,
                'value': self.rpc.to_wei(AMOUNT_TO_SWAP, 'ether'),
                'maxFeePerGas': int(max_fee_per_gas),
                'maxPriorityFeePerGas': int(max_priority_fee_per_gas),
                'gas': 300000,
                'nonce': await self.rpc.eth.get_transaction_count(self.account.address)
            })
            logger.info(f"Trying to snipe with v2")
            estimate_gas = await self.rpc.eth.estimate_gas(txn)
            txn.update({'gas': int(estimate_gas * 1.2)})

            signed_txn = self.rpc.eth.account.sign_transaction(txn, self.private_key)
            txn_hash = await self.rpc.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = await self.rpc.eth.wait_for_transaction_receipt(txn_hash, timeout=360)
            
            if receipt['status'] == 1:
                logger.success(f"Transaction successful! Hash: {txn_hash.hex()}")
            else:
                logger.error(f"Transaction failed! Hash: {txn_hash.hex()}")
                raise
            return txn_hash.hex()
        except Exception as e:
            logger.error(f"Problem while sniping with v2")
            logger.error("g1g")