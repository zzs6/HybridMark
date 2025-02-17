import pandas as pd
import pycountry
import os
import folium
import pandas as pd
import csv
import numpy as np
from scipy.spatial import distance
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt

from multidatabase_validation import get_IP2Location, get_ipinfo, get_Maxmind, get_ipdata_cloud

from arch import arch_model

import geopandas as gpd
from shapely.geometry import Point

from shapely.geometry import Polygon
import contextily as ctx


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def process_university_data():
    path= r""
    output_file = r""
    df = pd.read_csv(path, encoding='utf-8')
    extracted_data = []

    for index, row in df.iterrows():
        if row['Processed_Result'] == "1" and pd.notna(row['LatLon']) :
            ip_address = row['IP_address']
            location = row['Location']
            latlon = row['LatLon']
            latitude, longitude = latlon.split(',')
            alpha_2 = pycountry.countries.lookup(location).alpha_2
            extracted_data.append([ip_address, location, alpha_2, latitude.strip(), longitude.strip()])
    output_df = pd.DataFrame(extracted_data, columns=['IP_address', 'Country', 'Alpha_2', 'Latitude', 'Longitude'])
    output_df.to_csv(output_file, index=False)

def process_fofa_data():
    source_folder = r''  
    output_file = r'' 
    df = pd.read_csv(source_folder) 
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    extracted_data = []
                    for index, row in df.iterrows():
                        ip_address = row['ip']
                        Alpha_2 = row['country']
                        latitude = row['latitude']
                        longitude = row['longitude']
                        fofa_city_name = row['city']
                        Maxmind_result = get_Maxmind(ip_address)
                        ipdata_cloud_result = get_ipdata_cloud(ip_address)
                        if ipdata_cloud_result == Maxmind_result == fofa_city_name:
                            country =  pycountry.countries.lookup(Alpha_2).name
                            extracted_data.append([ip_address, country, Alpha_2, latitude, longitude])
                        else:
                            continue
                    output_df = pd.DataFrame(extracted_data, columns=['IP_address', 'Country', 'Alpha_2', 'Latitude', 'Longitude'])
                    output_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

def process_cloud_data():
    source_file = r''  
    output_file = r''
    world = gpd.read_file(r"ne_10m_admin_0_countries.shp")
    
    with open(source_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['IP_address', 'Country', 'Alpha_2', 'Latitude', 'Longitude']
        csv_reader = csv.DictReader(infile)
        csv_writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        
        for row in csv_reader:
            ip_address = row['ip_address']
            location = row['location']
            
            try:
                latitude, longitude = map(float, location.split(','))
                print(latitude,longitude)
                point = Point(longitude, latitude)
                for _, country in world.iterrows():
                    if country['geometry'].contains(point):
                        country_name = country['NAME']
                        alpha_2 = country['ISO_A2']
                        if alpha_2 == "-99":
                            alpha_2 = pycountry.countries.lookup(country_name).alpha_2
            
            except Exception as e:
                country, alpha_2 = 'N/A', 'N/A'
            csv_writer.writerow({
                'IP_address': ip_address,
                'Country': country_name,
                'Alpha_2': alpha_2,
                'Latitude': latitude,
                'Longitude': longitude
            })

def show_in_map():
    source_file = r"D:\research\project\landmark\open_source\Geocam_processed.csv"
    output_file = r"D:\research\project\landmark\open_source\Geocam_processed_map.html"  
    data = pd.read_csv(source_file)
    map_center = [data['Latitude'].mean(), data['Longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=2)
    for idx, row in data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=1,
            color='#4169E1',
            fill=True,
            fill_color='#4169E1',
            fill_opacity=0.2
        ).add_to(mymap)
    
    mymap.save(output_file)

def show_in_map_2():
    file_paths = {}
    output_pdf = r""
    colors = ["red", "blue", "green"]
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    world = world[world["name"] != "Antarctica"]
    fig, ax = plt.subplots(figsize=(8, 6))
    world.plot(ax=ax, color="lightgray")

    for (label, file_path), color in zip(file_paths.items(), colors):
        try:
            df = pd.read_csv(file_path)
            if not {"Latitude", "Longitude"}.issubset(df.columns):
                print(f"{file_path} is missing required columns 'Latitude' or 'Longitude'")
                continue
            gdf = gpd.GeoDataFrame(
                df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

            gdf.plot(ax=ax, color=color, markersize=0.1, label=label) 
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    plt.legend(title="Data Source", fontsize="small", title_fontsize="medium", scatterpoints=1)
    plt.title("Geographical Data Visualization")

    plt.savefig(output_pdf, format='png', dpi=300, bbox_inches='tight')
    plt.show()


def total_count_country():
    source_file = r''
    output_file = r''
    df = pd.read_csv(source_file)
    total_count = len(df)
    country_counts = df['Alpha_2'].value_counts()
    print(country_counts)
    country_counts.to_csv(output_file, header=['Count'], index_label='Alpha_2')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def average_nearest_neighbor(points):
    n = len(points)
    if n < 2:
        return np.nan

    distances = []
    for i in range(n):
        lat1, lon1 = points[i]
        min_distance = np.inf
        for j in range(n):
            if i != j:
                lat2, lon2 = points[j]
                dist = haversine(lat1, lon1, lat2, lon2)
                if dist < min_distance:
                    min_distance = dist
        distances.append(min_distance)
    return np.mean(distances)

def data_ann():
    df = pd.read_csv(r"")
    output_file = r''
    
    grouped = df.groupby('Alpha_2')
    nearest_neighbor_results = {}
    for alpha_2, group in grouped:
        lat_lon = group[['Latitude', 'Longitude']].values
        avg_distance = average_nearest_neighbor(lat_lon)
        nearest_neighbor_results[alpha_2] = avg_distance
    results_df = pd.DataFrame(list(nearest_neighbor_results.items()), columns=['Country', 'Average_Nearest_Neighbor_Distance'])
    print(results_df)   
    results_df.to_csv(output_file, index=False)

def create_grid(latitudes, longitudes, grid_size=1.0):

    lat_min, lat_max = min(latitudes), max(latitudes)
    lon_min, lon_max = min(longitudes), max(longitudes)
    lat_bins = np.arange(lat_min, lat_max + grid_size, grid_size)
    lon_bins = np.arange(lon_min, lon_max + grid_size, grid_size)
    
    return lat_bins, lon_bins

def grid_size_eval():
    df = pd.read_csv(r'')
    shapefile_path = r""
    world = gpd.read_file(shapefile_path)
    grouped = df.groupby('Alpha_2')
    grid_size = 5
    grid_coverage_results = []
    for alpha_2, group in grouped:
        country = world[world['ISO_A2'].str.upper() == alpha_2.upper()]
        if country.empty:
            print(f"Country code {alpha_2} not found in the shapefile.")
            continue

        country_boundary = country.geometry.iloc[0]
        minx, miny, maxx, maxy = country_boundary.bounds
        latitudes = group['Latitude'].values
        longitudes = group['Longitude'].values
        lat_bins, lon_bins = create_grid(
            np.array([miny, maxy]), np.array([minx, maxx]), grid_size
        )
        total_grids = (len(lat_bins) - 1) * (len(lon_bins) - 1)
        points_gdf = gpd.GeoDataFrame(
            group, geometry=gpd.points_from_xy(longitudes, latitudes)
        )
        points_in_country = points_gdf[points_gdf.within(country_boundary)]

        if points_in_country.empty:
            print(f"No points found within the country boundary for {alpha_2}.")
            continue
        latitudes = points_in_country.geometry.y
        longitudes = points_in_country.geometry.x
        lat_indices = np.digitize(latitudes, lat_bins) - 1
        lon_indices = np.digitize(longitudes, lon_bins) - 1
        unique_cells = set(zip(lat_indices, lon_indices))
        coverage_count = len(unique_cells)
        coverage_rate = coverage_count / total_grids if total_grids > 0 else 0
        grid_coverage_results.append(
            {
                "Country": alpha_2,
                "Grid_Coverage": coverage_count,
                "Total_Grids": total_grids,
                "Coverage_Rate": round(coverage_rate, 4),
            }
        )
        print(
            f"Country: {alpha_2}, Grid Coverage: {coverage_count}, Total Grids: {total_grids}, Coverage Rate: {coverage_rate:.2%}"
        )

    results_df = pd.DataFrame(grid_coverage_results)
    results_df.to_csv(
        fr"",
        index=False,
    )
    print("Results saved to grid_size.csv")

def latency_stability():
    csv_file = r''
    data = pd.read_csv(csv_file)
    ip_addresses = data.iloc[:, 0]
    latency_data = data.iloc[:, 1:]
    unreachable_value = 999  
    latency_data = latency_data.apply(pd.to_numeric, errors='coerce').fillna(unreachable_value)
    avg_volatility_list = []

    for i, ip in enumerate(ip_addresses):
        series = latency_data.iloc[i].values
        model = arch_model(series, vol='Garch', p=1, q=1)
        fitted_model = model.fit(disp="off")
        avg_volatility = np.mean(fitted_model.conditional_volatility)
        avg_volatility_list.append(avg_volatility)
    avg_volatility_array = np.array(avg_volatility_list)
    sorted_volatility = np.sort(avg_volatility_array)
    cdf = np.arange(1, len(sorted_volatility) + 1) / len(sorted_volatility)
    sorted_volatility = np.insert(sorted_volatility, 0, 0)
    cdf = np.insert(cdf, 0, 0)
    plt.figure(figsize=(8,6))
    plt.plot(sorted_volatility, cdf, linestyle='-', color='blue')
    plt.xlabel('Average Conditional Volatility (ms²)', fontsize=20)
    plt.ylabel('CDF (%)', fontsize=20)
    plt.xlim(left=0) 
    plt.ylim(bottom=0) 
    x_value = 100
    if x_value in sorted_volatility:
        y_value = cdf[np.where(sorted_volatility == x_value)[0][0]]
    else:
        closest_index = (np.abs(sorted_volatility - x_value)).argmin()
        y_value = cdf[closest_index]
    plt.plot([x_value, 0], [y_value, y_value], color='black', linestyle='--') 
    plt.plot([x_value, x_value], [0, y_value], color='black', linestyle='--') 
    plt.text(92, 0.78, f'{y_value:.3f}', color='red',  fontsize=16, ha='center', va='top')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.savefig(r"", format='pdf')
    plt.show()
