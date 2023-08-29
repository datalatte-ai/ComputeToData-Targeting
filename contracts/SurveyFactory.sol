pragma solidity 0.8.19;
//SPDX-License-Identifier: MIT

interface OPFactory {
    struct NftCreateData {
        string name;
        string symbol;
        uint256 templateIndex;
        string tokenURI;
        bool transferable;
        address owner;
    }

    struct ErcCreateData {
        uint256 templateIndex;
        string[] strings;
        address[] addresses;
        uint256[] uints;
        bytes[] bytess;
    }

    function createNftWithErc20(
        NftCreateData calldata _NftCreateData, 
        ErcCreateData calldata _ErcCreateData
    ) external returns (address erc721Address, address erc20Address);

}


contract SurveyFactory {

    /**
    * Events from Ocean Protocol
    * https://github.com/oceanprotocol/contracts/blob/main/contracts/ERC721Factory.sol#L62
    */

    event TokenCreated(
        address indexed newTokenAddress,
        address indexed templateAddress,
        string name,
        string symbol,
        uint256 cap,
        address creator
    );  
    
    event NFTCreated(
        address newTokenAddress,
        address indexed templateAddress,
        string tokenName,
        address indexed admin,
        string symbol,
        string tokenURI,
        bool transferable,
        address indexed creator
    );

    /// Ocean Protocol contract
    OPFactory oceanFactory;
    address private owner;
    /// @notice Constructor to initialize the 
    /// @param oceanFactoryAddress Ocean Factory's address
    constructor(address oceanFactoryAddress) {
        oceanFactory = OPFactory(oceanFactoryAddress);
        owner = msg.sender;
    }

    function createNftWithErc20(OPFactory.NftCreateData calldata nftData, OPFactory.ErcCreateData calldata ercData) public {
        oceanFactory.createNftWithErc20(nftData, ercData);        
    }
}