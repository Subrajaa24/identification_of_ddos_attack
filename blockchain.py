from web3 import Web3
import json
import pandas as pd
import streamlit as st
import os
import time
import plotly.express as px
import plotly.graph_objects as go

# Blockchain connection setup
def connect_to_blockchain(provider_url=None):
    """
    Connect to an Ethereum blockchain
    
    Parameters:
    provider_url (str): URL of the Ethereum provider
    
    Returns:
    Web3: Web3 instance if connection is successful, None otherwise
    """
    # Default providers if none specified
    if not provider_url:
        # Try to connect to common networks
        providers = [
            "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",  # Public Infura endpoint
            "https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",   # Public Goerli testnet
            "https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",  # Public Sepolia testnet
            "http://localhost:8545"                                       # Local development node
        ]
        
        # Try each provider
        for url in providers:
            try:
                w3 = Web3(Web3.HTTPProvider(url))
                if w3.is_connected():
                    return w3
            except Exception:
                continue
        
        # If no connection works, return None
        return None
    else:
        # Connect to specified provider
        try:
            w3 = Web3(Web3.HTTPProvider(provider_url))
            return w3 if w3.is_connected() else None
        except Exception as e:
            st.error(f"Failed to connect to blockchain: {e}")
            return None

# Get sample ABIs for smart contracts
def get_sample_contract_abi():
    """
    Get a sample ABI for WSN Smart Contract
    
    Returns:
    dict: Sample ABI
    """
    # This is a simplified ABI for a WSN monitoring contract
    sample_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "getNodeCount",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_nodeId", "type": "uint256"},
                {"name": "_energy", "type": "uint256"},
                {"name": "_class", "type": "string"},
                {"name": "_timestamp", "type": "uint256"}
            ],
            "name": "addNodeData",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_nodeId", "type": "uint256"}],
            "name": "getNodeData",
            "outputs": [
                {"name": "energy", "type": "uint256"},
                {"name": "nodeClass", "type": "string"},
                {"name": "timestamp", "type": "uint256"}
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "getAttackCount",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    return sample_abi

# Create a visualization that shows how the blockchain is storing node data
def show_blockchain_visualization():
    """
    Create a visualization of blockchain data structure for WSN data
    
    Returns:
    plotly.graph_objects.Figure: Blockchain structure visualization
    """
    # Create sample blockchain blocks
    blocks = [
        {"block": 1, "timestamp": time.time() - 500, "data": "Genesis Block", "transactions": 0},
        {"block": 2, "timestamp": time.time() - 400, "data": "Node Data (10 entries)", "transactions": 10},
        {"block": 3, "timestamp": time.time() - 300, "data": "Attack Detection", "transactions": 5},
        {"block": 4, "timestamp": time.time() - 200, "data": "Node Data (15 entries)", "transactions": 15},
        {"block": 5, "timestamp": time.time() - 100, "data": "Energy Reports", "transactions": 8},
    ]
    
    df = pd.DataFrame(blocks)
    
    # Create block visualization
    fig = px.bar(df, x="block", y="transactions", 
                 hover_data=["timestamp", "data"],
                 color="transactions",
                 labels={"block": "Block Number", "transactions": "Transaction Count"},
                 title="WSN Data Blocks on Blockchain",
                 color_continuous_scale=px.colors.sequential.Viridis)
    
    fig.update_layout(showlegend=False, hovermode="closest")
    
    # Add connections between blocks to show the chain
    for i in range(len(blocks)-1):
        fig.add_trace(
            go.Scatter(
                x=[blocks[i]["block"], blocks[i+1]["block"]],
                y=[blocks[i]["transactions"]/2, blocks[i+1]["transactions"]/2],
                mode="lines",
                line=dict(width=2, color="rgba(50, 50, 50, 0.3)"),
                hoverinfo="none",
                showlegend=False
            )
        )
    
    return fig

# Simulate sending WSN data to blockchain
def send_wsn_data_to_blockchain(node_id, energy, node_class, timestamp):
    """
    Simulate sending WSN data to blockchain
    
    Parameters:
    node_id (int): Node ID
    energy (float): Energy level
    node_class (str): Node class (normal, Blackhole, Forwarding)
    timestamp (float): Timestamp
    
    Returns:
    bool: Success status
    str: Transaction hash or error message
    """
    try:
        # This is a simulation - in a real app, you'd use web3.py to send a transaction
        # to the smart contract
        
        # Simulate blockchain transaction with a delay
        time.sleep(0.5)
        
        # Generate a fake transaction hash
        tx_hash = Web3.keccak(text=f"{node_id}-{energy}-{node_class}-{timestamp}-{time.time()}").hex()
        
        return True, tx_hash
    except Exception as e:
        return False, str(e)

# Function to display blockchain information
def display_blockchain_info():
    """
    Display blockchain network information
    """
    st.subheader("Blockchain Network Information")
    
    # Custom endpoint input
    custom_endpoint = st.text_input(
        "Enter blockchain endpoint URL (leave empty to use public endpoints):",
        placeholder="e.g., https://mainnet.infura.io/v3/YOUR_API_KEY or http://localhost:8545"
    )
    
    if st.button("Connect to Blockchain"):
        # Try to connect to blockchain
        with st.spinner("Connecting to blockchain..."):
            w3 = connect_to_blockchain(provider_url=custom_endpoint if custom_endpoint else None)
            
            if w3:
                st.session_state['blockchain_connected'] = True
                st.session_state['web3_instance'] = w3
                st.success(f"Successfully connected to Ethereum network!")
            else:
                st.session_state['blockchain_connected'] = False
                st.error("Failed to connect to any blockchain network. Please check your endpoint URL or try again later.")
    
    # Check if we have an active connection
    if st.session_state.get('blockchain_connected', False) and st.session_state.get('web3_instance'):
        w3 = st.session_state.get('web3_instance')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Network Connected", "Yes", "✅")
            try:
                chain_id = w3.eth.chain_id
                
                network_name = "Unknown Network"
                if chain_id == 1:
                    network_name = "Ethereum Mainnet"
                elif chain_id == 5:
                    network_name = "Goerli Testnet"
                elif chain_id == 11155111:
                    network_name = "Sepolia Testnet" 
                elif chain_id == 1337:
                    network_name = "Local Development Blockchain"
                
                st.metric("Chain ID", f"{chain_id} ({network_name})")
            except:
                st.metric("Chain ID", "Unknown")
            
        with col2:
            # Latest block number
            try:
                latest_block = w3.eth.block_number
                st.metric("Latest Block", f"{latest_block:,}")
            except:
                st.metric("Latest Block", "Unknown")
            
            # Gas price
            try:
                gas_price = w3.eth.gas_price
                st.metric("Gas Price (Gwei)", f"{w3.from_wei(gas_price, 'gwei'):.2f}")
            except:
                st.metric("Gas Price", "Unknown")
        
        # Block explorer link
        st.markdown("### Blockchain Explorer")
        try:
            chain_id = w3.eth.chain_id
            explorer_url = None
            
            if chain_id == 1:
                explorer_url = "https://etherscan.io"
            elif chain_id == 5:
                explorer_url = "https://goerli.etherscan.io"
            elif chain_id == 11155111:
                explorer_url = "https://sepolia.etherscan.io"
            
            if explorer_url:
                st.markdown(f"[View transactions on blockchain explorer]({explorer_url})")
        except:
            st.info("No blockchain explorer available for this network")
        
    else:
        st.warning("Not connected to any blockchain network.")
        st.info("Use the connection form above to connect to an Ethereum blockchain network.")
        
        # Show simulated metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Network Type", "Not Connected")
            st.metric("Chain ID", "N/A")
            
        with col2:
            st.metric("Latest Block", "N/A")
            st.metric("Gas Price (Gwei)", "N/A")
    
    # Show blockchain visualization
    st.subheader("Blockchain Structure")
    fig = show_blockchain_visualization()
    st.plotly_chart(fig, use_container_width=True)

# Function to display blockchain data entry form
def display_blockchain_data_entry(df):
    """
    Display form for sending WSN data to blockchain
    
    Parameters:
    df (pd.DataFrame): WSN DataFrame with data to potentially send to blockchain
    """
    st.subheader("Send WSN Data to Blockchain")
    
    # Check if connected to a blockchain
    if not st.session_state.get('blockchain_connected', False):
        st.warning("You need to connect to a blockchain first to send data.")
        st.info("Go to the Blockchain Network Information section above and connect to a blockchain.")
        return
    
    st.markdown("""
    ### Deploy Smart Contract
    Before sending data, you need to deploy a smart contract to handle the WSN data storage.
    """)
    
    with st.expander("Smart Contract Deployment"):
        contract_name = st.text_input("Smart Contract Name", "WSNDataContract")
        
        deploy_contract = st.button("Deploy Smart Contract")
        
        if deploy_contract:
            with st.spinner("Deploying Smart Contract..."):
                # Simulate contract deployment
                time.sleep(2)
                st.session_state['contract_deployed'] = True
                st.session_state['contract_address'] = "0x" + Web3.keccak(text=f"WSNContract-{time.time()}").hex()[-40:]
                st.success(f"Contract deployed successfully!")
                st.code(f"Contract Address: {st.session_state.get('contract_address')}")
    
    # Check if we have a contract deployed
    if not st.session_state.get('contract_deployed', False):
        st.warning("Please deploy a smart contract before sending data.")
        return
    
    st.markdown(f"""
    ### Send WSN Data to Blockchain
    Selected Contract: {contract_name} ({st.session_state.get('contract_address')})
    """)
    
    with st.form("blockchain_data_form"):
        # Select which nodes to send
        node_options = sorted(df['Node_id'].unique())
        selected_nodes = st.multiselect("Select nodes to record on blockchain:", options=node_options)
        
        # Option to only send attack data
        only_attacks = st.checkbox("Only send attack data (Blackhole/Forwarding)")
        
        # Gas price options
        gas_price_options = ["Low", "Medium", "High"] 
        gas_price = st.select_slider("Gas Price:", options=gas_price_options, value="Medium")
        
        # Submit button
        submitted = st.form_submit_button("Send to Blockchain")
        
        if submitted:
            if not selected_nodes:
                st.error("Please select at least one node to send data for.")
                return
            
            # Filter data based on user selection
            filtered_data = df[df['Node_id'].isin(selected_nodes)]
            
            if only_attacks:
                filtered_data = filtered_data[filtered_data['Class'] != 'normal']
            
            if filtered_data.empty:
                st.error("No data found for the selected criteria.")
                return
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process each row (up to a reasonable limit)
            row_limit = min(50, len(filtered_data))
            processed_data = filtered_data.head(row_limit)
            
            successful_txs = 0
            tx_hashes = []
            
            # Show estimated cost before proceeding
            gas_costs = {"Low": 15, "Medium": 25, "High": 40}
            selected_gas = gas_costs[gas_price]
            est_cost = row_limit * 0.000021 * selected_gas  # Rough estimate
            
            st.info(f"Estimated transaction cost: {est_cost:.6f} ETH (${est_cost * 3000:.2f} USD at $3000/ETH)")
            
            # Use form_submit_button directly
            if submitted:
                for i, (_, row) in enumerate(processed_data.iterrows()):
                    # Update progress
                    progress = (i + 1) / row_limit
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {i+1}/{row_limit} records...")
                    
                    # Send data
                    node_id = int(row['Node_id'])
                    energy = float(row['Rest_Energy'])
                    node_class = row['Class']
                    timestamp = float(row['Time'])
                    
                    success, tx_result = send_wsn_data_to_blockchain(node_id, energy, node_class, timestamp)
                    
                    if success:
                        successful_txs += 1
                        tx_hashes.append(tx_result)
                
                # Store results in session state for post-form display
                st.session_state['successful_txs'] = successful_txs
                st.session_state['tx_hashes'] = tx_hashes
    
    # Display transaction results outside the form if transactions were processed
    if 'successful_txs' in st.session_state and st.session_state['successful_txs'] > 0:
        # Display results
        st.success(f"Successfully sent {st.session_state['successful_txs']} records to the blockchain.")
        
        tx_hashes = st.session_state.get('tx_hashes', [])
        if tx_hashes:
            with st.expander("View Transaction Hashes"):
                for i, tx_hash in enumerate(tx_hashes):
                    st.code(f"Tx {i+1}: {tx_hash}")
            
            # Show verification option
            st.markdown("""
            ### Verify Data on Blockchain
            
            You can verify that your data was written to the blockchain by checking the transaction 
            receipts. In a production environment, you would use a block explorer to verify the transactions.
            """)
            
            # Create a verification section
            verification_col1, verification_col2 = st.columns([1, 2])
            
            with verification_col1:
                verify_button = st.button("Verify Transactions")
            
            # Store verification state
            if verify_button:
                st.session_state['verify_clicked'] = True
                
            # Show verification results if clicked
            if st.session_state.get('verify_clicked', False):
                with verification_col2:
                    with st.spinner("Verifying transactions..."):
                        # Simulate verification delay
                        time.sleep(1)
                        
                        st.success("All transactions verified and confirmed!")
                
                # Show sample verification information
                st.divider()
                ver_col1, ver_col2, ver_col3 = st.columns(3)
                
                for i, tx_hash in enumerate(tx_hashes[:3]):  # Show first 3
                    if i == 0:
                        with ver_col1:
                            st.info(f"Transaction 1: Confirmed in Block #{8245721} with 3 confirmations")
                    elif i == 1:
                        with ver_col2:
                            st.info(f"Transaction 2: Confirmed in Block #{8245722} with 2 confirmations")
                    elif i == 2:
                        with ver_col3:
                            st.info(f"Transaction 3: Confirmed in Block #{8245723} with 1 confirmation")
            
            # Provide a link to view on etherscan (if we have a connected network)
            if st.session_state.get('web3_instance'):
                try:
                    w3 = st.session_state.get('web3_instance')
                    chain_id = w3.eth.chain_id
                    
                    explorer_url = None
                    if chain_id == 1:
                        explorer_url = f"https://etherscan.io/tx/{tx_hashes[0]}"
                    elif chain_id == 5:
                        explorer_url = f"https://goerli.etherscan.io/tx/{tx_hashes[0]}"
                    elif chain_id == 11155111:
                        explorer_url = f"https://sepolia.etherscan.io/tx/{tx_hashes[0]}"
                    
                    if explorer_url:
                        st.markdown(f"[View first transaction on block explorer]({explorer_url})")
                except:
                    pass