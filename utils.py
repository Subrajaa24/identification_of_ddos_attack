import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    """
    Load and preprocess the WSN dataset
    
    Parameters:
    file_path (str or file object): Path to the CSV file or uploaded file object
    
    Returns:
    pd.DataFrame: Processed dataframe
    """
    try:
        # Load the dataset
        df = pd.read_csv(file_path)
        
        # Check if the expected columns are present
        expected_columns = [
            'Event', 'Time', 'S_Node', 'Node_id', 'Rest_Energy', 
            'Trace_Level', 'Mac_Type_Pckt', 'Source_IP_Port', 
            'Des_IP_Port', 'Packet_Size', 'TTL', 'Hop_Count', 
            'Broadcast_ID', 'Dest_Node_Num', 'Dest_Seq_Num', 
            'Src_Node_ID', 'Src_Seq_Num', 'Class'
        ]
        
        # Ensure all necessary columns exist
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convert columns to appropriate data types
        df['Event'] = df['Event'].astype(int)
        df['Time'] = df['Time'].astype(float)
        df['S_Node'] = df['S_Node'].astype(int)
        df['Node_id'] = df['Node_id'].astype(int)
        df['Rest_Energy'] = df['Rest_Energy'].astype(float)
        df['Class'] = df['Class'].astype(str)
        
        return df
    
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")

def filter_data(df, time_range=None, node_ids=None, classes=None):
    """
    Filter the dataset based on specified criteria
    
    Parameters:
    df (pd.DataFrame): Input dataframe
    time_range (tuple): (min_time, max_time)
    node_ids (list): List of node IDs to include
    classes (list): List of classes to include
    
    Returns:
    pd.DataFrame: Filtered dataframe
    """
    filtered_df = df.copy()
    
    # Apply time range filter
    if time_range:
        min_time, max_time = time_range
        filtered_df = filtered_df[(filtered_df['Time'] >= min_time) & 
                                 (filtered_df['Time'] <= max_time)]
    
    # Apply node filter
    if node_ids:
        filtered_df = filtered_df[filtered_df['Node_id'].isin(node_ids)]
    
    # Apply class filter
    if classes:
        filtered_df = filtered_df[filtered_df['Class'].isin(classes)]
    
    return filtered_df

def get_stats(df):
    """
    Calculate basic statistics from the dataset
    
    Parameters:
    df (pd.DataFrame): Input dataframe
    
    Returns:
    dict: Dictionary of statistics
    """
    stats = {
        'total_records': df.shape[0],
        'unique_nodes': df['Node_id'].nunique(),
        'time_range': (df['Time'].min(), df['Time'].max()),
        'class_distribution': df['Class'].value_counts().to_dict(),
        'avg_energy': df['Rest_Energy'].mean(),
        'min_energy': df['Rest_Energy'].min(),
        'max_energy': df['Rest_Energy'].max(),
    }
    
    return stats

def plot_energy_consumption(df, node_ids=None):
    """
    Generate energy consumption visualization
    
    Parameters:
    df (pd.DataFrame): Input dataframe
    node_ids (list): List of node IDs to include
    
    Returns:
    plotly.graph_objects.Figure: Energy consumption plot
    """
    if node_ids:
        data = df[df['Node_id'].isin(node_ids)]
    else:
        data = df
    
    # Group by time and calculate average energy
    energy_time = data.groupby(
        [pd.cut(data['Time'], bins=50), 'Class']
    )['Rest_Energy'].mean().reset_index()
    
    # Convert interval to midpoint for plotting
    energy_time['Time'] = energy_time['Time'].apply(lambda x: x.mid)
    
    # Create plot
    fig = px.line(
        energy_time, 
        x='Time', 
        y='Rest_Energy', 
        color='Class',
        title='Energy Consumption Over Time',
        labels={'Rest_Energy': 'Average Remaining Energy', 'Time': 'Time'},
        color_discrete_map={
            'normal': 'green',
            'Blackhole': 'red',
            'Forwarding': 'orange'
        }
    )
    
    return fig

def plot_attack_distribution(df):
    """
    Generate attack distribution visualization
    
    Parameters:
    df (pd.DataFrame): Input dataframe
    
    Returns:
    plotly.graph_objects.Figure: Attack distribution plot
    """
    # Count occurrences of each class
    class_counts = df['Class'].value_counts().reset_index()
    class_counts.columns = ['Class', 'Count']
    
    # Create pie chart
    fig = px.pie(
        class_counts, 
        values='Count', 
        names='Class',
        title='Distribution of Event Classes',
        color='Class',
        color_discrete_map={
            'normal': 'green',
            'Blackhole': 'red',
            'Forwarding': 'orange'
        }
    )
    
    return fig
