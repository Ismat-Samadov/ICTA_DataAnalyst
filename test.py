import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


# Load the Excel files
attendance_data = pd.read_excel('data/attendance.xlsx')
holiday_data = pd.read_excel('data/holiday.xlsx')
permission_data = pd.read_excel('data/permission.xlsx')

# Data Preparation and KPI Calculation
attendance_data['Entry'] = pd.to_datetime(attendance_data['Entry'], format='%H:%M')
attendance_data['Exit'] = pd.to_datetime(attendance_data['Exit'], format='%H:%M')
attendance_data['Work_Hours'] = (attendance_data['Exit'] - attendance_data['Entry']).dt.total_seconds() / 3600

# Calculate overtime and delay
attendance_data['Overtime'] = attendance_data['Work_Hours'] - 8
attendance_data['Overtime'] = attendance_data['Overtime'].apply(lambda x: x if x > 0 else 0)
attendance_data['Delay'] = 8 - attendance_data['Work_Hours']
attendance_data['Delay'] = attendance_data['Delay'].apply(lambda x: x if x > 0 else 0)

# Calculate fines and bonuses based on delay and overtime
attendance_data['Fine'] = 0
attendance_data.loc[attendance_data['Delay'] > 3, 'Fine'] = 0.02
attendance_data.loc[attendance_data['Delay'] > 10, 'Fine'] = 0.03
attendance_data.loc[attendance_data['Delay'] > 20, 'Fine'] = 0.05

attendance_data['Bonus'] = 0
attendance_data.loc[attendance_data['Overtime'] > 3, 'Bonus'] = 0.02
attendance_data.loc[attendance_data['Overtime'] > 10, 'Bonus'] = 0.03
attendance_data.loc[attendance_data['Overtime'] > 20, 'Bonus'] = 0.05

# Create a Dash app
app = dash.Dash(__name__)

# Expose the Flask server instance for gunicorn
server = app.server

# Layout
app.layout = html.Div([
    html.H1("Employee Attendance Performance Dashboard"),
    
    # Dropdown for selecting department
    html.Label("Select Department"),
    dcc.Dropdown(
        id='department-dropdown',
        options=[{'label': dept, 'value': dept} for dept in attendance_data['Department'].unique()],
        value=attendance_data['Department'].unique()[0]
    ),

    # Dropdown for selecting employee
    html.Label("Select Employee"),
    dcc.Dropdown(
        id='employee-dropdown',
        value=attendance_data['Employee'].unique()[0]
    ),
    
    # Dropdown for selecting time period
    html.Label("Select Time Period"),
    dcc.Dropdown(
        id='time-period-dropdown',
        options=[
            {'label': 'Monthly', 'value': 'M'},
            {'label': 'Yearly', 'value': 'Y'}
        ],
        value='M'
    ),

    # KPI Graphs
    dcc.Graph(id='work-hours-graph'),
    dcc.Graph(id='fines-bonuses-graph'),
    dcc.Graph(id='overtime-delay-pie-chart'),
    dcc.Graph(id='department-avg-work-hours'),
    dcc.Graph(id='attendance-trend-graph')
])

# Callback to update employee dropdown based on selected department
@app.callback(
    Output('employee-dropdown', 'options'),
    Input('department-dropdown', 'value')
)
def update_employee_dropdown(selected_department):
    employees = attendance_data[attendance_data['Department'] == selected_department]['Employee'].unique()
    return [{'label': emp, 'value': emp} for emp in employees]

# Callback to update work hours graph based on selected employee
@app.callback(
    Output('work-hours-graph', 'figure'),
    [Input('department-dropdown', 'value'),
     Input('employee-dropdown', 'value'),
     Input('time-period-dropdown', 'value')]
)
def update_work_hours_graph(selected_department, selected_employee, time_period):
    filtered_data = attendance_data[(attendance_data['Department'] == selected_department) & 
                                    (attendance_data['Employee'] == selected_employee)]
    
    fig = px.bar(filtered_data, x='Date', y='Work_Hours', title='Work Hours Over Time')
    return fig

# Callback to update fines and bonuses graph
@app.callback(
    Output('fines-bonuses-graph', 'figure'),
    [Input('department-dropdown', 'value'),
     Input('employee-dropdown', 'value')]
)
def update_fines_bonuses_graph(selected_department, selected_employee):
    filtered_data = attendance_data[(attendance_data['Department'] == selected_department) & 
                                    (attendance_data['Employee'] == selected_employee)]
    
    fig = px.bar(filtered_data, x='Date', y=['Fine', 'Bonus'], title='Fines and Bonuses Over Time')
    return fig

# Callback to update overtime and delay pie chart
@app.callback(
    Output('overtime-delay-pie-chart', 'figure'),
    [Input('department-dropdown', 'value'),
     Input('employee-dropdown', 'value')]
)
def update_overtime_delay_pie_chart(selected_department, selected_employee):
    filtered_data = attendance_data[(attendance_data['Department'] == selected_department) & 
                                    (attendance_data['Employee'] == selected_employee)]
    
    total_overtime = filtered_data['Overtime'].sum()
    total_delay = filtered_data['Delay'].sum()
    
    fig = px.pie(values=[total_overtime, total_delay], 
                 names=['Overtime', 'Delay'], 
                 title='Overtime vs Delay Distribution')
    return fig

# Callback to update average work hours by department
@app.callback(
    Output('department-avg-work-hours', 'figure'),
    Input('department-dropdown', 'value')
)
def update_department_avg_work_hours(selected_department):
    department_data = attendance_data[attendance_data['Department'] == selected_department]
    avg_work_hours = department_data.groupby('Employee')['Work_Hours'].mean().reset_index()
    
    fig = px.bar(avg_work_hours, x='Employee', y='Work_Hours', title='Average Work Hours by Employee')
    return fig

# Callback to show attendance trends over time
@app.callback(
    Output('attendance-trend-graph', 'figure'),
    [Input('department-dropdown', 'value'),
     Input('employee-dropdown', 'value'),
     Input('time-period-dropdown', 'value')]
)
def update_attendance_trend_graph(selected_department, selected_employee, time_period):
    filtered_data = attendance_data[(attendance_data['Department'] == selected_department) & 
                                    (attendance_data['Employee'] == selected_employee)]
    
    fig = px.line(filtered_data, x='Date', y='Work_Hours', title='Attendance Trends Over Time')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
