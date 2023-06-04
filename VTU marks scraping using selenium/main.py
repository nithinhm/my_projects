from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
import pandas as pd
import numpy as np

options = Options()
options.unhandled_prompt_behavior = 'ignore'

batch = '22'  # enter batch year as in USN (4th and 5th character)
branch = 'CS'  # enter branch as in USN (6th and 7th character)
final_number = 3  # enter the last number of this branch's last student as in USN (do not include padded zeros)

df = pd.DataFrame()

driver = webdriver.Chrome('chromedriver.exe', options=options)

url = 'https://results.vtu.ac.in/JJEcbcs23/index.php'

driver.get(url)

skipped_usns = []

k = 1

while k <= final_number:
    usn = '1AM' + batch + branch + f'{k}'.zfill(3)

    usn_bar = driver.find_element(By.NAME, 'lns')
    usn_bar.send_keys(usn)

    captcha_bar = driver.find_element(By.XPATH, '//*[@id="raj"]/div[2]/div[1]/label')
    captcha_bar.click()

    try:
        WebDriverWait(driver, 100).until_not(lambda d: d.find_element(By.NAME, 'lns'))

    except:
        alert = WebDriverWait(driver, 1).until(expected_conditions.alert_is_present())
        print(f'Error for {usn} because {alert.text}')

        if alert.text == 'University Seat Number is not available or Invalid..!':
            k += 1
            skipped_usns.append(usn)
            alert.accept()
            continue
        else:
            alert.accept()
            continue

    student_name = driver.find_element(By.XPATH,
                                       '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[2]/td[2]').text.split(
        ':')[1].strip()
    student_usn = driver.find_element(By.XPATH,
                                      '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]').text.split(
        ':')[1].strip()

    assert student_usn == usn, 'entered usn and obtained usn don\'t match'

    marks_data = driver.find_element(By.XPATH,
                                     '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div[2]')

    row_tags = marks_data.find_elements(By.CSS_SELECTOR, '.divTableRow')

    total_rows = len(row_tags)

    total_columns = len(row_tags[0].find_elements(By.CSS_SELECTOR, '.divTableCell'))

    data_array = np.empty((total_rows, total_columns), dtype=object)

    for i in range(total_rows):
        data_array[i] = [x.text for x in row_tags[i].find_elements(By.CSS_SELECTOR, '.divTableCell')]

    data_array = data_array[:, :-1]

    if k == 1:
        header_names = data_array[0][2:]
        subject_names = data_array[:, 1][1:]

        list_of_tuples = []

        for i in subject_names:
            for j in header_names:
                list_of_tuples.append((i, j))

    df[student_usn] = np.concatenate((np.array([student_name]), data_array[1:, 2:].flatten()))

    print(f'Data successsfully collected for {usn}')

    driver.back()

    k += 1

driver.quit()

print(f'These usns were skipped {skipped_usns}')

df2 = df.T.reset_index()
df2.columns = [('USN', ''), ('Student Name', '')] + list_of_tuples
df2.columns = pd.MultiIndex.from_tuples(df2.columns, names=['', ''])
df2.index += 1

df2 = df2.apply(pd.to_numeric, errors='ignore')

df2.to_excel(f'20{batch} {branch} VTU results.xlsx')
