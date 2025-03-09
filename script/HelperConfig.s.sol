// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import {Script} from "../lib/forge-std/src/Script.sol";
import {MockV3Aggregator} from "../test/mocks/MockV3Aggregator.sol";
// 1. Deploy mocks when we are on a local anvil chain
// 2. Keep track of contract address accross different chain

contract HelperConfig is Script {
    struct NetworkConfig {
        address priceFeed; //ETH/USD price feed address
    }

    uint8 public constant DECIMALS = 8;
    int256 public constant INITIAL_ETH_PRICE = 2500e8;

    NetworkConfig public activeNetworkConfig;
    mapping(uint256 => address) private chainIdToPriceFeed;

    constructor() {
        // Initialize the mapping with chain IDs and their respective price feeds
        chainIdToPriceFeed[1] = 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419; // Ethereum Mainnet
        chainIdToPriceFeed[11155111] = 0x694AA1769357215DE4FAC081bf1f309aDC325306; // Ethereum Sepolia
        chainIdToPriceFeed[324] = 0x6D41d1dc818112880b40e26BD6FD347E41008eDA; // Zksync Era Mainnet
        chainIdToPriceFeed[300] = 0xfEefF7c3fB57d18C5C6Cdd71e45D2D0b4F9377bF; // Zksync Sepolia
        chainIdToPriceFeed[137] = 0xF9680D99D6C9589e2a93a78A04A279e509205945; // Polygon Mainnet
        chainIdToPriceFeed[80002] = 0xF0d50568e3A7e8259E16663972b11910F89BD8e7; // Amoy Testnet

        // Get the price feed for current chain, or use Anvil config if not found
        address priceFeed = chainIdToPriceFeed[block.chainid];

        activeNetworkConfig = priceFeed != address(0) ? getEvmConfig(priceFeed) : getAnvilConfig();
    }

    function getAnvilConfig() private returns (NetworkConfig memory) {
        vm.startBroadcast();
        MockV3Aggregator mockV3Aggregator =
            new MockV3Aggregator({_decimals: DECIMALS, _initialAnswer: INITIAL_ETH_PRICE});
        vm.stopBroadcast();
        return NetworkConfig({priceFeed: address(mockV3Aggregator)});
    }

    function getEvmConfig(address priceFeed) private pure returns (NetworkConfig memory) {
        return NetworkConfig({priceFeed: priceFeed});
    }

    function isSupportedNetwork() public view returns (bool) {
        return chainIdToPriceFeed[block.chainid] != address(0) || block.chainid == 31337;
    }
}
