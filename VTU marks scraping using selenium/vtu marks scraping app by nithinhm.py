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


skipped_usns = []
data_dict = {}

options = Options()
options.unhandled_prompt_behavior = 'ignore'

print('Example USN: 1AM22CS010\n')
while True:
    try:
        batch = int(input('Enter batch year as in USN (Ex: 22 or 21 or 19): ').strip())
    except:
        print('Error! Enter a valid 2-digit number.\n')
    else:
        batch = str(batch)
        if len(batch) != 2:
            print('Error! Enter a valid 2-digit number.\n')
        else:
            break

while True:
    branch = input('\nEnter branch as in USN (Ex: CS or MT or CI): ').upper().strip()
    if len(branch) != 2:
        print('Error! Enter a valid 2-character branch.\n')
    else:
        break

while True:
    try:
        first_number = int(input("\nEnter the first number of this branch's USN (Ex: 1 or 25 or 140): ").strip())
    except:
        print('Error! Enter a valid 3-digit number.\n')
    else:
        if first_number > 999:
            print('Error! Enter a valid 3-digit number.\n')
        else:
            break

while True:
    try:
        final_number = int(input("\nEnter the last number of this branch's USN (Ex: 5 or 23 or 145): ").strip())
    except:
        print('Error! Enter a valid 3-digit number.\n')
    else:
        if final_number > 999:
            print('Error! Enter a valid 3-digit number.\n')
        else:
            break

while True:
    try:
        retry_delay = int(input('\nIf there are network issues, how many seconds do you wish to wait before retrying again?: ').strip())
    except:
        print('Error! Enter a valid number.\n')
    else:
        break

while True:
    try:
        max_retries = int(input('\nHow many times do you wish to retry before ending the session?: ').strip())
    except:
        print('Error! Enter a valid number.\n')
    else:
        break

url = input('\nEnter the URL of the results login page. (starts with https://): ').strip()

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

                print(f'\nError for {usn} because {alert_text}')

                if alert_text == 'University Seat Number is not available or Invalid..!':
                    print('Let\'s move to the next USN.\n')
                    k += 1
                    skipped_usns.append(usn)
                    alert.accept()
                else:
                    print('Let\'s try again.\n')
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

            print(f'Error for {usn} because {alert_text}.\n')

            if alert_text == 'University Seat Number is not available or Invalid..!':
                print('Let\'s move to the next USN.\n')
                k += 1
                skipped_usns.append(usn)
                alert.accept()
            else:
                print('Let\'s try again.\n')
                alert.accept()

        except NoSuchWindowException:
            print('Error! Window closed prematurely. Data collected so far will be saved.\n')
            window_is_present = False
            break

        except:
            soup2 = BeautifulSoup(driver.page_source, 'lxml')
            occur = soup2.find_all('b', string='University Seat Number')
            if len(occur) > 0:
                print(f'There was an error collecting data for {usn}. Let\'s try again.\n')
                driver.back()
            else:
                print(f'Error! Retrying after {retry_delay} seconds. Retry {this_retry+1} of {max_retries}\n')
                this_retry += 1
                time.sleep(retry_delay)
                driver.refresh()

    else:
        try:
            print(f'Maximum number of retries reached ({max_retries}). Data collected so far will be saved.\n')
        except NoSuchWindowException:
            print('Error! Window closed prematurely. Data collected so far will be saved.\n')
            window_is_present = False
        finally:
            break

driver.quit()

if len(skipped_usns) > 0:
    print(f'These USNs were skipped {skipped_usns}.\n')
else:
    print('No USNs were skipped.\n')

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

print(f'Data collected for USNs {branch} {first_USN} to {last_USN} and saved in an excel file.\n')

input("Press any button to close this app.")