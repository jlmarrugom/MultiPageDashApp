import dash
from whitenoise import WhiteNoise
external_stylesheets = ['https://codepen.io/chriddyp/pen/dZVMbK.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app,
root='static/')
