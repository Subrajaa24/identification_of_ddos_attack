import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_data, filter_data, get_stats, plot_energy_consumption, plot_attack_distribution
from blockchain import display_blockchain_info, display_blockchain_data_entry

# Set page configuration
st.set_page_config(
    page_title="WSN Security Analysis Dashboard",
    page_icon="🔒",
    layout="wide"
)

# Application title and description
st.title("Wireless Sensor Network Blockchain Security Dashboard")
st.markdown("""
This user dashboard provides visualization and analysis tools for detecting and investigating 
security attacks in Wireless Sensor Networks (WSN), with blockchain integration for secure 
data storage and verification.
""")

# Sidebar for data upload and controls
with st.sidebar:
    st.header("Data Controls")
    
    # Data upload section
    uploaded_file = st.file_uploader("Upload WSN dataset (CSV)", type=["csv"])
    
    # Load demo data option
    use_demo_data = st.checkbox("Use demo data", value=True if not uploaded_file else False)
    
    st.divider()

# Main content
# Create tabs for different parts of the dashboard
main_tabs = st.tabs(["WSN Analysis", "Blockchain Integration"])

with main_tabs[0]:  # WSN Analysis Tab
    if uploaded_file or use_demo_data:
        # Load data
        if uploaded_file:
            df = load_data(uploaded_file)
            st.success("Dataset successfully loaded from uploaded file!")
        else:
            # Use demo/sample data path
            st.info("Using demo dataset (WSNBFSFdataset.csv)")
            try:
                df = load_data("C:/Users/Subrajaa/OneDrive/Documents/Mini Project/Identification of ddos/SmartStudyTracker/WSNBFSFdataset.csv")
            except FileNotFoundError:
                st.error("Demo dataset not found. Please upload a dataset.")
                st.stop()

with main_tabs[1]:  # Blockchain Integration Tab
    st.header("Blockchain Integration")
    
    # Display blockchain information
    display_blockchain_info()
    
    # Option to send data to blockchain
    if 'df' in locals():
        display_blockchain_data_entry(df)
    else:
        st.warning("Please load a dataset in the WSN Analysis tab first to use blockchain features.")

# Continue with main content only if data is loaded
if uploaded_file or use_demo_data:
    
    # Display basic dataset information
    st.header("Dataset Overview")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Basic Statistics", "Attack Analysis", "Energy Analysis", "Node Analysis"])
    
    with tab1:
        # Show dataset preview
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
        
        # Display dataset statistics
        st.subheader("Dataset Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Records", df.shape[0])
            st.metric("Unique Nodes", df['Node_id'].nunique())
            st.metric("Time Range", f"{df['Time'].min():.2f} - {df['Time'].max():.2f}")
            
        with col2:
            # Calculate attack statistics
            attack_counts = df['Class'].value_counts()
            normal_count = attack_counts.get('normal', 0)
            blackhole_count = attack_counts.get('Blackhole', 0)
            forwarding_count = attack_counts.get('Forwarding', 0)
            
            st.metric("Normal Events", normal_count)
            st.metric("Blackhole Attacks", blackhole_count)
            st.metric("Forwarding Attacks", forwarding_count)
        
        # Display data types and missing values
        st.subheader("Data Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("Data Types:")
            st.write(df.dtypes)
        
        with col2:
            st.write("Missing Values:")
            st.write(df.isnull().sum())
    
    with tab2:
        st.subheader("Attack Analysis")
        
        # Attack distribution pie chart
        st.write("Attack Class Distribution")
        
        # Using plotly for interactive pie chart
        fig = px.pie(
            df, 
            names='Class', 
            title='Distribution of Event Classes',
            color='Class',
            color_discrete_map={
                'normal': 'green',
                'Blackhole': 'red',
                'Forwarding': 'orange'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Attack events over time
        st.write("Attack Events Over Time")
        
        # Group by time (rounded) and class
        time_class_counts = df.groupby([df['Time'].round(1), 'Class']).size().reset_index(name='Count')
        
        # Plot time series of attacks
        fig = px.line(
            time_class_counts, 
            x='Time', 
            y='Count', 
            color='Class',
            title='Events by Class Over Time',
            color_discrete_map={
                'normal': 'green',
                'Blackhole': 'red',
                'Forwarding': 'orange'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Attack sources analysis
        st.write("Attacking Nodes Analysis")
        
        # Filter only attack data
        attack_data = df[df['Class'] != 'normal']
        if not attack_data.empty:
            # Group attacks by node
            attack_nodes = attack_data.groupby(['Node_id', 'Class']).size().reset_index(name='Count')
            
            # Create bar chart
            fig = px.bar(
                attack_nodes, 
                x='Node_id', 
                y='Count', 
                color='Class',
                title='Attack Events by Node ID',
                color_discrete_map={
                    'Blackhole': 'red',
                    'Forwarding': 'orange'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attack data found in the dataset.")
    
    with tab3:
        st.subheader("Energy Consumption Analysis")
        
        # Energy distribution
        st.write("Energy Distribution by Node Class")
        
        # Create energy boxplot by class
        fig = px.box(
            df, 
            x='Class', 
            y='Rest_Energy', 
            color='Class',
            title='Energy Distribution by Event Class',
            color_discrete_map={
                'normal': 'green',
                'Blackhole': 'red',
                'Forwarding': 'orange'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Energy consumption over time
        st.write("Energy Consumption Over Time")
        
        # Select nodes for analysis
        node_selection = st.multiselect(
            "Select nodes to analyze (leave empty for overall average):",
            options=sorted(df['Node_id'].unique()),
            default=[]
        )
        
        # Filter data based on node selection
        if node_selection:
            energy_data = df[df['Node_id'].isin(node_selection)]
        else:
            energy_data = df
        
        # Group by time (rounded)
        energy_time = energy_data.groupby([energy_data['Time'].round(2), 'Node_id'])['Rest_Energy'].mean().reset_index()
        
        # Plot energy consumption
        fig = px.line(
            energy_time, 
            x='Time', 
            y='Rest_Energy', 
            color='Node_id',
            title='Energy Consumption Over Time',
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Energy consumption heatmap for top nodes
        st.write("Node Energy Consumption Heatmap")
        
        # Get top nodes by event count
        top_n = st.slider("Number of top nodes to display:", 5, 30, 15)
        top_nodes = df['Node_id'].value_counts().nlargest(top_n).index
        
        # Filter data for top nodes
        top_nodes_df = df[df['Node_id'].isin(top_nodes)]
        
        # Create pivot table for energy levels
        energy_pivot = top_nodes_df.pivot_table(
            index='Node_id', 
            columns=pd.cut(top_nodes_df['Time'], bins=10), 
            values='Rest_Energy', 
            aggfunc='mean'
        )
        
        # Plot heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(energy_pivot, cmap="YlGnBu", ax=ax)
        plt.title("Energy Levels Across Time Periods for Top Nodes")
        plt.ylabel("Node ID")
        plt.xlabel("Time Period")
        st.pyplot(fig)
    
    with tab4:
        st.subheader("Node Communication Analysis")
        
        # Node selection
        selected_node = st.selectbox(
            "Select a node to analyze:",
            options=sorted(df['Node_id'].unique())
        )
        
        # Filter data for selected node
        node_data = df[df['Node_id'] == selected_node]
        
        # Display node statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Events", node_data.shape[0])
            
        with col2:
            # Calculate class distribution for the node
            node_class_counts = node_data['Class'].value_counts()
            st.metric("Node Class", 
                      node_data['Class'].iloc[0] if not node_data.empty else "Unknown",
                      delta="Attack Node" if node_data['Class'].iloc[0] != 'normal' else "Normal Node" if not node_data.empty else "")
            
        with col3:
            # Calculate average energy
            avg_energy = node_data['Rest_Energy'].mean() if not node_data.empty else 0
            st.metric("Avg Energy", f"{avg_energy:.2f}")
        
        # Node event timeline
        st.write("Node Event Timeline")
        
        # Create timeline of events
        fig = px.scatter(
            node_data, 
            x='Time', 
            y='Event',
            color='Class', 
            size='Packet_Size',
            hover_data=['Rest_Energy', 'Hop_Count', 'TTL'],
            title=f'Event Timeline for Node {selected_node}',
            color_discrete_map={
                'normal': 'green',
                'Blackhole': 'red',
                'Forwarding': 'orange'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Node communication pattern
        st.write("Node Communication Pattern")
        
        # Create network diagram
        source_communications = node_data[node_data['S_Node'] == selected_node]
        target_communications = df[df['Dest_Node_Num'] == selected_node]
        
        if not source_communications.empty or not target_communications.empty:
            # Create network edges
            edges = []
            
            # Add outgoing communications
            for _, row in source_communications.iterrows():
                edges.append((selected_node, row['Dest_Node_Num'], row['Packet_Size'], row['Class']))
                
            # Add incoming communications
            for _, row in target_communications.iterrows():
                edges.append((row['S_Node'], selected_node, row['Packet_Size'], row['Class']))
            
            # Create edge DataFrame
            if edges:
                edge_df = pd.DataFrame(edges, columns=['Source', 'Target', 'Weight', 'Class'])
                
                # Create network graph
                fig = px.scatter(
                    edge_df,
                    x='Source',
                    y='Target',
                    size='Weight',
                    color='Class',
                    title=f'Communication Pattern for Node {selected_node}',
                    color_discrete_map={
                        'normal': 'green',
                        'Blackhole': 'red',
                        'Forwarding': 'orange'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No communication data found for Node {selected_node}")
        else:
            st.info(f"No communication data found for Node {selected_node}")
    
    # Add filters section in sidebar
    with st.sidebar:
        st.header("Filter Data")
        
        # Time range filter
        st.subheader("Time Range")
        time_min = float(df['Time'].min())
        time_max = float(df['Time'].max())
        time_range = st.slider("Select time range:", 
                              min_value=time_min, 
                              max_value=time_max,
                              value=(time_min, time_max))
        
        # Class filter
        st.subheader("Event Class")
        classes = df['Class'].unique()
        selected_classes = st.multiselect("Select classes:", 
                                         options=classes,
                                         default=classes)
        
        # Apply filters button
        if st.button("Apply Filters"):
            # Filter data based on selections
            filtered_df = df[(df['Time'] >= time_range[0]) & 
                            (df['Time'] <= time_range[1]) &
                            (df['Class'].isin(selected_classes))]
            
            # Update the main display with filtered data
            st.session_state['filtered_df'] = filtered_df
            st.rerun()
        
        # Reset filters
        if st.button("Reset Filters"):
            st.session_state.pop('filtered_df', None)
            st.rerun()
            
        # Export filtered data
        if 'filtered_df' in st.session_state:
            filtered_csv = st.session_state['filtered_df'].to_csv(index=False)
            st.download_button(
                label="Download Filtered Data",
                data=filtered_csv,
                file_name="filtered_wsn_data.csv",
                mime="text/csv"
            )
        
else:
    # Display instructions if no data is loaded
    st.info("Please upload a WSN dataset or use the demo data to begin analysis.")
    
    # Example of expected data format
    st.subheader("Expected Data Format")
    
    example_data = {
        'Event': [1, 2],
        'Time': [0.1, 0.15],
        'S_Node': [79, 78],
        'Node_id': [79, 78],
        'Rest_Energy': [600.0, 599.97],
        'Trace_Level': [5, 5],
        'Class': ['normal', 'Blackhole']
    }
    
    st.dataframe(pd.DataFrame(example_data))
