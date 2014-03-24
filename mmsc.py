#! -*- encoding:utf-8 -*-
import uuid
import tornado.ioloop
import tornado.web
from tornado import httpclient

from xmlparse import parse_xml

def reportMsg(msg):
    dic = msg
    dic["StatusCode"] = 129
    dic["StatusText"] = "Retrieved"
    dic["TransactionID"] = uuid.uuid4().get_hex()
    msgTmpl = '<?xml version="1.0" encoding="GB2312"?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"><env:Header><mm7:TransactionID xmlns:mm7="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0" env:mustUnderstand="1">{TransactionID}</mm7:TransactionID></env:Header><env:Body><DeliveryReportReq xmlns="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0"><MM7Version>{MM7Version}</MM7Version><MMSRelayServerID>902500</MMSRelayServerID><MessageID>{MessageID}</MessageID><Recipient><Number>{DestAddr0}</Number></Recipient><Sender>{SrcAddr}</Sender><TimeStamp>2014-3-24T10:34:50+08:00</TimeStamp><MMStatus>{StatusText}</MMStatus><MMSStatusErrorCode>{StatusCode}</MMSStatusErrorCode><StatusText>OK</StatusText></DeliveryReportReq></env:Body></env:Envelope>'.format(**dic)
    print "report: ", msgTmpl
    return msgTmpl

def sendReport(msg):
    http_client = httpclient.HTTPClient()
    try:
        response = http_client.fetch("http://10.116.40.67:8888/", method='POST', user_agent='MMSC Simulator', body=msg,
                                     headers={'soapAction': '""', 'x-mmsc-msg-from': 'mm7', 'Mime-Version': '1.0', 'Content-Type': 'text/xml; charset=utf-8', 'Content-Transfer-Encoding':'8bit'})
        print response.body
    except httpclient.HTTPError as e:
        print "Error:", e
    http_client.close()


def getContents(contents):
    data = {}
    ret  = False
    for line in contents.split("\r\n"):
        if len(line) <=5:
            continue
        if 'Content-Type' in line:
            if 'Content-Type:text/xml;' in line:
                data['Content-Type'] = line[len('Content-Type')+1:]
                ret = True
            else:
                break
        elif 'Content-Transfer-Encoding' in line:
            data['Content-Transfer-Encoding'] = line[len('Content-Transfer-Encoding')+1:]
        elif '<?xml' in line:
            data['Contents'] = parse_xml(line)
    return ret, data

def respMsg(msg):
    dic = msg
    dic["StatusCode"] = 1000
    dic["StatusText"] = "Success"
    dic["MessageID"] = uuid.uuid4().get_hex()
    msgTmpl = '<?xml version="1.0" encoding="UTF-8"?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"><env:Header><mm7:TransactionID xmlns:mm7="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0" env:mustUnderstand="1">{TransactionID}</mm7:TransactionID></env:Header><env:Body><SubmitRsp xmlns="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0"><MM7Version>{MM7Version}</MM7Version><Status><StatusCode>{StatusCode}</StatusCode><StatusText>{StatusText}</StatusText></Status><MessageID>{MessageID}</MessageID></SubmitRsp></env:Body></env:Envelope>'.format(**dic)
    report = reportMsg(dic)
    return msgTmpl, report

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
    def post(self):
        msg = []
        for contents in self.request.body.split("--=MMS_delimiter="):
            ret,data = getContents(contents)
            if ret:
                msg.append(data)
            else:
                msg.append(contents)
        resp, report = respMsg(msg[1].get('Contents'))
        # print "resp: ", resp, len(resp)
        self.set_header('Content-Type', 'text/xml; charset=UTF-8')
        self.write(resp)
        sendReport(report)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/mmsc/center/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8000, address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
