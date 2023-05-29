from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import numpy as np


batch = '21'        # enter batch year as in USN (4th and 5th character)
branch = 'ME'       # enter branch as in USN (6th and 7th character)
final_number = 11   # enter the last number of this branch's last student as in USN (do not include padded zeros)

df = pd.DataFrame()

driver = webdriver.Chrome('chromedriver.exe')

url = 'https://results.vtu.ac.in/JFEcbcs23/index.php'

driver.get(url)

k = 1

while k <= final_number:
    usn = '1AM' + batch + branch + f'{k}'.zfill(3)

    usn_bar = driver.find_element_by_name('lns')
    usn_bar.send_keys(usn)

    captcha_bar = driver.find_element_by_xpath('//*[@id="raj"]/div[2]/div[1]/label')
    captcha_bar.click()

    try:
        WebDriverWait(driver, timeout=100).until(lambda d: d.find_element_by_xpath(
            '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[3]/div[3]/table/tbody/tr[2]/td/b[2]'))
    except:
        alert = WebDriverWait(driver, timeout=5).until(expected_conditions.alert_is_present())

        if alert.text == 'Invalid captcha code !!!':
            alert.accept()
            continue
        elif alert.text == 'University Seat Number is not available or Invalid..!':
            k += 1
            alert.accept()
            continue

    student_name = driver.find_element_by_xpath(
        '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[2]/td[2]').text.split(':')[
        1].strip()
    student_usn = driver.find_element_by_xpath(
        '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]').text.split(':')[
        1].strip()

    assert student_usn == usn, 'entered usn and obtained usn don\'t match'

    marks_data = driver.find_element_by_xpath(
        '//*[@id="dataPrint"]/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div[2]')

    data_array = np.zeros(shape=(9, 7), dtype=object)

    row_tags = marks_data.find_elements_by_css_selector('.divTableRow')

    for i in range(len(row_tags)):
        data_array[i] = [x.text for x in row_tags[i].find_elements_by_css_selector('.divTableCell')]

    data_array = data_array[:, :-1]

    if k == 1:
        header_names = data_array[0][2:]
        subject_names = data_array[:, 1][1:]

        list_of_tuples = []

        for i in subject_names:
            for j in header_names:
                list_of_tuples.append((i, j))

    df[student_usn] = np.concatenate((np.array([student_name]), data_array[1:, 2:].flatten()))

    driver.back()

    k += 1

driver.quit()

df2 = df.T.reset_index()
df2.columns = [('USN',''),('Student Name','')] + list_of_tuples
df2.columns = pd.MultiIndex.from_tuples(df2.columns, names=['',''])
df2.index+=1

df2.to_excel(f'20{batch} VTU results.xlsx', sheet_name=f'{branch}')