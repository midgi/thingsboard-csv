import urllib.parse
import datetime
import time
from flask import Flask, render_template, request, redirect, url_for, make_response, Response
from thingsboard import ThingsBoardHTTP, thingsboardJSON2CSV

app = Flask(__name__, template_folder="templates", static_folder="assets")

@app.route('/')
def index():
    return redirect('/auth/login')

@app.route('/auth/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        host     = request.form.get('inputHost')
        port     = int(request.form.get('inputPort'))
        username = request.form.get('inputUser')
        password = request.form.get('inputPassword')

        thingsboard = ThingsBoardHTTP(host, port=port)
        if(thingsboard.login(username, password)):
            data = {
                "host": host,
                "port": port,
                "username": username,
                "token": thingsboard.userToken
            }
            return redirect('/downloader?'+urllib.parse.urlencode(data))
        else:
            return redirect('/login')
    
    return render_template("index.html")

@app.route('/downloader', methods=['GET'])
def downloader():
    host        = request.args.get('host')
    port        = int(request.args.get('port'))
    token       = request.args.get('token')
    thingsboard = ThingsBoardHTTP(host, port=port)
    thingsboard.userToken = token
    print("token: %s"%token)
    customer_list = thingsboard.customerList(0, 10)['data']
    device_list = thingsboard.customerDeviceList(customer_list[0]['id']['id'], 0, 10)['data']
    print("device_list: ",device_list)
    return render_template("downloader.html", customer_list = customer_list, 
        device_list = device_list, token=token, port=port, host=host)

@app.route('/download', methods=['POST'])
def download():
    host        = request.form.get('host')
    port        = int(request.form.get('port'))
    token       = request.form.get('token')
    device_id   = request.form.get('inputDevice')
    keys        = request.form.getlist('inputKeys[]')
    start_ts    = request.form.get('inputStartTime')
    end_ts      = request.form.get('inputEndTime')
    start_ts    = time.mktime(datetime.datetime.strptime(start_ts, "%Y-%m-%d %H:%M").timetuple())
    end_ts      = time.mktime(datetime.datetime.strptime(end_ts, "%Y-%m-%d %H:%M").timetuple())
    thingsboard = ThingsBoardHTTP(host, port=port)
    thingsboard.userToken = token

    
    timeseries_json = thingsboard.getTimeSeries(device_id, keys, start_ts*1000, end_ts*1000)
    csv = thingsboardJSON2CSV(timeseries_json)
    
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=backup.csv"})

@app.route('/devices', methods=['GET'])
def devices():
    host                    = request.args.get('host')
    port                    = int(request.args.get('port'))
    token                   = request.args.get('token')
    customerId              = request.args.get('customer')
    thingsboard             = ThingsBoardHTTP(host, port=port)
    thingsboard.userToken   = token
    device_list = thingsboard.customerDeviceList(customerId, 0, 10)['data']
    html = ""
    for device in device_list:
        html += '<option value="%s">%s</option>'%(device["id"]["id"], device["name"])
    return html

if __name__ == '__main__':
    app.run()