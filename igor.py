import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import cm
import matplotlib.patches as mpatches
import random
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

class HIVGISApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Namibia HIV/AIDS GIS Visualization System")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)
        
        # Load data
        self.load_dummy_data()
        
        # Configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Menu bar
        self.root.rowconfigure(1, weight=1)  # Main content
        
        # Create components
        self.create_menu()
        self.create_notebook()
        
        # Start with the HIV case distribution map
        self.show_hiv_distribution()
        
    def load_dummy_data(self):
        """Generate dummy data for Namibia's regions"""
        # Namibia's administrative regions
        self.regions = [
            "Erongo", "Hardap", "Karas", "Kavango East", "Kavango West",
            "Khomas", "Kunene", "Ohangwena", "Omaheke", "Omusati",
            "Oshana", "Oshikoto", "Otjozondjupa", "Zambezi"
        ]
        
        # Generate dummy HIV cases data
        num_records = 5000
        
        # Generate random dates from 2015 to 2024
        start_date = datetime(2015, 1, 1)
        end_date = datetime(2024, 12, 31)
        days_range = (end_date - start_date).days
        
        self.hiv_data = pd.DataFrame({
            'region': np.random.choice(self.regions, num_records),
            'district': ['District_' + str(random.randint(1, 5)) for _ in range(num_records)],
            'gender': np.random.choice(['Male', 'Female'], num_records),
            'age_group': np.random.choice(['0-14', '15-24', '25-34', '35-44', '45-54', '55+'], num_records),
            'diagnosis_date': [start_date + timedelta(days=random.randint(0, days_range)) for _ in range(num_records)],
            'diagnosis_status': np.random.choice(['New', 'Previously diagnosed'], num_records, p=[0.7, 0.3]),
            'latitude': [random.uniform(-28.97, -16.95) for _ in range(num_records)],  # Namibia latitude range
            'longitude': [random.uniform(11.73, 25.26) for _ in range(num_records)],   # Namibia longitude range
            'on_treatment': np.random.choice([True, False], num_records, p=[0.8, 0.2])
        })
        
        # Population data for regions (dummy data)
        self.population_data = pd.DataFrame({
            'region': self.regions,
            'population': [
                150000, 87000, 85000, 148000, 89000, 
                415000, 96000, 245000, 74000, 243000,
                176000, 181000, 154000, 98000
            ],
            'area_sqkm': [
                63579, 109651, 161235, 25576, 23166,
                36964, 115293, 10706, 84612, 26573,
                8653, 38653, 105185, 14785
            ]
        })
        
        # Calculate population density
        self.population_data['density'] = self.population_data['population'] / self.population_data['area_sqkm']
        
        # Health facilities data (dummy)
        facility_types = ['Hospital', 'Clinic', 'Testing Center', 'Community Outreach']
        services = [
            'HIV Testing', 'HIV Treatment', 'Counseling', 'PrEP', 
            'PMTCT', 'Youth Services', 'Support Groups'
        ]
        
        self.health_facilities = pd.DataFrame({
            'name': [f'Facility_{i}' for i in range(1, 101)],
            'region': np.random.choice(self.regions, 100),
            'district': ['District_' + str(random.randint(1, 5)) for _ in range(100)],
            'facility_type': np.random.choice(facility_types, 100),
            'latitude': [random.uniform(-28.97, -16.95) for _ in range(100)],
            'longitude': [random.uniform(11.73, 25.26) for _ in range(100)],
            'services': [', '.join(np.random.choice(services, random.randint(2, 5), replace=False)) for _ in range(100)],
            'contact': [f'+264 61 {random.randint(100000, 999999)}' for _ in range(100)],
            'hours': np.random.choice(['8:00-17:00', '8:00-16:00', '9:00-18:00', '24 hours'], 100)
        })
    
    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Current View", command=self.export_current_view)
        file_menu.add_command(label="Export All Data", command=self.export_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="HIV Case Distribution", command=self.show_hiv_distribution)
        view_menu.add_command(label="Population Density", command=self.show_population_density)
        view_menu.add_command(label="Health Facilities", command=self.show_health_facilities)
        view_menu.add_command(label="Regional Analysis", command=self.show_regional_analysis)
        view_menu.add_command(label="Temporal Trends", command=self.show_temporal_trends)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_notebook(self):
        """Create the main notebook with tabs for different visualizations"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create the tabs
        self.tab_hiv_map = ttk.Frame(self.notebook)
        self.tab_population = ttk.Frame(self.notebook)
        self.tab_facilities = ttk.Frame(self.notebook)
        self.tab_regional = ttk.Frame(self.notebook)
        self.tab_temporal = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.tab_hiv_map, text="HIV Case Distribution")
        self.notebook.add(self.tab_population, text="Population Density")
        self.notebook.add(self.tab_facilities, text="Health Facilities")
        self.notebook.add(self.tab_regional, text="Regional Analysis")
        self.notebook.add(self.tab_temporal, text="Temporal Trends")
        
        # Configure tab grid layouts
        for tab in [self.tab_hiv_map, self.tab_population, self.tab_facilities, self.tab_regional, self.tab_temporal]:
            tab.columnconfigure(0, weight=1)  # Controls panel
            tab.columnconfigure(1, weight=4)  # Map/visualization area
            tab.rowconfigure(0, weight=1)
        
        # Create filter panels for each tab
        self.create_hiv_map_controls()
        self.create_population_controls()
        self.create_facilities_controls()
        self.create_regional_controls()
        self.create_temporal_controls()
    
    def create_hiv_map_controls(self):
        """Create control panel for HIV case distribution map"""
        control_frame = ttk.LabelFrame(self.tab_hiv_map, text="Filters")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Time frame filter
        ttk.Label(control_frame, text="Time Frame:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.time_frame_var = tk.StringVar(value="All Time")
        time_frame_combo = ttk.Combobox(control_frame, textvariable=self.time_frame_var)
        time_frame_combo['values'] = ("All Time", "Last Year", "Last 5 Years", "Custom")
        time_frame_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        time_frame_combo.bind("<<ComboboxSelected>>", lambda e: self.update_hiv_map())
        
        # Age group filter
        ttk.Label(control_frame, text="Age Group:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.age_group_var = tk.StringVar(value="All")
        age_group_combo = ttk.Combobox(control_frame, textvariable=self.age_group_var)
        age_group_combo['values'] = ("All", "0-14", "15-24", "25-34", "35-44", "45-54", "55+")
        age_group_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        age_group_combo.bind("<<ComboboxSelected>>", lambda e: self.update_hiv_map())
        
        # Gender filter
        ttk.Label(control_frame, text="Gender:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.gender_var = tk.StringVar(value="All")
        gender_combo = ttk.Combobox(control_frame, textvariable=self.gender_var)
        gender_combo['values'] = ("All", "Male", "Female")
        gender_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        gender_combo.bind("<<ComboboxSelected>>", lambda e: self.update_hiv_map())
        
        # Diagnosis status filter
        ttk.Label(control_frame, text="Diagnosis Status:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.diagnosis_var = tk.StringVar(value="All")
        diagnosis_combo = ttk.Combobox(control_frame, textvariable=self.diagnosis_var)
        diagnosis_combo['values'] = ("All", "New", "Previously diagnosed")
        diagnosis_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        diagnosis_combo.bind("<<ComboboxSelected>>", lambda e: self.update_hiv_map())
        
        # Update button
        ttk.Button(control_frame, text="Update Map", command=self.update_hiv_map).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(control_frame, text="Statistics")
        stats_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.total_cases_var = tk.StringVar(value="Total Cases: 0")
        ttk.Label(stats_frame, textvariable=self.total_cases_var).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.filtered_cases_var = tk.StringVar(value="Filtered Cases: 0")
        ttk.Label(stats_frame, textvariable=self.filtered_cases_var).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.highest_region_var = tk.StringVar(value="Highest Region: N/A")
        ttk.Label(stats_frame, textvariable=self.highest_region_var).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        # Visualization type
        vis_frame = ttk.LabelFrame(control_frame, text="Visualization Type")
        vis_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.vis_type_var = tk.StringVar(value="Heatmap")
        ttk.Radiobutton(vis_frame, text="Heatmap", variable=self.vis_type_var, value="Heatmap").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(vis_frame, text="Scatter", variable=self.vis_type_var, value="Scatter").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(vis_frame, text="Choropleth", variable=self.vis_type_var, value="Choropleth").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        self.vis_type_var.trace("w", lambda *args: self.update_hiv_map())

        # Export button
        ttk.Button(control_frame, text="Export Data", command=lambda: self.export_filtered_data("hiv")).grid(row=7, column=0, columnspan=2, pady=10)
        
        # Create map frame
        self.hiv_map_frame = ttk.Frame(self.tab_hiv_map)
        self.hiv_map_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    def create_population_controls(self):
        """Create control panel for population density map"""
        control_frame = ttk.LabelFrame(self.tab_population, text="Controls")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Visualization type
        ttk.Label(control_frame, text="Display Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pop_display_var = tk.StringVar(value="Population Density")
        pop_display_combo = ttk.Combobox(control_frame, textvariable=self.pop_display_var)
        pop_display_combo['values'] = ("Population Density", "Total Population", "HIV Prevalence Rate")
        pop_display_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        pop_display_combo.bind("<<ComboboxSelected>>", lambda e: self.update_population_map())
        
        # Correlation analysis
        corr_frame = ttk.LabelFrame(control_frame, text="Correlation Analysis")
        corr_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Button(corr_frame, text="Analyze Correlation", command=self.show_correlation_analysis).grid(row=0, column=0, pady=5)
        
        self.corr_result_var = tk.StringVar(value="Correlation: Not calculated")
        ttk.Label(corr_frame, textvariable=self.corr_result_var).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        # High-risk identification
        risk_frame = ttk.LabelFrame(control_frame, text="High-Risk Areas")
        risk_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(risk_frame, text="Risk Threshold:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.risk_threshold_var = tk.DoubleVar(value=0.01)  # 1% prevalence as default
        risk_scale = ttk.Scale(risk_frame, from_=0.001, to=0.05, variable=self.risk_threshold_var, orient=tk.HORIZONTAL)
        risk_scale.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        risk_scale.bind("<ButtonRelease-1>", lambda e: self.update_high_risk_areas())
        
        ttk.Label(risk_frame, textvariable=tk.StringVar(value="0.1% - 5%")).grid(row=1, column=1, sticky="e", padx=5)
        
        ttk.Button(risk_frame, text="Identify High-Risk Areas", command=self.update_high_risk_areas).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Export button
        ttk.Button(control_frame, text="Export Data", command=lambda: self.export_filtered_data("population")).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Create map frame
        self.population_map_frame = ttk.Frame(self.tab_population)
        self.population_map_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    def create_facilities_controls(self):
        """Create control panel for health facilities map"""
        control_frame = ttk.LabelFrame(self.tab_facilities, text="Filters")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Region filter
        ttk.Label(control_frame, text="Region:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.facilities_region_var = tk.StringVar(value="All")
        facilities_region_combo = ttk.Combobox(control_frame, textvariable=self.facilities_region_var)
        facilities_region_combo['values'] = ["All"] + self.regions
        facilities_region_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        facilities_region_combo.bind("<<ComboboxSelected>>", lambda e: self.update_facilities_map())
        
        # Facility type filter
        ttk.Label(control_frame, text="Facility Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.facility_type_var = tk.StringVar(value="All")
        facility_type_combo = ttk.Combobox(control_frame, textvariable=self.facility_type_var)
        facility_type_combo['values'] = ["All", "Hospital", "Clinic", "Testing Center", "Community Outreach"]
        facility_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        facility_type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_facilities_map())
        
        # Services filter
        services_frame = ttk.LabelFrame(control_frame, text="Services")
        services_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.services_vars = {}
        services = ["HIV Testing", "HIV Treatment", "Counseling", "PrEP", "PMTCT", "Youth Services", "Support Groups"]
        
        for i, service in enumerate(services):
            self.services_vars[service] = tk.BooleanVar(value=False)
            ttk.Checkbutton(services_frame, text=service, variable=self.services_vars[service]).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        
        # Search functionality
        search_frame = ttk.LabelFrame(control_frame, text="Search")
        search_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Facility Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.facility_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.facility_search_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_facilities).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Update button
        ttk.Button(control_frame, text="Update Map", command=self.update_facilities_map).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Facility details
        facility_details_frame = ttk.LabelFrame(control_frame, text="Facility Details")
        facility_details_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.facility_details_text = tk.Text(facility_details_frame, height=8, width=30, wrap=tk.WORD)
        self.facility_details_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.facility_details_text.insert(tk.END, "Select a facility on the map to view details.")
        self.facility_details_text.config(state=tk.DISABLED)
        
        # Export button
        ttk.Button(control_frame, text="Export Data", command=lambda: self.export_filtered_data("facilities")).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Create map frame
        self.facilities_map_frame = ttk.Frame(self.tab_facilities)
        self.facilities_map_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    def create_regional_controls(self):
        """Create control panel for regional analysis"""
        control_frame = ttk.LabelFrame(self.tab_regional, text="Controls")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Region selection
        ttk.Label(control_frame, text="Select Region:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.regional_analysis_var = tk.StringVar(value="All")
        regional_combo = ttk.Combobox(control_frame, textvariable=self.regional_analysis_var)
        regional_combo['values'] = ["All"] + self.regions
        regional_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        regional_combo.bind("<<ComboboxSelected>>", lambda e: self.update_regional_analysis())
        
        # Comparison type
        ttk.Label(control_frame, text="Comparison Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.comparison_type_var = tk.StringVar(value="Cases by Region")
        comparison_combo = ttk.Combobox(control_frame, textvariable=self.comparison_type_var)
        comparison_combo['values'] = [
            "Cases by Region", 
            "Cases per 100,000 Population", 
            "New Cases vs. Previously Diagnosed", 
            "Gender Distribution",
            "Age Group Distribution"
        ]
        comparison_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        comparison_combo.bind("<<ComboboxSelected>>", lambda e: self.update_regional_analysis())
        
        # Time period
        ttk.Label(control_frame, text="Time Period:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.regional_time_var = tk.StringVar(value="All Time")
        regional_time_combo = ttk.Combobox(control_frame, textvariable=self.regional_time_var)
        regional_time_combo['values'] = ["All Time", "Last Year", "Last 3 Years", "Last 5 Years"]
        regional_time_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        regional_time_combo.bind("<<ComboboxSelected>>", lambda e: self.update_regional_analysis())
        
        # Policy impact assessment (simplified)
        policy_frame = ttk.LabelFrame(control_frame, text="Policy Impact")
        policy_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(policy_frame, text="Policy Implementation Date:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.policy_date_var = tk.StringVar(value="2020-01-01")
        ttk.Entry(policy_frame, textvariable=self.policy_date_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Button(policy_frame, text="Assess Impact", command=self.assess_policy_impact).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Update button
        ttk.Button(control_frame, text="Update Analysis", command=self.update_regional_analysis).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Export button
        ttk.Button(control_frame, text="Export Data", command=lambda: self.export_filtered_data("regional")).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Create visualization frame
        self.regional_vis_frame = ttk.Frame(self.tab_regional)
        self.regional_vis_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    def create_temporal_controls(self):
        """Create control panel for temporal trends"""
        control_frame = ttk.LabelFrame(self.tab_temporal, text="Controls")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Trend type selection
        ttk.Label(control_frame, text="Trend Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.trend_type_var = tk.StringVar(value="New Cases Over Time")
        trend_combo = ttk.Combobox(control_frame, textvariable=self.trend_type_var)
        trend_combo['values'] = [
            "New Cases Over Time", 
            "Age Group Comparison", 
            "Gender Comparison", 
            "Treatment Status",
            "Diagnosis Status Over Time"
        ]
        trend_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        trend_combo.bind("<<ComboboxSelected>>", lambda e: self.update_temporal_trends())
        
        # Time granularity
        ttk.Label(control_frame, text="Time Granularity:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.time_granularity_var = tk.StringVar(value="Yearly")
        granularity_combo = ttk.Combobox(control_frame, textvariable=self.time_granularity_var)
        granularity_combo['values'] = ["Yearly", "Quarterly", "Monthly"]
        granularity_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        granularity_combo.bind("<<ComboboxSelected>>", lambda e: self.update_temporal_trends())
        
        # Region filter
        ttk.Label(control_frame, text="Region:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.temporal_region_var = tk.StringVar(value="All")
        temporal_region_combo = ttk.Combobox(control_frame, textvariable=self.temporal_region_var)
        temporal_region_combo['values'] = ["All"] + self.regions
        temporal_region_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        temporal_region_combo.bind("<<ComboboxSelected>>", lambda e: self.update_temporal_trends())
        
        # Date range
        date_frame = ttk.LabelFrame(control_frame, text="Date Range")
        date_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.start_date_var = tk.StringVar(value="2015-01-01")
        ttk.Entry(date_frame, textvariable=self.start_date_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(date_frame, text="End Date:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.end_date_var = tk.StringVar(value="2024-12-31")
        ttk.Entry(date_frame, textvariable=self.end_date_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Update button
        ttk.Button(control_frame, text="Update Trends", command=self.update_temporal_trends).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(control_frame, text="Statistics")
        stats_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.trend_stats_text = tk.Text(stats_frame, height=6, width=30, wrap=tk.WORD)
        self.trend_stats_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.trend_stats_text.insert(tk.END, "Select a trend type to view statistics.")
        self.trend_stats_text.config(state=tk.DISABLED)
        
        # Export button
        ttk.Button(control_frame, text="Export Data", command=lambda: self.export_filtered_data("temporal")).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Create visualization frame
        self.temporal_vis_frame = ttk.Frame(self.tab_temporal)
        self.temporal_vis_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    # Tab content methods
    def show_hiv_distribution(self):
        """Show HIV case distribution map"""
        self.notebook.select(0)  # Switch to HIV map tab
        self.update_hiv_map()
    
    def update_hiv_map(self):
        """Update HIV case distribution map based on filters"""
        # Clear previous map
        for widget in self.hiv_map_frame.winfo_children():
            widget.destroy()
        
        # Filter data based on selected criteria
        filtered_data = self.hiv_data.copy()
        
        # Apply time frame filter
        if self.time_frame_var.get() == "Last Year":
            one_year_ago = datetime.now() - timedelta(days=365)
            filtered_data = filtered_data[filtered_data['diagnosis_date'] >= one_year_ago]
        elif self.time_frame_var.get() == "Last 5 Years":
            five_years_ago = datetime.now() - timedelta(days=5*365)
            filtered_data = filtered_data[filtered_data['diagnosis_date'] >= five_years_ago]
        
        # Apply age group filter
        if self.age_group_var.get() != "All":
            filtered_data = filtered_data[filtered_data['age_group'] == self.age_group_var.get()]
        
        # Apply gender filter
        if self.gender_var.get() != "All":
            filtered_data = filtered_data[filtered_data['gender'] == self.gender_var.get()]
        
        # Apply diagnosis status filter
        if self.diagnosis_var.get() != "All":
            filtered_data = filtered_data[filtered_data['diagnosis_status'] == self.diagnosis_var.get()]
        
        # Update statistics
        self.total_cases_var.set(f"Total Cases: {len(self.hiv_data)}")
        self.filtered_cases_var.set(f"Filtered Cases: {len(filtered_data)}")
        
        # Find region with highest cases
        if not filtered_data.empty:
            region_counts = filtered_data['region'].value_counts()
            highest_region = region_counts.idxmax()
            highest_count = region_counts.max()
            self.highest_region_var.set(f"Highest Region: {highest_region} ({highest_count} cases)")
        else:
            self.highest_region_var.set("Highest Region: N/A")
        
        # Create figure and axis for map
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Draw Namibia outline (simplified)
        # These are very simplified coordinates for demonstration
        namibia_x = [11.73, 25.26, 25.26, 11.73, 11.73]
        namibia_y = [-28.97, -28.97, -16.95, -16.95, -28.97]
        ax.plot(namibia_x, namibia_y, 'k-', linewidth=1)
        
        # Plot the data according to selected visualization type
        vis_type = self.vis_type_var.get()
        
        if vis_type == "Heatmap" and not filtered_data.empty:
            # Create a heatmap using kernel density estimation
            x = filtered_data['longitude']
            y = filtered_data['latitude']
            
            heatmap = ax.hexbin(x, y, gridsize=20, cmap='YlOrRd', alpha=0.8)
            plt.colorbar(heatmap, ax=ax, label='Case Density')
            
        elif vis_type == "Scatter" and not filtered_data.empty:
            # Color by gender
            colors = {'Male': 'blue', 'Female': 'red'}
            for gender, group in filtered_data.groupby('gender'):
                ax.scatter(group['longitude'], group['latitude'], 
                          c=colors.get(gender, 'green'), 
                          alpha=0.5, 
                          label=gender, 
                          s=10)
            ax.legend()
            
        elif vis_type == "Choropleth":
            # Create a simplified choropleth for regions
            region_counts = filtered_data['region'].value_counts().to_dict()
            
            # Create random region coordinates for demo purposes
            # In a real app, you would have actual polygon data for each region
            region_coords = {}
            for i, region in enumerate(self.regions):
                x_center = 18 + np.cos(i/len(self.regions) * 2 * np.pi) * 3
                y_center = -23 + np.sin(i/len(self.regions) * 2 * np.pi) * 3
                region_coords[region] = (x_center, y_center)
            
            # Draw simplified region shapes
            for region in self.regions:
                count = region_counts.get(region, 0)
                intensity = min(count / max(region_counts.values(), 1), 1.0)
                color = plt.cm.OrRd(intensity)
                
                x, y = region_coords[region]
                circle = plt.Circle((x, y), 0.5, color=color, alpha=0.7)
                ax.add_patch(circle)
                ax.annotate(region, (x, y), ha='center', va='center', fontsize=8)
        
        # Set map title and labels
        filter_text = []
        if self.time_frame_var.get() != "All Time":
            filter_text.append(f"Time: {self.time_frame_var.get()}")
        if self.age_group_var.get() != "All":
            filter_text.append(f"Age: {self.age_group_var.get()}")
        if self.gender_var.get() != "All":
            filter_text.append(f"Gender: {self.gender_var.get()}")
        if self.diagnosis_var.get() != "All":
            filter_text.append(f"Status: {self.diagnosis_var.get()}")
        
        filter_str = ", ".join(filter_text) if filter_text else "No filters applied"
        ax.set_title(f"HIV Case Distribution in Namibia\n{filter_str}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        # Set map limits (Namibia boundaries)
        ax.set_xlim(11.5, 25.5)
        ax.set_ylim(-29.0, -16.5)
        
        # Create canvas to display the map
        canvas = FigureCanvasTkAgg(fig, master=self.hiv_map_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_population_density(self):
        """Show population density map"""
        self.notebook.select(1)  # Switch to population density tab
        self.update_population_map()
    
    def update_population_map(self):
        """Update population density map"""
        # Clear previous map
        for widget in self.population_map_frame.winfo_children():
            widget.destroy()
        
        # Create figure and axis for map
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Draw Namibia outline (simplified)
        namibia_x = [11.73, 25.26, 25.26, 11.73, 11.73]
        namibia_y = [-28.97, -28.97, -16.95, -16.95, -28.97]
        ax.plot(namibia_x, namibia_y, 'k-', linewidth=1)
        
        # Get data to display based on selection
        display_type = self.pop_display_var.get()
        
        # Calculate HIV prevalence by region
        hiv_by_region = self.hiv_data['region'].value_counts().to_dict()
        
        # Create synthetic region areas for visualization
        # In a real application, these would be actual geographic polygons
        region_polygons = {}
        for i, region in enumerate(self.regions):
            # Create a simple circle for each region - just for visualization
            x_center = 18 + np.cos(i/len(self.regions) * 2 * np.pi) * 3
            y_center = -23 + np.sin(i/len(self.regions) * 2 * np.pi) * 3
            radius = 0.5
            
            # Create a simple polygon to represent the region
            theta = np.linspace(0, 2*np.pi, 20)
            x = x_center + radius * np.cos(theta)
            y = y_center + radius * np.sin(theta)
            
            region_polygons[region] = (x, y, x_center, y_center)
        
        # Plot data based on display type
        if display_type == "Population Density":
            # Use density from population data
            for region in self.regions:
                density = self.population_data.loc[self.population_data['region'] == region, 'density'].values[0]
                max_density = self.population_data['density'].max()
                intensity = min(density / max_density, 1.0)
                color = plt.cm.Blues(intensity)
                
                x, y, x_center, y_center = region_polygons[region]
                ax.fill(x, y, color=color, alpha=0.7)
                ax.annotate(f"{region}\n{density:.1f}/km²", (x_center, y_center), 
                           ha='center', va='center', fontsize=8)
                
            ax.set_title("Population Density by Region in Namibia")
            
        elif display_type == "Total Population":
            # Use total population
            for region in self.regions:
                population = self.population_data.loc[self.population_data['region'] == region, 'population'].values[0]
                max_pop = self.population_data['population'].max()
                intensity = min(population / max_pop, 1.0)
                color = plt.cm.Greens(intensity)
                
                x, y, x_center, y_center = region_polygons[region]
                ax.fill(x, y, color=color, alpha=0.7)
                ax.annotate(f"{region}\n{population:,}", (x_center, y_center), 
                           ha='center', va='center', fontsize=8)
                
            ax.set_title("Total Population by Region in Namibia")
            
        elif display_type == "HIV Prevalence Rate":
            # Calculate and show HIV prevalence rate (cases per population)
            for region in self.regions:
                population = self.population_data.loc[self.population_data['region'] == region, 'population'].values[0]
                cases = hiv_by_region.get(region, 0)
                prevalence = (cases / population) if population > 0 else 0
                
                # Scale for visualization (typically prevalence is a small decimal)
                max_prevalence = 0.05  # Assume 5% is max for scaling
                intensity = min(prevalence / max_prevalence, 1.0)
                color = plt.cm.OrRd(intensity)
                
                x, y, x_center, y_center = region_polygons[region]
                ax.fill(x, y, color=color, alpha=0.7)
                ax.annotate(f"{region}\n{prevalence:.2%}", (x_center, y_center), 
                           ha='center', va='center', fontsize=8)
                
            ax.set_title("HIV Prevalence Rate by Region in Namibia")
        
        # Set map limits (Namibia boundaries)
        ax.set_xlim(11.5, 25.5)
        ax.set_ylim(-29.0, -16.5)
        
        # Create canvas to display the map
        canvas = FigureCanvasTkAgg(fig, master=self.population_map_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_correlation_analysis(self):
        """Calculate and display correlation between population density and HIV prevalence"""
        # Calculate HIV cases per region
        hiv_counts = self.hiv_data['region'].value_counts().reset_index()
        hiv_counts.columns = ['region', 'cases']
        
        # Merge with population data
        merged_data = pd.merge(hiv_counts, self.population_data, on='region')
        
        # Calculate HIV prevalence (cases per population)
        merged_data['prevalence'] = merged_data['cases'] / merged_data['population']
        
        # Calculate correlation
        correlation = merged_data['density'].corr(merged_data['prevalence'])
        
        # Update the correlation result display
        self.corr_result_var.set(f"Correlation: {correlation:.3f}")
        
        # Show correlation plot in a popup window
        corr_window = tk.Toplevel(self.root)
        corr_window.title("Population Density vs. HIV Prevalence Correlation")
        corr_window.geometry("700x500")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Scatter plot with region labels
        ax.scatter(merged_data['density'], merged_data['prevalence'], s=50, alpha=0.7)
        
        for i, row in merged_data.iterrows():
            ax.annotate(row['region'], (row['density'], row['prevalence']), 
                       xytext=(5, 5), textcoords='offset points')
        
        # Add regression line
        z = np.polyfit(merged_data['density'], merged_data['prevalence'], 1)
        p = np.poly1d(z)
        ax.plot(sorted(merged_data['density']), p(sorted(merged_data['density'])), "r--", alpha=0.7)
        
        ax.set_title(f"Population Density vs. HIV Prevalence (r = {correlation:.3f})")
        ax.set_xlabel("Population Density (people/km²)")
        ax.set_ylabel("HIV Prevalence Rate")
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=corr_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_high_risk_areas(self):
        """Identify and display high-risk areas based on prevalence threshold"""
        # Calculate HIV cases per region
        hiv_counts = self.hiv_data['region'].value_counts().reset_index()
        hiv_counts.columns = ['region', 'cases']
        
        # Merge with population data
        merged_data = pd.merge(hiv_counts, self.population_data, on='region')
        
        # Calculate HIV prevalence (cases per population)
        merged_data['prevalence'] = merged_data['cases'] / merged_data['population']
        
        # Identify high-risk areas based on threshold
        threshold = self.risk_threshold_var.get()
        high_risk = merged_data[merged_data['prevalence'] >= threshold]
        
        # Create popup window to display results
        risk_window = tk.Toplevel(self.root)
        risk_window.title(f"High-Risk Areas (Prevalence ≥ {threshold:.2%})")
        risk_window.geometry("800x600")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
        
        # Map display of high-risk areas
        # Create synthetic region polygons for visualization
        for i, region in enumerate(self.regions):
            # Create a simple circle for each region
            x_center = 18 + np.cos(i/len(self.regions) * 2 * np.pi) * 3
            y_center = -23 + np.sin(i/len(self.regions) * 2 * np.pi) * 3
            radius = 0.5
            
            # Check if high-risk region
            is_high_risk = region in high_risk['region'].values
            color = 'red' if is_high_risk else 'green'
            alpha = 0.7 if is_high_risk else 0.3
            
            # Create a circle to represent the region
            circle = plt.Circle((x_center, y_center), radius, color=color, alpha=alpha)
            ax1.add_patch(circle)
            ax1.annotate(region, (x_center, y_center), ha='center', va='center', fontsize=8)
        
        # Draw Namibia outline (simplified)
        namibia_x = [11.73, 25.26, 25.26, 11.73, 11.73]
        namibia_y = [-28.97, -28.97, -16.95, -16.95, -28.97]
        ax1.plot(namibia_x, namibia_y, 'k-', linewidth=1)
        
        # Set limits and title
        ax1.set_xlim(11.5, 25.5)
        ax1.set_ylim(-29.0, -16.5)
        ax1.set_title(f"High-Risk Regions (Prevalence ≥ {threshold:.2%})")
        ax1.set_xlabel("Longitude")
        ax1.set_ylabel("Latitude")
        
        # Add legend
        high_risk_patch = mpatches.Patch(color='red', alpha=0.7, label='High Risk')
        low_risk_patch = mpatches.Patch(color='green', alpha=0.3, label='Low Risk')
        ax1.legend(handles=[high_risk_patch, low_risk_patch])
        
        # Bar chart of prevalence rates
        sorted_data = merged_data.sort_values('prevalence', ascending=False)
        bars = ax2.bar(sorted_data['region'], sorted_data['prevalence'], alpha=0.7)
        
        # Color the bars based on risk threshold
        for i, bar in enumerate(bars):
            if sorted_data.iloc[i]['prevalence'] >= threshold:
                bar.set_color('red')
            else:
                bar.set_color('green')
        
        # Add threshold line
        ax2.axhline(y=threshold, color='red', linestyle='--', alpha=0.7)
        ax2.text(0, threshold + 0.001, f"Threshold: {threshold:.2%}", va='bottom', ha='left', color='red')
        
        ax2.set_title("HIV Prevalence by Region")
        ax2.set_xlabel("Region")
        ax2.set_ylabel("Prevalence Rate")
        ax2.set_xticklabels(sorted_data['region'], rotation=90)
        ax2.set_ylim(0, max(sorted_data['prevalence']) * 1.1)
        
        plt.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=risk_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add button to close window
        ttk.Button(risk_window, text="Close", command=risk_window.destroy).pack(pady=10)
    
    def show_health_facilities(self):
        """Show health facilities map"""
        self.notebook.select(2)  # Switch to health facilities tab
        self.update_facilities_map()
    
    def update_facilities_map(self):
        """Update health facilities map based on filters"""
        # Clear previous map
        for widget in self.facilities_map_frame.winfo_children():
            widget.destroy()
        
        # Filter facilities based on selected criteria
        filtered_facilities = self.health_facilities.copy()
        
        # Apply region filter
        if self.facilities_region_var.get() != "All":
            filtered_facilities = filtered_facilities[filtered_facilities['region'] == self.facilities_region_var.get()]
        
        # Apply facility type filter
        if self.facility_type_var.get() != "All":
            filtered_facilities = filtered_facilities[filtered_facilities['facility_type'] == self.facility_type_var.get()]
        
        # Apply services filters
        selected_services = [service for service, var in self.services_vars.items() if var.get()]
        if selected_services:
            # Filter facilities that have at least one of the selected services
            filtered_facilities = filtered_facilities[filtered_facilities['services'].apply(
                lambda x: any(service in x for service in selected_services))]
        
        # Create figure and axis for map
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Draw Namibia outline (simplified)
        namibia_x = [11.73, 25.26, 25.26, 11.73, 11.73]
        namibia_y = [-28.97, -28.97, -16.95, -16.95, -28.97]
        ax.plot(namibia_x, namibia_y, 'k-', linewidth=1)
        
        # Plot facilities
        if not filtered_facilities.empty:
            # Define colors for facility types
            facility_colors = {
                'Hospital': 'red',
                'Clinic': 'blue',
                'Testing Center': 'green',
                'Community Outreach': 'purple'
            }
            
            # Plot each facility
            for facility_type, group in filtered_facilities.groupby('facility_type'):
                ax.scatter(group['longitude'], group['latitude'], 
                         c=facility_colors.get(facility_type, 'black'), 
                         label=facility_type, 
                         s=50, 
                         alpha=0.7)
            
            # Create legend
            ax.legend(title="Facility Type")
        
        # Set map title and labels
        filter_text = []
        if self.facilities_region_var.get() != "All":
            filter_text.append(f"Region: {self.facilities_region_var.get()}")
        if self.facility_type_var.get() != "All":
            filter_text.append(f"Type: {self.facility_type_var.get()}")
        if selected_services:
            filter_text.append(f"Services: {', '.join(selected_services)}")
        
        filter_str = ", ".join(filter_text) if filter_text else "All Facilities"
        ax.set_title(f"Health Facilities in Namibia\n{filter_str}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        # Set map limits (Namibia boundaries)
        ax.set_xlim(11.5, 25.5)
        ax.set_ylim(-29.0, -16.5)
        
        # Create canvas to display the map
        canvas = FigureCanvasTkAgg(fig, master=self.facilities_map_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Enable facility selection on click
        def on_click(event):
            if event.inaxes != ax:
                return
            
            x, y = event.xdata, event.ydata
            
            # Find closest facility
            if not filtered_facilities.empty:
                # Calculate distance to each facility
                filtered_facilities['distance'] = np.sqrt(
                    (filtered_facilities['longitude'] - x)**2 + 
                    (filtered_facilities['latitude'] - y)**2
                )
                
                # Get closest facility within a reasonable distance
                closest = filtered_facilities.loc[filtered_facilities['distance'].idxmin()]
                
                if closest['distance'] < 0.5:  # Arbitrary threshold for clicking
                    self.display_facility_details(closest)
        
        # Connect the click event
        canvas.mpl_connect('button_press_event', on_click)
    
    def search_facilities(self):
        """Search for facilities by name"""
        search_term = self.facility_search_var.get().strip().lower()
        
        if not search_term:
            messagebox.showinfo("Search", "Please enter a search term.")
            return
        
        # Find matching facilities
        matching_facilities = self.health_facilities[
            self.health_facilities['name'].str.lower().str.contains(search_term)
        ]
        
        if matching_facilities.empty:
            messagebox.showinfo("Search Results", "No facilities found matching your search.")
            return
        
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results for '{search_term}'")
        results_window.geometry("600x400")
        
        # Create listbox for results
        ttk.Label(results_window, text=f"Found {len(matching_facilities)} matching facilities:").pack(pady=5)
        
        result_frame = ttk.Frame(results_window)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        results_list = tk.Listbox(result_frame, width=50, height=15)
        results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=results_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        results_list.config(yscrollcommand=scrollbar.set)
        
        # Populate listbox
        for _, facility in matching_facilities.iterrows():
            results_list.insert(tk.END, f"{facility['name']} ({facility['facility_type']}) - {facility['region']}")
        
        # Function to show details when a facility is selected
        def show_selected_facility():
            selection = results_list.curselection()
            if selection:
                index = selection[0]
                facility = matching_facilities.iloc[index]
                self.display_facility_details(facility)
                
                # Update filters to show this facility on the map
                self.facilities_region_var.set(facility['region'])
                self.facility_type_var.set(facility['facility_type'])
                self.update_facilities_map()
                results_window.destroy()
        
        # Add button to view details
        ttk.Button(results_window, text="View Details", command=show_selected_facility).pack(pady=10)
    
    def display_facility_details(self, facility):
        """Display details of a selected health facility"""
        # Enable editing of the text widget
        self.facility_details_text.config(state=tk.NORMAL)
        
        # Clear previous content
        self.facility_details_text.delete(1.0, tk.END)
        
        # Format and insert facility details
        details = (
            f"Name: {facility['name']}\n"
            f"Type: {facility['facility_type']}\n"
            f"Region: {facility['region']}\n"
            f"District: {facility['district']}\n"
            f"Services: {facility['services']}\n"
            f"Contact: {facility['contact']}\n"
            f"Hours: {facility['hours']}"
        )
        
        self.facility_details_text.insert(tk.END, details)
        
        # Disable editing again
        self.facility_details_text.config(state=tk.DISABLED)
    
    def show_regional_analysis(self):
        """Show regional analysis tab"""
        self.notebook.select(3)  # Switch to regional analysis tab
        self.update_regional_analysis()
    
    def update_regional_analysis(self):
        """Update regional analysis visualization"""
        # Clear previous visualization
        for widget in self.regional_vis_frame.winfo_children():
            widget.destroy()
        
        # Filter HIV data based on selected region and time period
        filtered_data = self.hiv_data.copy()
        
        # Apply region filter
        if self.regional_analysis_var.get() != "All":
            filtered_data = filtered_data[filtered_data['region'] == self.regional_analysis_var.get()]
        
        # Apply time period filter
        if self.regional_time_var.get() == "Last Year":
            one_year_ago = datetime.now() - timedelta(days=365)
            filtered_data = filtered_data[filtered_data['diagnosis_date'] >= one_year_ago]
        elif self.regional_time_var.get() == "Last 3 Years":
            three_years_ago = datetime.now() - timedelta(days=3*365)
            filtered_data = filtered_data[filtered_data['diagnosis_date'] >= three_years_ago]
        elif self.regional_time_var.get() == "Last 5 Years":
            five_years_ago = datetime.now() - timedelta(days=5*365)
            filtered_data = filtered_data[filtered_data['diagnosis_date'] >= five_years_ago]
        
        # Create figure and axis for visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate visualization based on comparison type
        comparison_type = self.comparison_type_var.get()
        
        if comparison_type == "Cases by Region":
            # Count cases by region
            region_counts = filtered_data['region'].value_counts().sort_values(ascending=False)
            
            # Bar chart of cases by region
            bars = ax.bar(region_counts.index, region_counts.values, color='cornflowerblue')
            
            # Add data labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{int(height)}', ha='center', va='bottom')
            
            ax.set_title(f"HIV Cases by Region {self.regional_time_var.get()}")           
            ax.set_title(f"HIV Cases by Region {self.regional_time_var.get()}")
            ax.set_xlabel("Region")
            ax.set_ylabel("Number of Cases")
            ax.set_xticklabels(region_counts.index, rotation=45, ha='right')
            
        elif comparison_type == "Cases per 100,000 Population":
            # Count cases by region
            region_counts = filtered_data['region'].value_counts().reset_index()
            region_counts.columns = ['region', 'cases']
            
            # Merge with population data
            merged_data = pd.merge(region_counts, self.population_data, on='region')
            
            # Calculate cases per 100,000 population
            merged_data['cases_per_100k'] = (merged_data['cases'] / merged_data['population']) * 100000
            merged_data = merged_data.sort_values('cases_per_100k', ascending=False)
            
            # Bar chart of cases per 100k
            bars = ax.bar(merged_data['region'], merged_data['cases_per_100k'], color='salmon')
            
            # Add data labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height:.1f}', ha='center', va='bottom')
            
            ax.set_title(f"HIV Cases per 100,000 Population {self.regional_time_var.get()}")
            ax.set_xlabel("Region")
            ax.set_ylabel("Cases per 100,000 Population")
            ax.set_xticklabels(merged_data['region'], rotation=45, ha='right')
            
        elif comparison_type == "New Cases vs. Previously Diagnosed":
            # Count by diagnosis status
            if not filtered_data.empty:
                status_counts = filtered_data['diagnosis_status'].value_counts()
                
                # Pie chart of diagnosis status
                wedges, texts, autotexts = ax.pie(
                    status_counts.values,
                    labels=status_counts.index,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=['lightgreen', 'lightcoral']
                )
                
                ax.set_title(f"New vs. Previously Diagnosed Cases\n{self.regional_time_var.get()}")
                ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
                
        elif comparison_type == "Gender Distribution":
            # Count by gender
            if not filtered_data.empty:
                gender_counts = filtered_data['gender'].value_counts()
                
                # Pie chart of gender distribution
                wedges, texts, autotexts = ax.pie(
                    gender_counts.values,
                    labels=gender_counts.index,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=['lightblue', 'pink']
                )
                
                ax.set_title(f"Gender Distribution of Cases\n{self.regional_time_var.get()}")
                ax.axis('equal')
                
        elif comparison_type == "Age Group Distribution":
            # Count by age group
            if not filtered_data.empty:
                age_counts = filtered_data['age_group'].value_counts().sort_index()
                
                # Bar chart of age groups
                bars = ax.bar(age_counts.index, age_counts.values, color='mediumpurple')
                
                # Add data labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{int(height)}', ha='center', va='bottom')
                
                ax.set_title(f"Age Group Distribution {self.regional_time_var.get()}")
                ax.set_xlabel("Age Group")
                ax.set_ylabel("Number of Cases")
        
        plt.tight_layout()
        
        # Create canvas to display the visualization
        canvas = FigureCanvasTkAgg(fig, master=self.regional_vis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def assess_policy_impact(self):
        """Assess the impact of a policy implementation on HIV cases"""
        try:
            policy_date = datetime.strptime(self.policy_date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
        
        # Filter data for the selected region
        filtered_data = self.hiv_data.copy()
        
        if self.regional_analysis_var.get() != "All":
            filtered_data = filtered_data[filtered_data['region'] == self.regional_analysis_var.get()]
        
        # Split data into pre-policy and post-policy periods
        pre_policy = filtered_data[filtered_data['diagnosis_date'] < policy_date]
        post_policy = filtered_data[filtered_data['diagnosis_date'] >= policy_date]
        
        # Calculate monthly case counts
        pre_monthly = pre_policy.resample('M', on='diagnosis_date').size()
        post_monthly = post_policy.resample('M', on='diagnosis_date').size()
        
        # Create impact assessment window
        impact_window = tk.Toplevel(self.root)
        impact_window.title(f"Policy Impact Assessment (Implemented {policy_date.date()})")
        impact_window.geometry("800x600")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot monthly cases with policy date line
        if not pre_monthly.empty:
            pre_monthly.plot(ax=ax, label='Pre-Policy', color='blue')
        if not post_monthly.empty:
            post_monthly.plot(ax=ax, label='Post-Policy', color='red')
        
        # Add policy implementation line
        ax.axvline(x=policy_date, color='green', linestyle='--', label='Policy Implementation')
        
        ax.set_title(f"HIV Cases Before and After Policy Implementation\nRegion: {self.regional_analysis_var.get() or 'All'}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Monthly Cases")
        ax.legend()
        ax.grid(True)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=impact_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Calculate and display statistics
        stats_frame = ttk.Frame(impact_window)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Pre-policy stats
        pre_mean = pre_monthly.mean() if not pre_monthly.empty else 0
        pre_std = pre_monthly.std() if not pre_monthly.empty else 0
        
        ttk.Label(stats_frame, text=f"Pre-Policy (n={len(pre_monthly)} months):").grid(row=0, column=0, sticky="w")
        ttk.Label(stats_frame, text=f"Mean: {pre_mean:.1f} cases/month").grid(row=1, column=0, sticky="w")
        ttk.Label(stats_frame, text=f"Std Dev: {pre_std:.1f}").grid(row=2, column=0, sticky="w")
        
        # Post-policy stats
        post_mean = post_monthly.mean() if not post_monthly.empty else 0
        post_std = post_monthly.std() if not post_monthly.empty else 0
        
        ttk.Label(stats_frame, text=f"Post-Policy (n={len(post_monthly)} months):").grid(row=0, column=1, sticky="w", padx=20)
        ttk.Label(stats_frame, text=f"Mean: {post_mean:.1f} cases/month").grid(row=1, column=1, sticky="w", padx=20)
        ttk.Label(stats_frame, text=f"Std Dev: {post_std:.1f}").grid(row=2, column=1, sticky="w", padx=20)
        
        # Change calculation
        if pre_mean > 0:
            change = ((post_mean - pre_mean) / pre_mean) * 100
            change_color = "red" if change > 0 else "green"
            change_text = f"{change:.1f}% increase" if change > 0 else f"{abs(change):.1f}% decrease"
            
            ttk.Label(stats_frame, text="Change:").grid(row=0, column=2, sticky="w")
            ttk.Label(stats_frame, text=change_text, foreground=change_color).grid(row=1, column=2, sticky="w")
        
        # Add close button
        ttk.Button(impact_window, text="Close", command=impact_window.destroy).pack(pady=10)
    
    def show_temporal_trends(self):
        """Show temporal trends tab"""
        self.notebook.select(4)  # Switch to temporal trends tab
        self.update_temporal_trends()
    
    def update_temporal_trends(self):
        """Update temporal trends visualization"""
        # Clear previous visualization
        for widget in self.temporal_vis_frame.winfo_children():
            widget.destroy()
        
        # Filter data based on selected region
        filtered_data = self.hiv_data.copy()
        
        if self.temporal_region_var.get() != "All":
            filtered_data = filtered_data[filtered_data['region'] == self.temporal_region_var.get()]
        
        # Parse date range
        try:
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
        
        # Filter by date range
        filtered_data = filtered_data[
            (filtered_data['diagnosis_date'] >= start_date) & 
            (filtered_data['diagnosis_date'] <= end_date)]
        
        if filtered_data.empty:
            messagebox.showwarning("No Data", "No data available for the selected filters.")
            return
        
        # Create figure and axis for visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate visualization based on trend type
        trend_type = self.trend_type_var.get()
        time_granularity = self.time_granularity_var.get()
        
        # Resample data based on time granularity
        if time_granularity == "Yearly":
            freq = 'Y'
            date_format = "%Y"
        elif time_granularity == "Quarterly":
            freq = 'Q'
            date_format = "%Y-Q%q"
        else:  # Monthly
            freq = 'M'
            date_format = "%Y-%m"
        
        if trend_type == "New Cases Over Time":
            # Resample cases over time
            cases_over_time = filtered_data.resample(freq, on='diagnosis_date').size()
            
            # Plot the trend
            cases_over_time.plot(ax=ax, marker='o', linestyle='-', color='royalblue')
            
            ax.set_title(f"HIV Cases Over Time\nRegion: {self.temporal_region_var.get() or 'All'}")
            ax.set_xlabel("Time Period")
            ax.set_ylabel("Number of Cases")
            ax.grid(True)
            
            # Update statistics
            self.update_trend_statistics(cases_over_time, "cases")
            
        elif trend_type == "Age Group Comparison":
            # Group by time period and age group
            age_groups = filtered_data.groupby([
                pd.Grouper(key='diagnosis_date', freq=freq),
                'age_group'
            ]).size().unstack()
            
            # Plot each age group
            age_groups.plot(ax=ax, marker='o', linestyle='-')
            
            ax.set_title(f"HIV Cases by Age Group Over Time\nRegion: {self.temporal_region_var.get() or 'All'}")
            ax.set_xlabel("Time Period")
            ax.set_ylabel("Number of Cases")
            ax.grid(True)
            ax.legend(title="Age Group")
            
        elif trend_type == "Gender Comparison":
            # Group by time period and gender
            gender_groups = filtered_data.groupby([
                pd.Grouper(key='diagnosis_date', freq=freq),
                'gender'
            ]).size().unstack()
            
            # Plot each gender
            gender_groups.plot(ax=ax, marker='o', linestyle='-', color=['blue', 'pink'])
            
            ax.set_title(f"HIV Cases by Gender Over Time\nRegion: {self.temporal_region_var.get() or 'All'}")
            ax.set_xlabel("Time Period")
            ax.set_ylabel("Number of Cases")
            ax.grid(True)
            ax.legend(title="Gender")
            
        elif trend_type == "Treatment Status":
            # Group by time period and treatment status
            treatment_groups = filtered_data.groupby([
                pd.Grouper(key='diagnosis_date', freq=freq),
                'on_treatment'
            ]).size().unstack()
            
            # Plot treatment status
            treatment_groups.plot(ax=ax, kind='bar', stacked=True, color=['red', 'green'])
            
            ax.set_title(f"Treatment Status Over Time\nRegion: {self.temporal_region_var.get() or 'All'}")
            ax.set_xlabel("Time Period")
            ax.set_ylabel("Number of Cases")
            ax.legend(["Not on Treatment", "On Treatment"], title="Treatment Status")
            
            # Format x-axis labels
            ax.set_xticklabels([pd.to_datetime(label.get_text()).strftime(date_format) 
                              for label in ax.get_xticklabels()], rotation=45)
            
        elif trend_type == "Diagnosis Status Over Time":
            # Group by time period and diagnosis status
            diagnosis_groups = filtered_data.groupby([
                pd.Grouper(key='diagnosis_date', freq=freq),
                'diagnosis_status'
            ]).size().unstack()
            
            # Plot diagnosis status
            diagnosis_groups.plot(ax=ax, kind='bar', stacked=True, color=['lightgreen', 'lightcoral'])
            
            ax.set_title(f"Diagnosis Status Over Time\nRegion: {self.temporal_region_var.get() or 'All'}")
            ax.set_xlabel("Time Period")
            ax.set_ylabel("Number of Cases")
            ax.legend(title="Diagnosis Status")
            
            # Format x-axis labels
            ax.set_xticklabels([pd.to_datetime(label.get_text()).strftime(date_format) 
                              for label in ax.get_xticklabels()], rotation=45)
        
        plt.tight_layout()
        
        # Create canvas to display the visualization
        canvas = FigureCanvasTkAgg(fig, master=self.temporal_vis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_trend_statistics(self, time_series, series_type):
        """Update the statistics text box with trend analysis"""
        if time_series.empty:
            stats_text = "No data available for the selected filters."
        else:
            # Calculate basic statistics
            mean = time_series.mean()
            std = time_series.std()
            minimum = time_series.min()
            maximum = time_series.max()
            latest = time_series.iloc[-1]
            
            # Calculate percentage change
            if len(time_series) >= 2:
                last_period = time_series.iloc[-1]
                prev_period = time_series.iloc[-2]
                pct_change = ((last_period - prev_period) / prev_period) * 100
                change_text = f"{pct_change:.1f}% from previous period"
            else:
                change_text = "Insufficient data for change calculation"
            
            # Prepare statistics text
            stats_text = (
                f"Statistics for {series_type.replace('_', ' ')}:\n"
                f"Mean: {mean:.1f}\n"
                f"Standard Deviation: {std:.1f}\n"
                f"Minimum: {minimum}\n"
                f"Maximum: {maximum}\n"
                f"Latest: {latest}\n"
                f"Change: {change_text}"
            )
        
        # Update the text widget
        self.trend_stats_text.config(state=tk.NORMAL)
        self.trend_stats_text.delete(1.0, tk.END)
        self.trend_stats_text.insert(tk.END, stats_text)
        self.trend_stats_text.config(state=tk.DISABLED)
    
    # Export methods
    def export_current_view(self):
        """Export the currently displayed visualization"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # HIV Case Distribution
            self.export_filtered_data("hiv")
        elif current_tab == 1:  # Population Density
            self.export_filtered_data("population")
        elif current_tab == 2:  # Health Facilities
            self.export_filtered_data("facilities")
        elif current_tab == 3:  # Regional Analysis
            self.export_filtered_data("regional")
        elif current_tab == 4:  # Temporal Trends
            self.export_filtered_data("temporal")
    
    def export_filtered_data(self, data_type):
        """Export filtered data based on current filters"""
        # Get save file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            title=f"Export {data_type.replace('_', ' ').title()} Data"
        )
        
        if not file_path:  # User cancelled
            return
        
        try:
            if data_type == "hiv":
                # Filter HIV data based on current filters
                filtered_data = self.hiv_data.copy()
                
                # Apply time frame filter
                if self.time_frame_var.get() == "Last Year":
                    one_year_ago = datetime.now() - timedelta(days=365)
                    filtered_data = filtered_data[filtered_data['diagnosis_date'] >= one_year_ago]
                elif self.time_frame_var.get() == "Last 5 Years":
                    five_years_ago = datetime.now() - timedelta(days=5*365)
                    filtered_data = filtered_data[filtered_data['diagnosis_date'] >= five_years_ago]
                
                # Apply age group filter
                if self.age_group_var.get() != "All":
                    filtered_data = filtered_data[filtered_data['age_group'] == self.age_group_var.get()]
                
                # Apply gender filter
                if self.gender_var.get() != "All":
                    filtered_data = filtered_data[filtered_data['gender'] == self.gender_var.get()]
                
                # Apply diagnosis status filter
                if self.diagnosis_var.get() != "All":
                    filtered_data = filtered_data[filtered_data['diagnosis_status'] == self.diagnosis_var.get()]
                
                data_to_export = filtered_data
                
            elif data_type == "population":
                # Calculate HIV prevalence by region
                hiv_counts = self.hiv_data['region'].value_counts().reset_index()
                hiv_counts.columns = ['region', 'cases']
                
                # Merge with population data
                data_to_export = pd.merge(hiv_counts, self.population_data, on='region')
                data_to_export['prevalence_rate'] = data_to_export['cases'] / data_to_export['population']
                
            elif data_type == "facilities":
                # Filter facilities based on current filters
                filtered_facilities = self.health_facilities.copy()
                
                # Apply region filter
                if self.facilities_region_var.get() != "All":
                    filtered_facilities = filtered_facilities[filtered_facilities['region'] == self.facilities_region_var.get()]
                
                # Apply facility type filter
                if self.facility_type_var.get() != "All":
                    filtered_facilities = filtered_facilities[filtered_facilities['facility_type'] == self.facility_type_var.get()]
                
                # Apply services filters
                selected_services = [service for service, var in self.services_vars.items() if var.get()]
                if selected_services:
                    filtered_facilities = filtered_facilities[filtered_facilities['services'].apply(
                        lambda x: any(service in x for service in selected_services))]
                
                data_to_export = filtered_facilities
                
            elif data_type == "regional":
                # Filter HIV data based on regional analysis filters
                filtered_data = self.hiv_data.copy()
                
                # Apply region filter
                if self.regional_analysis_var.get() != "All":
                    filtered_data = filtered_data[filtered_data['region'] == self.regional_analysis_var.get()]
                
                # Apply time period filter
                if self.regional_time_var.get() == "Last Year":
                    one_year_ago = datetime.now() - timedelta(days=365)
                    filtered_data = filtered_data[filtered_data['diagnosis_date'] >= one_year_ago]
                elif self.regional_time_var.get() == "Last 3 Years":
                    three_years_ago = datetime.now() - timedelta(days=3*365)
                    filtered_data = filtered_data[filtered_data['diagnosis_date'] >= three_years_ago]
                elif self.regional_time_var.get() == "Last 5 Years":
                    five_years_ago = datetime.now() - timedelta(days=5*365)
                    filtered_data = filtered_data[filtered_data['diagnosis_date'] >= five_years_ago]
                
                data_to_export = filtered_data
                
            elif data_type == "temporal":
                # Filter HIV data based on temporal trends filters
                filtered_data = self.hiv_data.copy()
                
                # Apply region filter
                if self.temporal_region_var.get() != "All":
                    filtered_data = filtered_data[filtered_data['region'] == self.temporal_region_var.get()]
                
                # Apply date range filter
                try:
                    start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
                    end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format in date range.")
                    return
                
                filtered_data = filtered_data[
                    (filtered_data['diagnosis_date'] >= start_date) & 
                    (filtered_data['diagnosis_date'] <= end_date)]
                
                data_to_export = filtered_data
            
            # Save to file
            if file_path.endswith('.xlsx'):
                data_to_export.to_excel(file_path, index=False)
            else:
                data_to_export.to_csv(file_path, index=False)
            
            messagebox.showinfo("Export Successful", f"Data exported successfully to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
    
    def export_all_data(self):
        """Export all data as a zip file"""
        # Get save file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")],
            title="Export All Data as ZIP"
        )
        
        if not file_path:  # User cancelled
            return
        
        try:
            # Create a temporary directory
            temp_dir = "temp_export"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Export each dataset
            self.hiv_data.to_csv(os.path.join(temp_dir, "hiv_cases.csv"), index=False)
            self.population_data.to_csv(os.path.join(temp_dir, "population_data.csv"), index=False)
            self.health_facilities.to_csv(os.path.join(temp_dir, "health_facilities.csv"), index=False)
            
            # Create ZIP file
            import zipfile
            with zipfile.ZipFile(file_path, 'w') as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
            
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir)
            
            messagebox.showinfo("Export Successful", f"All data exported successfully to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
    
    # Help methods
    def show_user_guide(self):
        """Display the user guide"""
        guide_text = """
        Namibia HIV/AIDS GIS Visualization System - User Guide
        
        1. HIV Case Distribution:
        - View spatial distribution of HIV cases
        - Filter by time frame, age group, gender, and diagnosis status
        - Choose between heatmap, scatter plot, or choropleth visualization
        
        2. Population Density:
        - View population density by region
        - Compare with HIV prevalence rates
        - Identify high-risk areas
        
        3. Health Facilities:
        - View locations of health facilities
        - Filter by region, facility type, and services offered
        - Click on facilities to view details
        
        4. Regional Analysis:
        - Compare regions by various metrics
        - View demographic breakdowns
        - Assess policy impacts
        
        5. Temporal Trends:
        - Analyze trends over time
        - View by different time granularities (yearly, quarterly, monthly)
        - Compare different demographic groups
        
        Export:
        - Export current view or all data
        - Supports CSV and Excel formats
        
        For more detailed documentation, please refer to the system manual.
        """
        
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        
        text = tk.Text(guide_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        text.insert(tk.END, guide_text.strip())
        text.config(state=tk.DISABLED)
        
        ttk.Button(guide_window, text="Close", command=guide_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Display about information"""
        about_text = """
        Namibia HIV/AIDS GIS Visualization System
        
        Version: 1.0
        Developed by: [Your Organization]
        
        This application provides spatial and temporal analysis tools for 
        monitoring and managing HIV/AIDS data across Namibia's regions.
        
        Features:
        - Interactive maps and visualizations
        - Demographic analysis tools
        - Health facility mapping
        - Policy impact assessment
        - Data export capabilities
        
        For support or feedback, please contact:
        support@yourorganization.org
        """
        
        messagebox.showinfo("About", about_text.strip())

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = HIVGISApp(root)
    root.mainloop()