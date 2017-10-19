import re
import requests
import dryscrape
import time
import random

s = requests.session()

un = "CHANGEME: your username"
pw = "CHANGEME: your password"
url = "CHANGEME: url of assignment (everything after 'https://learn.zybooks.com')"

with open('static/js/dragndrop.js', 'r') as f:
    js = f.read()

session = dryscrape.Session(base_url="https://learn.zybooks.com")
session.set_header("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25")
session.set_error_tolerant(True)

session.visit("/")
session.at_xpath("//div[@class='zb-card-content']//input[@type='email']").set(un)
session.at_xpath("//div[@class='zb-card-content']//input[@type='password']").set(pw)
session.at_xpath("//div[@class='zb-card-content']//button").click()
session.wait_for(lambda: session.at_xpath("//div[@class='zybook-info']"))

for i in range(2,3):
    session.visit(url.format(i))
    print('Section {}'.format(i))
    session.wait_for(lambda: session.at_xpath("//h1[@class='zybook-section-title']"))

    # Multiple choice
    mc_q = re.findall(r'<div id=\"(ember\d{1,6})\" class=\"question-set-question multiple-choice-question', session.body())
    for q in mc_q:
        question = session.at_xpath("//div[@id='{}']//fieldset".format(q))
        if question:
            print('MULTIPLE CHOICE QUESTION')
            choices = question.children()
            keepClicking = True
            while keepClicking:
                for choice in choices:
                    if session.at_xpath("//div[@id='{}']//div[@aria-label='Question completed']".format(q)):
                        print('COMPLETE')
                        keepClicking = False
                        break
                    print('CLICKING {}'.format(str(choice)))
                    session.driver.exec_script('document.getElementById("{}").getElementsByTagName("input")[0].click();'.format(choice.get_attr('id')))

    # Short answer
    sa_q = re.findall(r'<div id=\"(ember\d{1,6})\" class=\"question-set-question short-answer-question', session.body())
    for q in sa_q:
        print('SHORT ANSWER')
        input_id = session.at_xpath("//div[@id='{}']//pre//textarea".format(q)).get_attr('id')
        time.sleep(2)
        js = "document.getElementById('{}').getElementsByClassName('show-answer-button')[0].click()".format(q)
        session.exec_script(js)
        time.sleep(1)
        session.exec_script(js)
        js = "document.getElementById('{}').value = document.getElementById('{}').getElementsByClassName('forfeit-answer')[0].innerHTML;".format(input_id, q)
        session.exec_script(js)
        time.sleep(2)
        js = "document.getElementById('{}').getElementsByClassName('check-button')[0].click()".format(q)
        session.exec_script(js)
        print('COMPLETE')
    # Demo Animations
    demos = re.findall(r'<div id=\"(ember\d{1,8})\" class=\"content-resource animation-canvas', session.body())
    for demo in demos:
        print('WATCH DEMO')
        if session.at_xpath(session.at_xpath("//div[@id='{}']".format(demo)).parent().parent().path() + "//div[@aria-label='Activity completed']"):
            print('SKIPPING')
#            continue
        session.driver.exec_script('document.getElementById("{}").getElementsByTagName("input")[0].click();'.format(demo))
        session.driver.exec_script('document.getElementById("{}").getElementsByClassName("start-button start-graphic")[0].click();'.format(demo))
        while True:
            try:
                session.wait_while(lambda: session.at_xpath("//div[@id='{}']//div[@class='play-button disabled  ']".format(demo)))
                session.driver.exec_script('document.getElementById("{}").getElementsByClassName("play-button   bounce")[0].click();'.format(demo))
            except:
                break
        print('DONE')

    # Drag and Drop
    dnds = re.findall(r'<div id=\"(ember\d{1,6})\" class=\"draggable-object-target', session.body())
    tids = re.findall(r'<div id=\"(ember\d{1,6})\" class=\"definition-drag-container', session.body())
    for dnd in dnds:
        print('MATCHING')
        if session.at_xpath(session.at_xpath("//div[@id='{}']".format(dnd)).parent().parent().parent().path() + "//div[@aria-label='Activity completed']"):
            print('SKIPPING')
            continue
        for i in range(len(session.at_xpath("//div[@id='{}']//ul[@class='term-bank']".format(dnd)).children())):
            draggable = session.at_xpath("//div[@id='{}']//ul[@class='term-bank']//li[{}]//div[@draggable='true']".format(dnd, 1))
            print(draggable)
            for tid in tids:
                target = session.at_xpath("//div[@id='{}']//div[@class='term-bucket ']".format(tid))
                if not target:
                    print('notice: no target')
                    continue
                target.set_attr('id', 'target-drop')
                action = "$('#{}')".format(draggable.get_attr('id')) + ".simulateDragDrop({ dropTarget: '#target-drop'});"
                session.exec_script(js + action)
                target.set_attr('id', '')
                if session.at_xpath("//div[@id='{}']/following-sibling::div[@class='explanation ']".format(tid)):
                    print('NOT ANSWERED')
                    draggable = session.at_xpath("//div[@id='{}']//div[@class='term-bucket populated']//div[@draggable='true']".format(tid))
                    print(draggable)
                if session.at_xpath("//div[@id='{}']/following-sibling::div[@class='explanation incorrect']".format(tid)):
                    print('INCORRECT')
                    draggable = session.at_xpath("//div[@id='{}']//div[@class='term-bucket populated']//div[@draggable='true']".format(tid))
                    print(draggable)
                if session.at_xpath("//div[@id='{}']/following-sibling::div[@class='explanation correct']".format(tid)):
                    print('CORRECT')
                    break





