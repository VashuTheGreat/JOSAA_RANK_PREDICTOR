import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
# driver setup
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

def select_and_wait(element_id, text):
    # Element ke ready hone ka wait karo
    el = wait.until(EC.presence_of_element_located((By.ID, element_id)))
    print(f"Element enabled: {el.is_enabled()}, displayed: {el.is_displayed()}")
    time.sleep(1) # Extra buffer for ASP.NET
    
    # Set value and trigger change event
    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", el, text)
    
    # CRITICAL: Jab tak page refresh (loading) khatam na ho jaye wait karo
    time.sleep(3) 

try:
    driver.get("https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx")
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    wait.until(lambda driver: driver.execute_script("return typeof $ !== 'undefined'"))
    
    print("Selecting Year...")
    select_and_wait("ctl00_ContentPlaceHolder1_ddlYear", "2024")
    
    print("Selecting Round...")
    select_and_wait("ctl00_ContentPlaceHolder1_ddlRoundNo", "2")
    
    print("Selecting Institute Type...")
    select_and_wait("ctl00_ContentPlaceHolder1_ddlInstType", "ALL")
    
    # Baki filters (Institute, Branch, etc.) JoSAA par automatically 'ALL' ho jate hain 
    # agar tum seedha Submit daba do.
    
    print("Clicking Submit...")
    submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnSubmit")))
    submit_btn.click()
    
    # Wait for the table to appear
    print("Waiting for data table...")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-responsive")))
    time.sleep(2)
    
    # Data nikalna
    df = pd.read_html(driver.page_source)[0]
    df.to_csv("josaa_2024_data.csv", index=False)
    print("Mubarak ho! CSV ban gayi.")

except Exception as e:
    print(f"Abhi bhi error hai: {e}")
finally:
    driver.quit()