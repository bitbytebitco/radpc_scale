import os
import csv
import tornado.ioloop
import tornado.web
import tornado.process
import subprocess 
import motor.motor_tornado
import base64
import json
import datetime
import time
from statistics import mean
import numpy as np
import binascii
import math
import requests
from PIL import Image, ImageDraw
import io
import smopy
from staticmap import StaticMap, CircleMarker
import parse_packet_128 as packet

DEBUG = False

async def run_command(command):
    process = tornado.process.Subprocess([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #await process.wait_for_exit()  # This waits without blocking the event loop.
    out, err = process.stdout.read(), process.stderr.read()
    print(out)
    print(err)
    
    return out, err 

class BaseHandler(tornado.web.RequestHandler):
    async def get_packet_data(self, num_rows=100, paynumq=None, date_from=None, date_to=None):
        db = self.settings['db']
        #print('PAYNUMQ {}'.format(paynumq))

        if paynumq == "1":
            print('PL1')
            if date_from is not None and date_to is not None:
                start = datetime.datetime.strptime(date_from, "%m/%d/%Y").isoformat()
                end = datetime.datetime.strptime(date_to, "%m/%d/%Y").isoformat()
                cursor = db.messages.find({"$and":[{"data": {"$exists":True}, "payload":1, "airMessageTime":{"$gte": start, "$lte":end }}]}).sort([("_id",-1)])
            else:
                cursor = db.messages.find({"data": {"$exists":True}, "payload":1}).sort([("_id",-1)])
        elif paynumq == "2":
            print('PL2')
            if date_from is not None and date_to is not None:
                start = datetime.datetime.strptime(date_from, "%m/%d/%Y").isoformat()
                end = datetime.datetime.strptime(date_to, "%m/%d/%Y").isoformat()
                cursor = db.messages.find({"$and":[{"data": {"$exists":True}, "payload":2, "airMessageTime":{"$gte": start, "$lte":end }}]}).sort([("_id",-1)])
            else:
                cursor = db.messages.find({"data": {"$exists":True}, "payload":2}).sort([("_id",-1)])
        else:
            print('condition 3')
            #print(date_from)
            #print(date_to)
            if date_from is not None and date_to is not None:
                #print('tst')
                start = datetime.datetime.strptime(date_from, "%m/%d/%Y").isoformat()
                end = datetime.datetime.strptime(date_to, "%m/%d/%Y").isoformat()
                cursor = db.messages.find({"$and":[{"data": {"$exists":True}, "airMessageTime":{"$gte": start, "$lte":end }}]}).sort([("_id",-1)])
            else:
                print('condition 4')
                cursor = db.messages.find({"data": {"$exists":True}}).sort([("_id",-1)])

        rows = []
        count = 0
        for document in await cursor.to_list(length=num_rows):
            json_data = json.loads(document["data"])
            json_data["i"] = count
            count = count+1
            #print(document)
            #print('data')
            #print(json_data)

            #print(json_data["message"])

            packet_length = packet.get_packet_length(json_data["message"])
            #print("length: {}".format(packet_length))

            if packet_length == 128:
                #print('')
                #print('')
                #print('******')
                #print('******')
                #print('packet_length is 128')

                try:
                    packet_data = packet.parse_from_base64str(json_data["message"])
                    if packet_data is not None:
                        #print("packet_data")
                        #print(packet_data)
                        json_data["packet"] = packet_data
                    else:
                        json_data["packet"] = None
                except Exception as e:
                    print('')
                    print('ISSUE: parse_from_base64str')
                    print(e)


            msg_decoded = base64.b64decode(json_data["message"])
            json_data["message_decoded"] = msg_decoded.hex()
           
            if False: 
                print("PACKET_DATA: {}".format(packet_data))
                #print(msg_decoded)
                print(json_data["message"])
                #print(json_data["latitude"])
                #print(json_data["longitude"])
                #print(json_data["paynum"])
        

            try:
                if 'img_b64' in document and document['img_b64'] is not None:
                    img_str = document['img_b64']
                else:
                    tile_server = "https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}@2x.png?key=tKYZKeMsXOhrrshXAj86" 
                    zoom = 12 
                    lat = json_data['latitude']
                    lon = json_data['longitude']

                    ''' staticmap '''
                    m = StaticMap(512, 512, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

                    marker_outline = CircleMarker((lon, lat), 'white', 18)
                    marker = CircleMarker((lon, lat), '#0036FF', 12)

                    m.add_marker(marker_outline)
                    m.add_marker(marker)

                    image = m.render(zoom=zoom)
                    
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG") 
                    img_str = base64.b64encode(buffered.getvalue())

                    update_result = await db.messages.update_one({"_id": document['_id'] }, {'$set':{'img_b64':img_str, 
                                    "payload": json_data["paynum"], 
                                    "airMessageTime":json_data["airMessageTime"] }})
                    
                json_data['img_b64'] = img_str 

            except Exception as e:
                print(e)

            json_data["message_f"] = "{}{}".format(msg_decoded[0:24].decode('utf-8'),msg_decoded[24:].hex())

            date_obj = datetime.datetime.strptime(json_data['airMessageTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            json_data['at_f'] = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            rows.append(json_data)

        return rows


class MainHandler(BaseHandler):
    async def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (xtile, ytile)

    async def get(self):
        if 'p' in self.request.arguments:
            paynumq = self.get_argument('p')
        else:
            paynumq = None

        date_from = self.get_argument('date_from', None)
        date_to = self.get_argument('date_to', None)
        num_rows = self.get_argument('num_rows', 1000)

        if date_from is None or date_to is None:
            self.redirect('/?date_from=07%2F27%2F2021&date_to=07%2F29%2F2021')

        rows = []
        rows = await self.get_packet_data(num_rows=int(num_rows),date_from=date_from, date_to=date_to)

        self.render("index.html", content=rows, date_from=date_from, date_to=date_to, num_rows=num_rows, row_count=len(rows))

class ChartHandler(BaseHandler):
    async def get(self, start=None, end=None):
        db = self.settings['db']

        q = self.get_argument('q', None)
        paynum = self.get_argument('paynum', None)

        date_from = self.get_argument("date_from", "07/25/2021")
        date_to = self.get_argument("date_to", None)

        sem_inj_fault_correction = self.get_argument("sem_inj_fault_correction", None)

        chart_data = []
        chart_2_data = []
        rows = await self.get_packet_data(num_rows=1000,paynumq=paynum, date_from=date_from, date_to=date_to)
        packet_fields = []
        fields_set = False
    
        #print(int(sem_inj_fault_correction))

        for i, row in enumerate(rows):
            #print("") 
            #print("ROW") 
            #print(row['airMessageTime']) 
            if 'packet' in row:
                #print(row['packet'][q]) 
                if not(fields_set):
                    for f in row['packet']:
                        packet_fields.append(f)
                    fields_set = True

                # 2021-06-07T17:07:30.000Z
                #date_obj = datetime.datetime.strptime(row['airMessageTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                if q == "sem_inj_cnt":
                    chart_2_data.append({'x':row['airMessageTime'], 'y':row['packet']['sem_fault_cnt'] + int(sem_inj_fault_correction)}) 
                chart_data.append({'x':row['airMessageTime'], 'y':row['packet'][q]}) 


        ########### Regression Stuff #####
        ## Math
        #xs = np.array([1,2,3,4,5], dtype=np.float64)
        #ys = np.array([5,4,6,5,6], dtype=np.float64)
       
        ''' 
        def best_fit_slope_and_intercept(xs,ys):
            m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
                 ((mean(xs)*mean(xs)) - mean(xs*xs)))
            
            b = mean(ys) - m*mean(xs)
            
            return m, b

        try:
            rlines = {}
            chart_data.reverse()
            
            #reg_data = chart_data[0:50]
            reg_data = chart_data

            #print("reg_data")
            #print(reg_data)
            for i in reg_data:
                #print('')
                #print(i)
                #minute_deltas = [] 
                #reg_data.reverse() 
                minute_deltas = [{'delta':0, 'i':0, 'date':reg_data[0]['x'].replace("Z", "")}]
                for i,v in enumerate(reg_data):
                    #if i<=16:
                    #    break
                    #print(i)
                    #print(i+1)
                    if i+1 in [i for i, v in enumerate(reg_data)]:
                        current_date = datetime.datetime.fromisoformat(v['x'].replace("Z", ""))
                        next_date = datetime.datetime.fromisoformat(reg_data[i+1]['x'].replace("Z", ""))
                        #print('')
                        #print('')
                        #print(next_date)
                        #print(current_date)
                        sec_diff = next_date - current_date
                        min_diff = sec_diff / datetime.timedelta(minutes=1)
                        minute_deltas.append({'delta':min_diff, 'i': i, 'date':next_date.isoformat()})
            
            print('reg_data')
            #print(reg_data)
            print('here we are')
            #print(minute_deltas)
            data_points = [i['y'] for i in reg_data]
            #data_points.reverse()
            #print(data_points)

            #print("First data points: {}".format(data_points))

            xs = np.array([i['delta'] for i in minute_deltas], dtype=np.float64)
            ys = np.array(data_points, dtype=np.float64)

            print('now here')
            #print(xs)
            #print(ys)

            print(len(xs))
            print(len(ys))

            print('it worked')
            regression_line = []
        
            m, b = best_fit_slope_and_intercept(xs,ys)
            print("m: {}".format(m))
            print("b: {}".format(b))

            print(chart_data[0])
            x_delta = datetime.datetime.fromisoformat(chart_data[-1]['x'].replace("Z", "")) - datetime.datetime.fromisoformat(chart_data[0]['x'].replace("Z", ""))
            time_delta = x_delta / datetime.timedelta(hours=4)
            y_delta = (data_points[-1]-data_points[0])
            #print(data_points[-1]) 
            #print(data_points[0]) 
            #print(y_delta)
            m2 = y_delta/time_delta
            #print("m2: {}".format(m2))
            #b2 = mean(ys) - m2*mean(xs)
            b2 =  data_points[0] 

            xsum = 0
       
            print(data_points) 
            
            for i,x in enumerate(xs):
                ## old 
                xsum = xsum + x
                regression_line.append({"x": "{}Z".format(minute_deltas[i]['date']), "y":(m2*(xsum/len(xs)))+b2})

                ## new?
                step_size = 5
                if i+step_size < len(data_points):
                    rise = data_points[i+step_size] - data_points[i] 
                    print("rise: {}".format(rise))
                    time_delta = datetime.datetime.fromisoformat(chart_data[i+step_size]['x'].replace("Z", "")) - datetime.datetime.fromisoformat(chart_data[i]['x'].replace("Z", ""))
                    run = time_delta / datetime.timedelta(minutes=30)
                    print("run: {}".format(run))
                    m_star = rise/run 
                    print("m_star: {}".format(m_star))
                    print('')
                    regression_line.append({"x": "{}Z".format(minute_deltas[i]['date']), "y":((m_star+b2))})
 
                #print(m_star)
                #print("m: {}".format(m))
                #print("b: {}".format(b))
    
            print('regression_line')
            #print(regression_line)
        except Exception as e:
            print('')
            print('## Regression Issue')
            print(e)
            print('')
        '''           

        #print(chart_data) 
        #print('packet_fields') 
        #print(packet_fields) 

        self.render("chart.html",
            #start=start, 
            #end=end, 
            #segments=segments,
            chart_select=q,
            date_from=date_from,
            date_to=date_to,
            packet_fields=packet_fields,
            row_count=len(chart_data),
            data_points=json.dumps(chart_data),
            data_points_2=json.dumps(chart_2_data),
            sem_inj_fault_correction=sem_inj_fault_correction,
            paynum=paynum,
            #regression_line=json.dumps(regression_line),
            regression_line=json.dumps([]),
            segments=[],
        )

class CallbackHandler(tornado.web.RequestHandler):
    async def do_insert(self, data):
        db = self.settings['db']
        document = {'data': data}
        result = await db.messages.insert_one(document)
        print('result %s' % repr(result.inserted_id))

    '''async def get(self):
        db = self.settings['db']
        await self.do_insert(data=self.request.body.decode('utf-8'))
        self.write('test')'''
            
    async def put(self):
        print('testing put')
        print(self.request.arguments)
        print(self.request.body.decode('utf-8'))
        await self.do_insert(data=self.request.body.decode('utf-8'))

class ObscurityHandler(tornado.web.RequestHandler):
    async def get(self, cmd=None):
        print('ObscurityHandler GET')
        # try to get output using synchronous PIPE for stdin
        if cmd == "start":
            result, error = await run_command('sudo systemctl start raven_rest_caller.service')
            self.write('start')
        elif cmd == "stop":
            result, error = await run_command('sudo systemctl stop raven_rest_caller.service')
            self.write('stop')
        elif cmd == "status":
            result, error = await run_command('sudo systemctl is-active raven_rest_caller.service')
            #result, error = await run_command('sudo systemctl list-units --type=service | grep raven')
            self.write('status: {}'.format(result.decode('utf-8')))
        else:
            self.write('ok')

class SaveHandler(BaseHandler):
    async def get(self):
        paynum = self.get_argument("paynum", 1)
        date_from = self.get_argument("date_from", None)
        date_to = self.get_argument("date_to", None)
        rows = await self.get_packet_data(num_rows=5000, paynumq=paynum, date_from=date_from, date_to=date_to)
    
        print('')
        print('')
        print('########')
        print(len(rows))

        row_names = [] 
        data_rows = []
        fill_header = True
        for rc, r in enumerate(rows):
            new_row = [] # start of data_row

            print(r.keys())
            for k,v in r.items():
                if k not in ["uri","metrics","img_b64", "flightId", "missionId", "at_f", "message_decoded"]: 
                    if k == "packet":
                        print(v)
                        #print(json.loads(v))
                        for i in v:
                            if fill_header:
                                row_names.append(i)
                            new_row.append(v[i])
                            print(i)
                    else:
                        if fill_header:
                            row_names.append(k)
                        new_row.append(v)
                        print(k)
                        print(v)
                    print('')
            data_rows.append(new_row)
            fill_header = False
        print(row_names)
        print('')

        with open('static/data_out.csv', mode='w+') as out_file:
            file_writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            file_writer.writerow(row_names)
            for nr in data_rows:
                print(nr)
                file_writer.writerow(nr)

        self.write('Paynum:{} {}-{} <a href="/static/data_out.csv">data_out.csv</a>'.format(paynum, date_from, date_to))

def make_app():
    SITE_DIR= os.getcwd()
    db = motor.motor_tornado.MotorClient().radpi_callbacks
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/callback", CallbackHandler),
        (r"/chart", ChartHandler),
        (r"/save", SaveHandler),
        (r"/request-caller/(.*)", ObscurityHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': SITE_DIR + "/static/"}),
    ], db=db, debug=True)  

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
