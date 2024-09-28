import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data
file_path = 'data/monthly_fines_bonuses.xlsx'  # Update this with the correct path to your file
monthly_data = pd.read_excel(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # This is necessary for Gunicorn to recognize the app

# App layout with multiple pages and dropdowns
app.layout = html.Div([
    html.H1("Employee Performance Dashboard"),

    # Page Navigation
    dcc.Tabs(id="tabs", value='overview', children=[
        dcc.Tab(label='Overview Dashboard', value='overview'),
        dcc.Tab(label='Employee Comparison', value='employee_comparison'),
        dcc.Tab(label='Department Performance', value='department_performance'),
        dcc.Tab(label='Fines and Bonuses Report', value='fines_bonuses_report'),
    ]),

    html.Div(id='content')
])

# Update the layout for different tabs
@app.callback(Output('content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'overview':
        # Page 1: Overview Dashboard
        return html.Div([
            html.H3('Overview Dashboard'),
            dcc.Graph(
                id='total-overtime-bar',
                figure=px.bar(monthly_data.groupby('Employee')['Overtime'].sum().reset_index(), 
                              x='Employee', y='Overtime', title='Total Overtime by Employee')
            ),
            dcc.Graph(
                id='total-delay-bar',
                figure=px.bar(monthly_data.groupby('Employee')['Delay'].sum().reset_index(), 
                              x='Employee', y='Delay', title='Total Delay by Employee')
            ),
            dcc.Graph(
                id='total-fines-bonuses',
                figure=px.bar(monthly_data.groupby('Employee')[['Fine', 'Bonus']].sum().reset_index(),
                              x='Employee', y=['Fine', 'Bonus'], barmode='group', 
                              title='Total Fines and Bonuses by Employee')
            )
        ])
    
    elif tab == 'employee_comparison':
        # Page 2: Employee Comparison
        return html.Div([
            html.H3('Employee Comparison'),
            dcc.Graph(
                id='work-hours-comparison',
                figure=px.bar(monthly_data, x='Employee', y='Overtime', title='Comparison of Employee Overtime')
            ),
            dcc.Graph(
                id='top-5-overtime',
                figure=px.bar(monthly_data.nlargest(5, 'Overtime'), x='Employee', y='Overtime', 
                              title='Top 5 Employees with Most Overtime')
            ),
            dcc.Graph(
                id='fine-bonus-comparison',
                figure=px.bar(monthly_data, x='Employee', y=['Fine', 'Bonus'], barmode='group', 
                              title='Fine and Bonus Comparison by Employee')
            )
        ])
    
    elif tab == 'department_performance':
        # Page 3: Department Performance
        department_grouped = monthly_data.groupby('Department')[['Overtime', 'Delay']].sum().reset_index()
        return html.Div([
            html.H3('Department Performance'),
            dcc.Graph(
                id='overtime-delay-department',
                figure=px.bar(department_grouped, x='Department', y=['Overtime', 'Delay'], 
                              barmode='group', title='Overtime and Delay by Department')
            )
        ])
    
    elif tab == 'fines_bonuses_report':
        # Page 4: Fines and Bonuses Report
        return html.Div([
            html.H3('Fines and Bonuses Report'),
            dcc.Graph(
                id='fines-bonuses-overtime-line',
                figure=px.line(monthly_data.groupby('Employee')[['Fine', 'Bonus']].sum().reset_index(),
                               x='Employee', y=['Fine', 'Bonus'], 
                               title='Fines and Bonuses Over Time (Line Chart)')
            ),
            dcc.Graph(
                id='top-employee-fines',
                figure=px.bar(monthly_data.nlargest(5, 'Fine'), x='Employee', y='Fine', 
                              title='Top Employees with Highest Fines')
            )
        ])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=False)
