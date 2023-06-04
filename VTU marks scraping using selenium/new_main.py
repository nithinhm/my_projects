from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import *
import pandas as pd
from bs4 import BeautifulSoup
import time

batch = '22'            # enter batch year as in USN (4th and 5th character)
branch = 'AI'           # enter branch as in USN (6th and 7th character)
first_number = 1        # enter the first number of this branch's USN (do not include padded zeros)
final_number = 10      # enter the last number of this branch's USN (do not include padded zeros)

url = 'https://results.vtu.ac.in/JFEcbcs23/index.php'

skipped_usns = []
data_dict = {}
max_retries = 5
retry_delay = 10

options = Options()
options.unhandled_prompt_behavior = 'ignore'

service = ChromeService(executable_path='/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

driver.get(url)

k = first_number - 1

window_is_present = True

while k < final_number and window_is_present:
    
    k += 1
    this_retry = 0
    while this_retry < max_retries:
        try:
            usn = f'1AM{batch}{branch}{k:03d}'

            usn_bar = driver.find_element(By.NAME, 'lns')
            usn_bar.send_keys(usn)

            captcha_bar = driver.find_element(By.XPATH, '//*[@id="raj"]/div[2]/div[1]/label')
            captcha_bar.click()

            try:
                WebDriverWait(driver, 300).until_not(lambda d: d.find_element(By.NAME, 'lns'))

            except UnexpectedAlertPresentException:
                alert = WebDriverWait(driver, 1).until(EC.alert_is_present())
                alert_text = alert.text

                print(f'Error for {usn} because {alert_text}')

                if alert_text == 'University Seat Number is not available or Invalid..!':
                    k += 1
                    skipped_usns.append(usn)
                    alert.accept()
                else:
                    alert.accept()
                
                continue

            student_name = driver.find_element(By.XPATH,'//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[2]/td[2]').text.split(':')[1].strip()
            student_usn = driver.find_element(By.XPATH,'//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]').text.split(':')[1].strip()

            assert student_usn == usn, 'entered usn and obtained usn don\'t match'

            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            marks_data = soup.find('div', class_='divTableBody')

            data_dict[f'{student_usn}+{student_name}'] = marks_data

            print(f'Data successsfully collected for {usn}')

            driver.back()

            break

        except UnexpectedAlertPresentException:
            alert = WebDriverWait(driver, 1).until(EC.alert_is_present())
            alert_text = alert.text

            print(f'Error for {usn} because {alert_text}')

            if alert_text == 'University Seat Number is not available or Invalid..!':
                k += 1
                skipped_usns.append(usn)
                alert.accept()
            else:
                alert.accept()

        except NoSuchWindowException:
            print('Window closed prematurely. Data collected so far will be saved.')
            window_is_present = False
            break

        except:
            soup2 = BeautifulSoup(driver.page_source, 'lxml')
            occur = soup2.find_all('b', string='University Seat Number')
            if len(occur) > 0:
                print(f'There was an error collecting data for {usn}. Let\'s try again.')
                driver.back()
            else:
                print(f'Encountered an error. Retrying after {retry_delay} seconds. Retry {this_retry+1}/{max_retries}')
                this_retry += 1
                time.sleep(retry_delay)
                driver.refresh()

    else:
        try:
            print(f'Maximum number of retries reached ({max_retries}). Data collected so far will be saved.')
            break
        except NoSuchWindowException:
            print('Window closed prematurely. Data collected so far will be saved.')
            window_is_present = False
            break

driver.quit()

if len(skipped_usns) > 0:
    print(f'These USNs were skipped {skipped_usns}')
else:
    print('No USNs were skipped')

list_of_student_dfs = []

for id, marks_data in data_dict.items():

    this_usn, this_name = tuple(id.split('+'))
    rows = marks_data.find_all('div', class_='divTableRow')

    data = []
    for row in rows:
        cells = row.find_all('div', class_='divTableCell')
        data.append([cell.text.strip() for cell in cells])
    
    df_temp = pd.DataFrame(data[1:], columns=data[0])

    subjects = [f'{name} ({code})' for name, code in zip(df_temp['Subject Name'], df_temp['Subject Code'])]
    headers = df_temp.columns[2:-1]

    ready_columns = [(name, header) for name in subjects for header in headers]

    student_df = pd.DataFrame([this_usn, this_name] + list(df_temp.iloc[:,2:-1].to_numpy().flatten()), index= [('USN',''), ('Student Name','')] + ready_columns).T
    student_df.columns = pd.MultiIndex.from_tuples(student_df.columns, names=['', ''])

    list_of_student_dfs.append(student_df)

final_df = pd.concat(list_of_student_dfs).reset_index(drop=True)

cols = list(final_df.columns)[2:]
cols.sort(key = lambda x: x[0].split('(')[1][5:-1])
final_df = final_df[[('USN',''), ('Student Name','')] + cols]

final_df.index += 1

df2 = final_df.apply(pd.to_numeric, errors='ignore')

collected_usns = list(df2['USN'])

first_USN, last_USN = collected_usns[0], collected_usns[-1]

df2.to_excel(f'20{batch} {branch} {first_USN} to {last_USN} VTU results.xlsx')

print(f'Data collected for USNs {branch} {first_USN} to {last_USN} and saved in an excel file')