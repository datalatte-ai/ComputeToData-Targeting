// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

interface IERC721Receiver {
    function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data) external returns(bytes4);
}

interface IERC721 {
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function ownerOf(uint256 tokenId) external view returns (address);
    function approve(address to, uint256 tokenId) external;
    function getApproved(uint256 tokenId) external view returns (address);
    function isApprovedForAll(address owner, address operator) external view returns (bool);
    function setApprovalForAll(address operator, bool approved) external view returns (bool);
}

interface TokenVault {
    function receiveData(address dataNftContract,bool flag_sender) external returns (bool);
}

contract DataNftVault{
    address public owner;
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    uint256 private blockStartContract;
    TokenVault private receiver;
    address private ownerAfterOneYear = 0xc56f81953b34E84dA930F395d458E910B5BC4a0f;
    constructor() {
        blockStartContract = block.timestamp;
        owner = msg.sender;
    }

    function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data) 
    external returns(bytes4) {
        return this.onERC721Received.selector;
    }

    function TransferNft(address nftAddress, address from, uint256 tokenId, address _reciverAddress) public {
        IERC721 nftToken = IERC721(nftAddress);
        receiver = TokenVault(_reciverAddress);
        // Check that the person transferring the token actually owns it or is approved to transfer it
        require(nftToken.ownerOf(tokenId) == from, "ERC721: Transfer of token that is not owned.");
        require(nftToken.getApproved(tokenId) == address(this) || nftToken.isApprovedForAll(from, address(this)), "ERC721: transfer caller is not owner nor approved");
        
        nftToken.safeTransferFrom(from, address(this), tokenId);
        emit Transfer(from, address(this), tokenId);
        receiver.receiveData(address(this), true);
    }

    function ownerofnft(address nftAddress, uint256 tokenId) public view returns (address) {
        IERC721 nftToken = IERC721(nftAddress);
        return nftToken.ownerOf(tokenId);
    }

    modifier onlyOwnerAfterOneYear() {
        require( block.timestamp >=  blockStartContract + 365 days,"not the time to change the owner");
        _;
    }

    function changeTheOwner(address nftAddress,uint256 tokenId) public onlyOwnerAfterOneYear{
        owner = ownerAfterOneYear;
        IERC721 nftToken = IERC721(nftAddress);
        nftToken.safeTransferFrom(address(this), ownerAfterOneYear, tokenId);
        emit Transfer(address(this), ownerAfterOneYear, tokenId);
    }
}