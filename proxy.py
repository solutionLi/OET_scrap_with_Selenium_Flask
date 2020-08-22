# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotVisibleException
import time , random
from threading import Thread
from os import sys
import pprint
import os
from os.path import join, dirname
from dotenv import load_dotenv
from twilio.rest import Client
import smtplib
import logging
from logging.handlers import RotatingFileHandler


def my_logging(log, f_name, msg):
    log.propagate = True
    fileh = RotatingFileHandler('static/logs/' + f_name + '.log', mode='a', maxBytes=log_file_size*1024, backupCount=2, encoding='utf-8', delay=0)
    # ('logs/' + f_name + '.log', 'a')
    fileh.setFormatter(formatter)
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)
    log.critical(msg)
    log.propagate = False


def find_error(browser):
    try:
        elem = browser.find_element_by_xpath("//[contains(text(),'System Error']")
        return "System Error"
    except:
        pass

    try:
        elem = browser.find_element_by_xpath("//[contains(text(),'already been taken by others']")
        return "already been taken by others"
    except:
        pass

    try:
        elem = browser.find_element_by_xpath("//[contains(text(),'This location is fully booked for this date']")
        return "This location is fully booked for this date. Please select a different location or date."
    except:
        pass

    return "ok"


class MyThread(Thread):
 
    def __init__(self, name, user):
        Thread.__init__(self)
        self.name = name 
        self.user = user
        self.user["country"] = self.user["country"].split("##")
        self.user["locations"] = self.user["locations"].split("##")
        self.user["dates"] = self.user["dates"].split("##")        
        self.log = logging.getLogger("a")  # root logger
 
    def run(self):
        global proxies_list, proxy_index   

        while proxy_status[self.name] == 1 or proxy_status[self.name] == 4:
            start_time = time.perf_counter()
            if os.environ.get('USE_PROXY') == "true":
                proxy = proxies_list[proxy_index]
                proxy_index += 1
                if proxy_index == len(proxies_list): proxy_index = 0
            # is_redirected = False  # if it is true, current page is testcenterselect.aspx.

            path = '.\\Lib\\chromedriver.exe'
            options = webdriver.ChromeOptions ( ) 
            options.add_argument('--log-level=0')

            my_logging(self.log, self.name, "USE_PROXY = " + os.environ.get('USE_PROXY'))
            my_logging(self.log, self.name, "FREE_PROXY = " + os.environ.get('FREE_PROXY'))
            
            if os.environ.get('USE_PROXY') == "true":
                options.add_argument('--proxy-server=%s' % proxy)
            browser = webdriver.Chrome (executable_path = path, options = options )
            browser.get("https://registration.myoet.com/login.jsp")
            action = ActionChains(browser)
            
            if os.environ.get('USE_PROXY') == "true":
                my_logging(self.log, self.name, proxies_list[proxy_index] + ' started.')

            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                return

            if fast_mode:
                pass
            else:
                time.sleep(5)
            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                return

            try:
                elem = browser.find_element_by_id("u")
                elem.send_keys(self.user["username"])

                if fast_mode:
                    pass
                else:
                    time.sleep(2) 

                elem = browser.find_element_by_id("p")
                elem.send_keys(self.user["password"])

                if fast_mode:
                    pass
                else:
                    time.sleep(2)

                ######## break ##############
                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
            except:
                # Page Loading Fail
                browser.close() 
                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Loading Failed') 

                if fast_mode:
                    pass
                else:              
                    time.sleep(30)
                continue
                
            try:
                elem = browser.find_element_by_id("s")
                elem.click()

                if fast_mode:
                    time.sleep(1)
                else:
                    time.sleep(5)

                ######## break ##############
                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                elem = browser.find_element_by_xpath("//div[@class='v-slot v-slot-button-0 v-slot-i-understand v-slot-primary']//span[@class='v-button-caption']").click() #[contains(text(),'I UNDERSTAND']
            except:
                # Incorrect Login
                proxy_status[self.name] = 3 # Incorrect Login
                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Incorrect Login') 
                browser.close()
                return

            while proxy_status[self.name] == 1 or proxy_status[self.name] == 4:
                action = ActionChains(browser)
                proxy_change = True
                try:                    
                    if self.user["defer"] == True:
                        
                        elems = browser.find_elements_by_xpath("//div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[3]/div/div/div[2]/div[1]/table/tbody/tr")    
                        for elem in elems:
                            if self.user["test_date"] == "0000-00-00" or elem.find_element_by_xpath("./td[4]/div").text.upper() == self.user["test_date"]:
                                
                                print("actin setting")
                                firstLevelMenu = elem.find_element_by_xpath("./td[1]/div/div/div[2]/span")
                                print("element setting")
                                action.move_to_element(firstLevelMenu).perform()
                                print("move to element")
                                
                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(2)

                                secondLevelMenu = browser.find_element_by_xpath("//div[2]/div[2]/div/div//span[contains(text(),'Defer')]")
                                action.move_to_element(secondLevelMenu).perform() 
                                secondLevelMenu.click()

                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(2)

                                # Confirm Button
                                browser.find_element_by_xpath("//div[2]/div[3]/div/div/div[3]/div/div/div/div[2]/div/div[3]/div/span/span").click()
                                
                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(2)
                                # Next Button
                                browser.find_element_by_xpath("//span[@class='v-button-caption'][contains(text(),'NEXT')]").click()

                                err_msg = find_error(browser)
                                if err_msg != "ok":
                                    raise Exception(err_msg)


                                ######## break ##############
                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                    return
                                
                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(2)                                

                                break
                        else:
                            raise Exception("")
                    else:
                        # Select Profession
                        elem = browser.find_element_by_xpath("//span[@class='v-menubar-menuitem-caption'][contains(text(),'Apply for the test')]").click()
                        
                        if fast_mode:
                            time.sleep(1)
                        else:
                            time.sleep(5)

                        err_msg = find_error(browser)
                        if err_msg != "ok":
                            raise Exception(err_msg)
                        
                        ######## break ##############
                        if proxy_status[self.name] == 0: 
                            browser.close()
                            my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                            return

                        select = Select(browser.find_element_by_xpath("//tr[@class='v-formlayout-row v-formlayout-firstrow']/td[@class='v-formlayout-contentcell']//select"))
                        select.select_by_visible_text(self.user["profession"])
                        my_logging(self.log, self.name, 'Profession: ' + self.user["profession"]) 
                        
                        if fast_mode:
                            time.sleep(1)
                        else:
                            time.sleep(2)
                    

                    while (proxy_status[self.name] == 1 or proxy_status[self.name] == 4) and time.perf_counter() - start_time < proxy_period * 60:
                        for country in self.user["country"]:
                            if time.perf_counter() - start_time >= proxy_period * 60: break 
                            print("country: ##" + country + "##")
                            try:
                                if self.user['defer'] == True:
                                    select = Select(browser.find_element_by_xpath("//div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div/div[2]/div[3]/table/tbody/tr/td[3]/div/select"))
                                else:
                                    select = Select(browser.find_element_by_xpath("//tr[@class='v-formlayout-row v-formlayout-lastrow']/td[@class='v-formlayout-contentcell']//select"))
                                
                                select.select_by_visible_text(country)
                                my_logging(self.log, self.name, 'Country: ' + country)
                                
                                if fast_mode:
                                    pass
                                else:
                                    time.sleep(2) 

                            except ElementNotVisibleException:
                                print("#################### Country Mismatch.")
                                my_logging(self.log, self.name, '############  Country Mismatch. ##########') 
                                my_logging(self.log, self.name, 'mismatched country name: ' + country) 
                                
                                if fast_mode:
                                    pass
                                else:
                                    time.sleep(2)

                                continue
                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                return
                            elem = browser.find_element_by_xpath("//span[@class='v-button-caption'][contains(text(),'NEXT')]").click()
                            
                            if fast_mode:
                                time.sleep(1)
                            else:
                                time.sleep(5)

                            err_msg = find_error(browser)
                            if err_msg != "ok":
                                raise Exception(err_msg)

                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                return

                            select = Select(browser.find_element_by_xpath("//div[@class='v-slot v-slot-time-select v-slot-booking-style v-slot-current']//select"))
                            for date_ in self.user["dates"]:
                                if time.perf_counter() - start_time >= proxy_period * 60: break 
                                print("date = " + date_)
                                try:
                                    select.select_by_visible_text(date_)
                                    my_logging(self.log, self.name, 'Date: ' + date_) 
                                    
                                    if fast_mode:
                                        pass
                                    else:
                                        time.sleep(2)

                                    ######## break ##############
                                    if proxy_status[self.name] == 0: 
                                        browser.close()
                                        my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                        return
                                except :#ElementNotVisibleException
                                    
                                    if fast_mode:
                                        pass
                                    else:
                                        time.sleep(2)

                                    continue
                                elem = browser.find_element_by_xpath("//span[@class='v-button-caption'][contains(text(),'NEXT')]").click()
                                
                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(3)

                                err_msg = find_error(browser)
                                if err_msg != "ok":
                                    raise Exception(err_msg)

                                ######## break ##############
                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                    return
                                
                                for location in self.user["locations"]:
                                    my_logging(self.log, self.name, 'Location: ' + location) 
                                    elems = browser.find_elements_by_xpath("//div[@class='v-slot v-slot-venue-select v-slot-booking-style v-slot-current']//tr[@class='v-formlayout-row v-formlayout-firstrow']//span[@class='v-radiobutton v-select-option']")
                                    for elem in elems:
                                        txt = elem.find_element_by_xpath("./label[2]/span").text.strip().lower()
                                        my_logging(self.log, self.name, "LLL : " + txt)
                                        if txt.find(location.strip().lower()) > -1:
                                            print("OK")
                                            elem.find_element_by_xpath("./label[1]").click()
                                            msg = os.environ.get('MESSAGE')

                                            if self.user["defer"] == True:
                                                if fast_mode:
                                                    time.sleep(1)
                                                else:
                                                    time.sleep(5)

                                                browser.find_element_by_xpath("//span[@class='v-button-caption'][contains(text(),'NEXT')]").click()
                                                
                                                if fast_mode:
                                                    time.sleep(1)
                                                else:
                                                    time.sleep(5)

                                                    err_msg = find_error(browser)
                                                    if err_msg != "ok":
                                                        raise Exception(err_msg)
                                                browser.find_element_by_xpath("//span[@class='v-button-caption'][contains(text(),'DEFER APPLICATION')]").click()                                            
                                                
                                                if fast_mode:
                                                    time.sleep(1)
                                                else:
                                                    time.sleep(5)

                                                err_msg = find_error(browser)
                                                if err_msg != "ok":
                                                    raise Exception(err_msg)

                                                try:
                                                    elem = browser.find_element_by_xpath("//div[1]/div/div[2]/div/div[1]/div/div[contains(text(), 'My Dashboard')]")
                                                    msg = "Alert for %NAME. %DATE %TIME at %LOCATION. Date booked successfully"
                                                except:
                                                    raise Exception("date_missed")

                                            


                                            sended = False
                                            msg = msg.replace("%NAME", self.name).replace("%DATE", date_).replace("%LOCATION", location)
                                            print(msg)
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                                    
                                            my_logging(self.log, self.name, "[msg] " + msg)    
                                            # #################### email ##############################
                                            try:
                                                smtpObj = smtplib.SMTP('smtp.gmail.com: 587')#('smtp-mail.outlook.com', 587)
                                            except Exception as e:
                                                print(e)
                                                my_logging(self.log, self.name, e)#'SMTP TSL connection failed.  trying SMTP SSL connection...\n' + e)
                                                try:
                                                    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                                except Exception as e:
                                                    print(e)
                                                    my_logging(self.log, self.name, 'SMTP SSL connection failed.  S M T P   F A I L E D\n' + e)
                                                    raise Exception('')
                                            
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            try:
                                                smtpObj.ehlo()
                                                smtpObj.starttls()
                                                smtpObj.login(from_email, email_pass)
                                                smtpObj.sendmail(from_email, self.user["email"], "Subject: Notification\n" + msg)
                                                smtpObj.quit()
                                                my_logging(self.log, self.name, 'email::  to:' + self.user["email"] + ' msg: ' + msg)
                                                sended = True
                                            except Exception as e:
                                                print(e)
                                                my_logging(self.log, self.name, 'SMTP Login failed.\n' + e)
                                                    

                                            # # ################### CALL ################################
                                            print(twilio_phone_number)
                                            print("---------------------------------------------")
                                            print("from_=" + twilio_phone_number + ", " + " to=" + self.user["phone"] + ", " + "body=" + msg)
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            try:
                                                response_call = client.calls.create(twiml='<Response><Say>' + msg + '</Say></Response>', from_=twilio_phone_number, to=self.user["phone"] )
                                                if response_call.sid :                                                
                                                    my_logging(self.log, self.name, 'CALL::  to:' + self.user["phone"] + ' msg: ' + msg)
                                                    sended = True
                                            except  Exception as e:
                                                print(e)
                                                my_logging(self.log, self.name, e)
                                                
                                            print("----------------------------------------------")

                                            # # ################### SMS ################################
                                            print(twilio_phone_number)
                                            print("---------------------------------------------")
                                            print("from_=" + twilio_phone_number + ", " + " to=" + self.user["phone"] + ", " + "body=" + msg)
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.name, proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            try:
                                                response_msg = client.messages.create(body=msg, from_=twilio_phone_number, to=self.user["phone"] )
                                                if response_msg.sid :
                                                    my_logging(self.log, self.name, 'SMS::  to:' + self.user["phone"] + ' msg: ' + msg)
                                                    sended = True
                                            except  Exception as e:
                                                print(e)
                                                my_logging(self.log, self.name, e)
                                                        
                                            print("----------------------------------------------")
                                                    

                                            if sended:
                                                proxy_status[self.name] = 2
                                                my_logging(self.log, self.name, " Message sent.") 
                                                browser.close()
                                                return
                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(5)
                                
                                # if self.user["defer"] == True:
                                #     browser.find_element_by_xpath("//span[contains(text(), 'CANCEL')]").click() 
                                #     time.sleep(1)
                                #     raise Exception("defer_cancel")


                                elem = browser.find_element_by_xpath("//div[@class='v-slot v-slot-buttons']//span[@class='v-button-caption'][contains(text(), 'PREVIOUS')]").click()
                                
                                if fast_mode:
                                    time.sleep(1)
                                else:
                                    time.sleep(5)
                            
                            # if self.user["defer"] == True:
                            #     browser.find_element_by_xpath("//span[contains(text(), 'CANCEL')]").click() 
                            #     time.sleep(1)
                            #     raise Exception("defer_cancel")

                            if fast_mode:
                                time.sleep(1)
                            else:
                                time.sleep(5)

                            elem = browser.find_element_by_xpath("//div[@class='v-slot v-slot-buttons']//span[@class='v-button-caption'][contains(text(), 'PREVIOUS')]").click()
                            
                            if fast_mode:
                                time.sleep(1)
                            else:
                                time.sleep(5)
                        
                        if self.user["defer"] == True:
                            # browser.find_element_by_xpath("//span[contains(text(), 'CANCEL')]").click() 
                            # time.sleep(2)
                            # browser.find_element_by_xpath("//span[contains(text(), 'Yes')]").click()
                            # time.sleep(10)
                            raise Exception("defer_cancel")

                except Exception as e: 
                    my_logging(self.log, self.name, " Exception : " + e.args[0])
                    if e.args[0] == "date_missed":                    
                        proxy_status[self.name] = 4
                        my_logging(self.log, self.name, " Date Missed.")
                    if e.args[0] == "defer_cancel":
                        proxy_change = False
                        
                finally: 
                    if self.user["defer"] == True:
                        try:
                            browser.find_element_by_xpath("//span[contains(text(), 'CANCEL')]").click() 
                            time.sleep(2)
                            browser.find_element_by_xpath("//span[contains(text(), 'Yes')]").click()
                            time.sleep(10)
                        except:
                            pass
                    else:
                        try:
                            firstLevelMenu = browser.find_element_by_xpath("//body/div[1]/div/div[2]/div/div[1]/div/div[2]/span[1]/span[2]")
                            action.move_to_element(firstLevelMenu).perform()
                                
                            if fast_mode:
                                time.sleep(1)
                            else:
                                time.sleep(2)

                            secondLevelMenu = browser.find_element_by_xpath("//body/div[2]/div[2]/div/div/span[2]/span")
                            action.move_to_element(secondLevelMenu).perform() 
                            secondLevelMenu.click()
                            try:
                                elem = browser.find_element_by_xpath("//body/div[2]/div[3]/div/div/div[3]/div/div/div/div[2]/div/div[1]/div/span/span")
                                elem.click()
                            except:
                                pass
                        except:
                            pass
                        browser.save_screenshot("image_logs/" + self.user["name"] + time.strftime("-%Y-%m-%d-%H-%M-%S") +".png") 
                        browser.close()
                        my_logging(self.log, self.name, proxies_list[proxy_index] + ': Failed.   Other Proxy will is started.') 
                        
                        if fast_mode:
                            time.sleep(1)
                        else:
                            time.sleep(30)
                        break
                    
                        

    



            


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Get Twilio Account Info
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

from_email = os.environ.get('EMAIL_ADDRESS')
email_pass = os.environ.get('EMAIL_PASSWORD')
if os.environ.get('FAST_MODE') == "true":
    fast_mode = True
else:
    fast_mode = False

log_file_size = float(os.environ.get('LOG_FILE_SIZE'))
proxy_period = float(os.environ.get('PROXY_PERIOD'))

proxies_list = []
proxy_index = 0
proxy_status = {}

formatter = logging.Formatter('%(asctime)s    %(message)s')