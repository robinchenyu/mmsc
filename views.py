#! -*- encoding: utf-8 -*-
import uuid
import os

import tornado.web
from tornado import httpclient

from settings import settings
from xmlparse import parse_xml
from readxls import resolv

def reportMsg(msg):
    dic = msg
    dic["RStatusCode"] = 129
    dic["RStatusText"] = "Retrieved"
    dic["RTransactionID"] = uuid.uuid4().get_hex()
    msgTmpl = '<?xml version="1.0" encoding="GB2312"?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"><env:Header><mm7:TransactionID xmlns:mm7="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0" env:mustUnderstand="1">{RTransactionID}</mm7:TransactionID></env:Header><env:Body><DeliveryReportReq xmlns="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0"><MM7Version>{MM7Version}</MM7Version><MMSRelayServerID>902500</MMSRelayServerID><MessageID>{MessageID}</MessageID><Recipient><Number>{DestAddr0}</Number></Recipient><Sender>{SrcAddr}</Sender><TimeStamp>2014-3-24T10:34:50+08:00</TimeStamp><MMStatus>{RStatusText}</MMStatus><MMSStatusErrorCode>{RStatusCode}</MMSStatusErrorCode><StatusText>OK</StatusText></DeliveryReportReq></env:Body></env:Envelope>'.format(**dic)
    # print "report: ", msgTmpl
    return msgTmpl

def sendReport(msg):
    http_client = httpclient.AsyncHTTPClient()
    def handle_request(response):
        if response.error:
            print "Error:", response.error
        # else:
        #     print response.body
    http_client.fetch("http://10.116.40.67:8888/", handle_request, method='POST', user_agent='MMSC Simulator', body=msg, headers={'soapAction': '""', 'x-mmsc-msg-from': 'mm7', 'Mime-Version': '1.0', 'Content-Type': 'text/xml; charset=utf-8', 'Content-Transfer-Encoding':'8bit'})


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
    report = reportMsg(dic)
    return dic, report




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
        self.render("resp.xml", **resp)
        sendReport(report)

class XlsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/xls/upload.html")

    def post(self):
        start_time = self.get_argument("start_time", "08:00")
        end_time = self.get_argument("end_time", "19:00")
        if len(start_time) < 5:
            start_time = "08:00"
        if len(end_time) < 5:
            end_time = "19:00"

        print "start_time:%s, end_time: %s " % (start_time, end_time)
        try:
            fbody = self.request.files.get('file')[0]
            if fbody and fbody.get('content_type') == 'application/vnd.ms-excel':
                filename = os.path.join(settings.get('static_path'), fbody.get('filename', 'data.xls'))
                print "save file: ", filename
                with open(filename, "w") as fw:
                    fw.write(fbody.get('body'))
                out_file, form, origin_form = resolv(filename, "08:00", "19:00")
            self.render("templates/xls/download.html", form=form, origin_form=origin_form,
                        start_time = start_time, end_time = end_time, file_url = "/static/out.csv", file_name=out_file)
        except Exception as e:
            print "ERror file:", e
            self.write("failed")
