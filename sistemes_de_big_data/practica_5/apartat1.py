# Required imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import warnings
warnings.filterwarnings('ignore')

# Read the CSV file
df = pd.read_csv('31949.csv', sep=';')

# Helper function to group ages
def group_ages(age):
    if age == 'Todas las edades':
        return age
    age = int(age)
    if age <= 19:
        return 'Fins a 19 anys'
    elif age <= 29:
        return 'De 20 a 29 anys'
    elif age <= 39:
        return 'De 30 a 39 anys'
    elif age <= 49:
        return 'De 40 a 49 anys'
    else:
        return '50 anys o més'

# Helper function to group birth orders
def group_birth_order(order):
    if order == 'Todos':
        return order
    elif order == 'Primero':
        return 'Primer fill'
    elif order == 'Segundo':
        return 'Segon fill'
    else:
        return 'Tercer fill o posterior'

# Add grouped columns
df['age_group'] = df['Edad de la madre'].apply(group_ages)
df['birth_order_group'] = df['Orden del nacido vivo'].apply(group_birth_order)

# 1. Pie chart with Matplotlib - births by mother's age group in 2023
plt.figure(figsize=(10, 8))
data_2023 = df[
    (df['Periodo'] == 2023) & 
    (df['Nacional y Comunidades autónomas'] == 'Total Nacional') &
    (df['Orden del nacido vivo'] == 'Todos') &
    (df['age_group'] != 'Todas las edades')
]
age_totals = data_2023.groupby('age_group')['Total'].sum()
colors = sns.color_palette('husl', n_colors=len(age_totals))
plt.pie(age_totals, labels=age_totals.index, autopct='%1.1f%%', colors=colors)
plt.title('Percentatge de naixements per grup d\'edat de la mare (2023)')
plt.show()

# 2. Grouped bar chart with Seaborn - Mediterranean communities
mediterranean = ['Balears, Illes', 'Catalunya', 'Comunitat Valenciana', 'Murcia, Región de', 'Andalucía']
med_data = df[
    (df['Periodo'] == 2023) &
    (df['Nacional y Comunidades autónomas'].isin(mediterranean)) &
    (df['Orden del nacido vivo'] == 'Todos') &
    (df['age_group'] != 'Todas las edades')
]

plt.figure(figsize=(12, 6))
sns.barplot(
    data=med_data,
    x='Nacional y Comunidades autónomas',
    y='Total',
    hue='age_group',
    errorbar=None
)
plt.xticks(rotation=45)
plt.title('Naixements per grup d\'edat de la mare - Comunitats Mediterrànies (2023)')
plt.xlabel('Comunitat Autònoma')
plt.ylabel('Nombre de naixements')
plt.legend(title='Grup d\'edat')
plt.tight_layout()
plt.show()

# 3. Grouped bar chart with Plotly - births by order over time
national_data = df[
    (df['Nacional y Comunidades autónomas'] == 'Total Nacional') &
    (df['Edad de la madre'] == 'Todas las edades') &
    (df['birth_order_group'] != 'Todos')
]
yearly_orders = national_data.groupby(['Periodo', 'birth_order_group'])['Total'].sum().reset_index()

fig = px.bar(
    yearly_orders,
    x='Periodo',
    y='Total',
    color='birth_order_group',
    barmode='group',
    title='Naixements per ordre de naixement (2009-2023)'
)
fig.update_layout(
    xaxis_title='Any',
    yaxis_title='Nombre de naixements',
    legend_title='Ordre de naixement'
)
fig.show()

# 4. Line plot with Seaborn - evolution of births by order
plt.figure(figsize=(12, 6))
yearly_orders = national_data.groupby(['Periodo', 'birth_order_group'])['Total'].sum().reset_index()
sns.lineplot(
    data=yearly_orders,
    x='Periodo',
    y='Total',
    hue='birth_order_group',
    marker='o'
)
plt.title('Evolució dels naixements per ordre de naixement (2009-2023)')
plt.xlabel('Any')
plt.ylabel('Nombre de naixements')
plt.legend(title='Ordre de naixement')
plt.show()

# 5. Line plot with Plotly - Balearic Islands evolution by age group
balearic_data = df[
    (df['Nacional y Comunidades autónomas'] == 'Balears, Illes') &
    (df['Orden del nacido vivo'] == 'Todos') &
    (df['age_group'] != 'Todas las edades')
]
yearly_ages = balearic_data.groupby(['Periodo', 'age_group'])['Total'].sum().reset_index()

fig = px.line(
    yearly_ages,
    x='Periodo',
    y='Total',
    color='age_group',
    markers=True,
    title='Evolució dels naixements a les Illes Balears per grup d\'edat (2009-2023)'
)
fig.update_layout(
    xaxis_title='Any',
    yaxis_title='Nombre de naixements',
    legend_title='Grup d\'edat'
)
fig.show()

# 6. Boxplot with Seaborn - Balearic Islands births by age group
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=balearic_data,
    x='age_group',
    y='Total',
    palette='husl'
)
plt.title('Distribució dels naixements a les Illes Balears per grup d\'edat (2009-2023)')
plt.xlabel('Grup d\'edat')
plt.ylabel('Nombre de naixements')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 7. Boxplot with Plotly - Mediterranean communities
med_data_all = df[
    (df['Nacional y Comunidades autónomas'].isin(mediterranean)) &
    (df['Orden del nacido vivo'] == 'Todos') &
    (df['Edad de la madre'] == 'Todas las edades')
]

fig = px.box(
    med_data_all,
    x='Nacional y Comunidades autónomas',
    y='Total',
    color='Nacional y Comunidades autónomas',
    title='Distribució dels naixements a les comunitats mediterrànies (2009-2023)'
)
fig.update_layout(
    xaxis_title='Comunitat Autònoma',
    yaxis_title='Nombre de naixements',
    showlegend=True
)
fig.show()

# 8. Dash interface
app = Dash(__name__)

app.layout = html.Div([
    html.H1('Naixements per comunitat autònoma'),
    dcc.Dropdown(
        id='community-dropdown',
        options=[{'label': i, 'value': i} for i in df['Nacional y Comunidades autónomas'].unique()],
        value='Total Nacional'
    ),
    dcc.Graph(id='birth-order-graph')
])

@app.callback(
    Output('birth-order-graph', 'figure'),
    Input('community-dropdown', 'value')
)
def update_graph(selected_community):
    community_data = df[
        (df['Nacional y Comunidades autónomas'] == selected_community) &
        (df['Periodo'] == 2023) &
        (df['age_group'] != 'Todas las edades') &
        (df['birth_order_group'] != 'Todos')
    ]
    
    fig = px.bar(
        community_data,
        x='age_group',
        y='Total',
        color='birth_order_group',
        barmode='group',
        title=f'Naixements a {selected_community} per grup d\'edat i ordre (2023)'
    )
    
    fig.update_layout(
        xaxis_title='Grup d\'edat',
        yaxis_title='Nombre de naixements',
        legend_title='Ordre de naixement'
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)