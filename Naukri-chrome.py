import re
import requests
import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import datetime as dt


# In[2]:


##User details is entered below
firstname='Rahul'                        #Add your LastName
lastname='KR'                         #Add your FirstName
jobs = 1                         #Number of naukri pages you want the code to go through
job_links=[]                          #Initialized list to store links
maxcount=100                         #Max daily apply quota for Naukri
keywords=[ "python","mulesoft"]                    #Add you list of role you want to apply comma seperated Ex: for Python developer: python
#objective and additional details, Must be under 100 characters
objective_or_additionaldetails = "Excited to explore new opportunities"
location = 'bangalore'                       #Add your location/city name for within India or remote
curr_loc = "bangalore"    ###Enter your current location in the same format
curr_state = "karnataka"  ##Enter your current state
###Salary format: "0-3 Lakhs", "3-6 Lakhs", "6-10 Lakhs", "10-15 Lakhs", "15-25 Lakhs", "25-50 Lakhs", "50-75 Lakhs", "75-100 Lakhs", "1-5 Cr", "5+ Cr"
sal = "10to15"     ##Copy-paste from the above
exp_years = "2"  ## Type your experience in years
exp_months = "5"  ## Type your experience in years
notice_per = "3 Month" ##Enter your notice period, enter Immediate joining, if no notice period
gen = "male"                ##male or female
yournaukriemail = 'krrahulraj007@gmail.com'   #naukri usename
yournaukripass = '<enter_your_pass>'      #naukri password
headless = False


# In[3]:


#Checks for the user inputs
if(len(objective_or_additionaldetails)>=100):
    print("objective and additional details, Must be under 100 characters.")
    exit()


# In[4]:


applied =0                          #Count of jobs applied sucessfully
failed = 0                          #Count of Jobs failed
applied_list={
    'passed':[],
    'failed':[]
}        
gender = {"male": '//*[@id="gender_1"]', "female":'//*[@id="gender_2"]'}


# In[5]:


##Fill naukri job specific forms while applying
def final_form(driver,wait):
    # to enter first name and last name
    wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@id='CUSTOM-FIRSTNAME"))).send_keys(firstname)
    wait.until(EC.visibility_of_element_located((By.XPATH,"//input[@id='CUSTOM-LASTNAME"))).send_keys(lastname)
    #full name entering
    wait.until(EC.visibility_of_element_located((By.ID,'fid8'))).send_keys(firstname+" " +lastname)
    print("after the full name")
    #gender selection
    if(wait.until(EC.visibility_of_element_located((By.XPATH,gender[gen])))):
        Select(wait.until(EC.visibility_of_element_located((By.XPATH,gender[gen]))))
    # Current location
    if(wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="Sug_city"]')))):
        dropdown = Select(wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="Sug_city"]'))))
        # Loop through each option and print its text
        for option in dropdown.options:
            ###driver.refresh()
            if(curr_loc in option.text):
                dropdown.select_by_visible_text(option.text)
                break
    # Experience years selection
    if(wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="cstmExpY"]')))):
        dropdown = Select(wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="cstmExpY"]'))))
        # Loop through each option and print its text
        for option in dropdown.options:
            ###driver.refresh()
            if(exp_years == option.text):
                dropdown.select_by_visible_text(option.text)
                break
    # Experience Months selection
    if(wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="cstmExpM"]')))):
        dropdown = Select(wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="cstmExpM"]'))))
        # Loop through each option and print its text
        for option in dropdown.options:
            ###driver.refresh()
            if(exp_months == option.text):
                dropdown.select_by_visible_text(option.text)
                break


# In[6]:


##Initializing the chrome driver and logging into the naukri application
try:
    chrome_options = Options()
    chrome_driver = ChromeDriverManager()
    # chrome_options.add_argument('--ignore-certificate-errors')
    if(headless == True):
        chrome_options.add_argument("--headless")  # For Chrome versions 109 and above
        chrome_options.add_argument('--disable-gpu')
        # For older versions (up to 108): options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_driver.install(), options=chrome_options)
    else:
        driver = webdriver.Chrome(chrome_driver.install())
    ##driver = webdriver.Chrome(chrome_driver.install(), options=chrome_options)
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])
    wait = WebDriverWait(driver, 10)
    driver.get('https://login.naukri.com/')
    wait.until(EC.visibility_of_element_located((By.ID, 'usernameField'))).send_keys(yournaukriemail)
    passwd=driver.find_element(By.ID, 'passwordField')
    passwd.send_keys(yournaukripass)
    passwd.send_keys(Keys.ENTER)
except Exception as e:
    print(f'Webdriver exception: {e}')
    raise e
    exit()


# In[7]:


#Filter by the location if mentioned and parse the html using bs4
job_links = []
time.sleep(10)
for k in keywords:
    for i in range(jobs):
        if(location and sal and exp_years):
            url = "https://www.naukri.com/"+k.lower().replace(' ','-')+"-jobs-in-"+location.lower().replace(' ','-')+"-"+str(i+1)+"?ctcFilter="+sal+"&experience="+exp_years
        elif(sal and location):
            url = "https://www.naukri.com/"+k.lower().replace(' ','-')+"-jobs-in-"+location.lower().replace(' ','-')+"-"+str(i+1)+"?ctcFilter="+sal
        elif location=='':
            url = "https://www.naukri.com/"+k.lower().replace(' ','-')+"-"+str(i+1)
        response = requests.get(url)
        status_code = response.status_code
        if status_code == 200:
            print(f"The website {url} is up and running.")
            driver.get(url)
            # Wait for the sorting dropdown to be visible
            sorting_dropdown = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "filter-sort")))
            sorting_dropdown.click()

            # Click on the "Most recent" option (assuming the option's text is "Most recent")
            date_option = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@data-id='filter-sort-f']")))
            date_option.click()
        else:
            print(f"Matching jobs not found or {url} is incorrect, Please try again!")
        try:
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            urls = soup.find_all(href=re.compile(r'^https://www\.naukri\.com/job-listings'))
            job_links.extend(url['href'] for url in urls)
        except Exception as e:
            print(f"Exception{e} occurred, Please run again!")

##Iterate over each job and try to apply for the job
for i in job_links:
    try:
        time.sleep(3)
        driver.get(i)
        job_title = str(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h1[@class='styles_jd-header-title__rZwM1']")))).strip().lower()
        job_description = str(WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "styles_JDC__dang-inner-html__h0K4t"))
    )).strip().lower()

        match = True ## Change it to true, if you want to apply for related jobs to the keyword
        if(match != True):
            for kw in keywords:
                if(kw.strip().lower() in job_title or kw.strip().lower() in job_description):
                    match = True
        if(match):
            if applied <=maxcount:
                try:
                    # driver.find_element_by_class_name('apply-button').click()
                    wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'apply-button'))).click()
                    applied +=1
                    applied_list['passed'].append(i)
                    print('Applied for ',i, " Count", applied)
                except Exception as e:
                    failed += 1
                    applied_list['failed'].append(i)
                    print(e, "Failed ", failed)
                    pass
            else:
                if driver.find_element_by_xpath("//*[text()='Your daily quota has been expired.']"):
                    print('MAX Limit reached closing browser')
        #             driver.close()
                    break
                failed += 1
                applied_list['failed'].append(i)
                print(e, "Failed ", failed)
        else:
            print(f"Skipping job url: {i}")
    except Exception as e:
        print(f"Exception {e} occurred!")

def apply_form():
        # Wait until the element is visible
    try:  
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'qusSubmit'))
        )
        # Click on the element
        element.click()
    except:
        pass


##Complte the job apply process and update the results to the csv
print('Completed applying closing browser saving in applied jobs csv')
try:
    driver.close()
except:
    pass
csv_file = f"./data/naukriapplied-{dt.date.today()}.csv"
final_dict= dict ([(k, pd.Series(v)) for k,v in applied_list.items()])
df = pd.DataFrame.from_dict(final_dict)
df.to_csv(csv_file, index = False)


