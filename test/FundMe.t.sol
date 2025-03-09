// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import {FundMe} from "../src/FundMe.sol";
import {DeployFundMe} from "../script/DeployFundMe.s.sol";

contract FundMeTest is Test {
    FundMe private fundMe;
    address constant PRICE_FEED_ADDRESS = 0x694AA1769357215DE4FAC081bf1f309aDC325306; //Sepolia ETH/USD

    function setUp() external {
        DeployFundMe deployer = new DeployFundMe();
        fundMe = deployer.run();
    }

    function testMinimumDollarIsFive() public view {
        assertEq(fundMe.MINIMUM_USD(), 5e18);
    }

    function testOwnerIsMsgSender() public view {
        console2.log("Sender:", msg.sender);
        console2.log("Owner:", fundMe.getOwner());
        assertEq(fundMe.getOwner(), msg.sender);
    }

    function testPriceFeedVersionIsAccurate() public view {
        uint256 version = fundMe.getVersion();
        console2.log("Version:", version);
        assert(version >= 1);
    }
}
