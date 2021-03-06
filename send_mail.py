import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import datetime
from jinja2 import Template
import json
from bs4 import BeautifulSoup

MAIL_TO_ME=True
DEBUGGING_MODE=False

from custom_decorators import *
import config

class WorkLog:
    def __init__(self,name=config.email,email=config.email):
        self.name=name
        self.email=email
        self.mailto=config.mail_to_debug if MAIL_TO_ME else config.mail_to_final
        self.cc=config.cc_final
        self.date=str(datetime.date.today())+" "+datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d').strftime('%A')
        self.worklog={
        'task_of_today':[],
        'task_completed':[],
        'problems_faced':[],
        'planning_for_tomorrow':[]}
        self.history=None
        self.html_body=None
        self.rendered_html=None

    def load_history(self):
        with open("worklog.json","r") as json_file:
            log=json.load(json_file)[-1]
        if self.date in log:
            self.history=log[self.date]
            return True
        else:
            return False

    def load_html(self):
        with open("mail_template.html") as reader:
            self.html_body=reader.read()
        html_template=Template(self.html_body)
        self.rendered_html=html_template.render(name=self.name, \
            date=self.date, \
            task_today=self.worklog['task_of_today'], \
                task_completed=self.worklog['task_completed'], \
                    issues=self.worklog['problems_faced'], \
                        plans_tomorrow=self.worklog['planning_for_tomorrow'])
        if DEBUGGING_MODE:
            soup=BeautifulSoup(self.rendered_html,'html.parser')
            print(soup.prettify())

    # @color_console('green')
    def save_worklog(self):
        with open("worklog.json","r") as json_file:
            log=json.load(json_file)
        log.append({str(self.date):self.worklog})
        with open("worklog.json","w") as json_file:
            json.dump(log,json_file)
        print("Worklog saved to file...")


    def input_logs(self):
        for key in self.worklog:
            change_color('green')
            print("Enter: "+key+":<enter twice to end>:")
            change_color()
            input_string=None
            if key=='task_completed':
                for task in self.worklog['task_of_today']:
                    print("\t>"+task)
                    self.worklog[key].append(task)
            while (input_string!=''):
                if input_string in ['re','RE','Re']:
                    self.worklog[key].pop()
                    delete_prev_line(2)
                elif input_string:
                    self.worklog[key].append(input_string)
                input_string=input("\t>")
            delete_prev_line()
        if not DEBUGGING_MODE:
            self.save_worklog()


    def send_mail(self):
        change_color('yellow')
        print("Creating email.... Please wait...")
        MY_KEY=config.ZOHO_KEY
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.mailto
        msg['cc']=self.cc
        msg['Subject'] = "Re: Work Log: "+self.name
        msg.attach(MIMEText(self.rendered_html, 'html'))
        server = smtplib.SMTP('smtp.zoho.com:587')
        server.starttls()
        server.login(self.email,MY_KEY)
        text = msg.as_string()
        print("Sending email.... Please wait...")
        server.sendmail(self.email, self.mailto, text)
        server.quit()
        change_color('green')
        print("Process completed, your email is sent.")
        change_color()

if __name__=="__main__":
    try:
        log=WorkLog()
        if log.load_history():
            change_color('bred')
            print("You have a worklog entry for this date:")
            change_color()
            print("do you want to send that to:"+log.mailto+"?\n<y>/n:")
            response=input("")
            if response not in ['\n','y','']:
                log.input_logs()
            else:
                log.worklog=log.history
        else:
            log.input_logs()
        log.load_html()
        if not DEBUGGING_MODE:
            log.send_mail()
        else:
            print("Debugging mode: reached end of program...")
    except KeyboardInterrupt:
        print("\nProcess terminated..")
