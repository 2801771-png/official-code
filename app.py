from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import folium

app = Flask(__name__)
app.secret_key = 'african_minerals_secret_key_2025'

def load_csv(filename):
    data = []
    try:
        with open(f'data/{filename}', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Safely convert numeric fields
                try:
                    if 'GDP_BillionUSD' in row:
                        row['GDP_BillionUSD'] = float(row['GDP_BillionUSD'])
                    if 'MiningRevenue_BillionUSD' in row:
                        row['MiningRevenue_BillionUSD'] = float(row['MiningRevenue_BillionUSD'])
                    if 'MarketPriceUSD_per_tonne' in row:
                        row['MarketPriceUSD_per_tonne'] = float(row['MarketPriceUSD_per_tonne'])
                    if 'Production_tonnes' in row:
                        row['Production_tonnes'] = int(row['Production_tonnes'])
                    if 'ExportValue_BillionUSD' in row:
                        row['ExportValue_BillionUSD'] = float(row['ExportValue_BillionUSD'])
                    if 'Latitude' in row:
                        row['Latitude'] = float(row['Latitude'])
                    if 'Longitude' in row:
                        row['Longitude'] = float(row['Longitude'])
                except (ValueError, TypeError):
                    # If conversion fails, keep original value
                    pass
                
                data.append(row)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
    return data

# Custom Jinja2 filters
@app.template_filter('format_number')
def format_number(value):
    """Format numbers with commas for thousands"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_csv('users.csv')
        user = next((u for u in users if u['Username'] == username), None)
        
        if user and user['Password'] == password:
            session['user_id'] = user['UserID']
            session['username'] = user['Username']
            session['role_id'] = user['RoleID']
            
            # Load role name
            roles = load_csv('roles.csv')
            user_role = next((r for r in roles if r['RoleID'] == user['RoleID']), {})
            session['role_name'] = user_role.get('RoleName', 'User')
            
            flash(f'Login successful! Welcome {session["username"]}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    countries = load_csv('countries.csv')
    minerals = load_csv('minerals.csv')
    production = load_csv('production_stats.csv')
    
    total_countries = len(countries)
    total_minerals = len(minerals)
    
    # Calculate total production
    total_production = sum(item.get('Production_tonnes', 0) for item in production)
    
    return render_template('dashboard.html', 
                         total_countries=total_countries,
                         total_minerals=total_minerals,
                         total_production=total_production)

@app.route('/minerals')
def minerals():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    minerals = load_csv('minerals.csv')
    return render_template('minerals.html', minerals=minerals)

@app.route('/countries')
def countries():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    countries = load_csv('countries.csv')
    stats = load_csv('production_stats.csv')
    minerals = load_csv('minerals.csv')
    
    combined_stats = []
    for stat in stats:
        country = next((c for c in countries if c['CountryID'] == stat['CountryID']), {})
        mineral = next((m for m in minerals if m['MineralID'] == stat['MineralID']), {})
        combined_stats.append({
            'CountryName': country.get('CountryName', 'Unknown'),
            'MineralName': mineral.get('MineralName', 'Unknown'),
            'Year': stat['Year'],
            'Production_tonnes': stat.get('Production_tonnes', 0),
            'ExportValue_BillionUSD': stat.get('ExportValue_BillionUSD', 0)
        })
    
    return render_template('countries.html', 
                         countries=countries,
                         stats=combined_stats)

@app.route('/map')
def map_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    sites = load_csv('sites.csv')
    countries = load_csv('countries.csv')
    minerals = load_csv('minerals.csv')
    
    m = folium.Map(location=[-8, 28], zoom_start=4)
    
    mineral_colors = {
        'Cobalt': 'blue',
        'Lithium': 'green', 
        'Graphite': 'red',
        'Manganese': 'orange'
    }
    
    for site in sites:
        mineral = next((m for m in minerals if m['MineralID'] == site['MineralID']), {})
        country = next((c for c in countries if c['CountryID'] == site['CountryID']), {})
        
        mineral_name = mineral.get('MineralName', 'Unknown')
        country_name = country.get('CountryName', 'Unknown')
        mineral_color = mineral_colors.get(mineral_name, 'purple')
        
        popup_content = f"""
        <div style="min-width: 200px;">
            <h4 style="color: {mineral_color}; margin-bottom: 10px;">{site['SiteName']}</h4>
            <hr style="margin: 5px 0;">
            <p><strong>Country:</strong> {country_name}</p>
            <p><strong>Mineral:</strong> {mineral_name}</p>
            <p><strong>Production:</strong> {site.get('Production_tonnes', 0):,} tonnes</p>
            <p><strong>Coordinates:</strong> {site.get('Latitude', 0)}, {site.get('Longitude', 0)}</p>
        </div>
        """
        
        folium.Marker(
            location=[float(site.get('Latitude', 0)), float(site.get('Longitude', 0))],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"📌 {site['SiteName']} - {mineral_name}",
            icon=folium.Icon(color=mineral_color, icon='info-sign')
        ).add_to(m)
    
    map_html = m._repr_html_()
    return render_template('map.html', map_html=map_html)

@app.route('/charts')
def charts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('charts.html')

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Only allow administrators
    if session.get('role_id') != '1':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    users = load_csv('users.csv')
    roles = load_csv('roles.csv')
    
    # Add role names to users
    for user in users:
        role = next((r for r in roles if r['RoleID'] == user['RoleID']), {})
        user['RoleName'] = role.get('RoleName', 'Unknown')
    
    return render_template('admin_users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)