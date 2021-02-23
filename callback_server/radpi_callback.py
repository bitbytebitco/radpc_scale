import os
import tornado.ioloop
import tornado.web
import motor.motor_tornado
import base64
import json
import datetime

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        db = self.settings['db']
        #cursor = db.messages.find({'i': {'$lt': 5}}).sort('i')

        cursor = db.messages.find({"data": {"$exists":True}}).sort([("_id",-1)])
        rows = []
        count = 0
        for document in await cursor.to_list(length=100):
            json_data = json.loads(document["data"])
            json_data["i"] = count
            count = count+1
            #print(document)
            print('data')
            print(json_data)

            msg_decoded = base64.b64decode(json_data["message"])
            json_data["message_decoded"] = msg_decoded
            print(json_data['airMessageTime'])
            date_obj = datetime.datetime.strptime(json_data['airMessageTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            json_data['at_f'] = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            rows.append(json_data)

        self.render("index.html", content=rows)
        #self.write("Hello, world")

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
def make_app():
    SITE_DIR= os.getcwd()
    db = motor.motor_tornado.MotorClient().radpi_callbacks
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/callback", CallbackHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': SITE_DIR + "/static/"}),
    ], db=db, debug=True)  

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
