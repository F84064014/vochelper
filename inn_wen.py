import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Options
options = Options()
# options.add_argument("--headless")  # 可以選擇開啟無頭模式(似乎是不要開UI)
# options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
## options.add_argument("--no-sandbox") # 建議不要用 https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md#headless

download_dir = r"C:\Users\R123828878\Downloads\temp"
os.makedirs(download_dir, exist_ok=True)

prefs = {
    # "plugins.always_open_pdf_externally": False,
    "download.default_directory": download_dir,
    "directory_upgrade": True,  # totally dont know wtf is this
    "download.prompt_for_download": False, # 開起會有file browser
    # "safebrowsing.enabled": True,
}

options.add_experimental_option("prefs", prefs)
from selenium.webdriver.common.action_chains import ActionChains

# edge_pth = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Microsoft Edge.lnk"
# print(os.path.isfile(edge_pth))
#driver = webdriver.Edge(edge_pth)

service = Service(service_args=[""]) #--verbose"])
driver = webdriver.Edge(service=service, options=options)
# driver.maximize_window()

# Open page
driver.get("https://service.vac.gov.tw/vac/index.asp")
WebDriverWait(driver, 100).until(
    EC.presence_of_all_elements_located((By.XPATH, "//a[@href='main.asp']"))
)
driver.find_element(By.XPATH, "//a[@href='main.asp']").click()

time.sleep(0.5)
WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "frame"))
)

## Switch to new Frame
iframe = driver.find_element(By.TAG_NAME, 'frame')
driver.switch_to.frame(iframe)
print("Switch to Frame")

# Login (Auto Login, not need to enter password)
driver.find_element(By.XPATH, "//a[@href='mainfirstAD.asp']").click()
print("Login")
time.sleep(0.5)

# 文檔管理
s = driver.page_source # this line is somehow necessary
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "frame"))
    )
except:
    try:
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "frame"))
        )
    except:
        print("Timeout loading left bar")
        exit()

WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.XPATH, "//frame[@title='leftbar']"))
)

# left_bar = driver.find_elements(By.TAG_NAME, "frame")[1]
left_bar = driver.find_element(By.XPATH, "//frame[@title='leftbar']")
driver.switch_to.frame(left_bar)
# print(left_bar.get_attribute('title'), "Loaded")

# WebDriverWait(driver, 10).until(
#     EC.presence_of_all_elements_located((By.XPATH, "//a[@href='/LinkToODMS.asp')]"))
# )

element = driver.find_element(By.XPATH, "//a[contains(text(), '文檔資訊入口網')]")
# element = driver.find_element(By.XPATH, "//*[contains(text(), '文檔資訊入口')]")
# element = driver.find_element(By.XPATH, "//a[@href='/LinkToODMS.asp')]")
# element = driver.find_element(By.XPATH, "//*[@id='itemTextLink2']") # 文黨資訊入口
# print(element.get_attribute('text'), "Loaded")
print("文檔資訊入口網 Loaded")
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
element.click()

# Close download tab
time.sleep(1.5)
temp = None
for window in driver.window_handles:
    driver.switch_to.window(window)
    if "國軍退除役官兵輔導委員會文檔資訊入口網" not in driver.title:
        driver.close()
    else:
        # driver.switch_to.window(window)
        temp = window
        print("found 國軍退除役官兵輔導委員會文檔資訊入口網 V1.0")
        break
driver.switch_to.window(temp)

# time.sleep(0.5)
# print(driver.window_handles[0])
# time.sleep(0.5)
# driver.switch_to.window(driver.window_handles[0])
# driver.switch_to.window(window)

# 文黨資訊入口網左側選單的frame
# frame = filter(lambda e: e.get_attribute('title')=='檔管狀態樹', driver.find_elements(By.TAG_NAME, "frame"))
# frame = list(frame)[0]
frame = driver.find_element(By.XPATH, "//*[@title='檔管狀態樹']")
driver.switch_to.frame(frame)

# 點選公文管理系統
element = driver.find_elements(By.XPATH, "//*[contains(text(), '公文管理')]")[0]
element.click()

# 記錄下兩個主要的frame
#   左排: 功能組織數
#   中間: 主頁面資料
s = driver.page_source # same somehow needed
def build_frames(title):
    # _frame = filter(lambda e: e.get_attribute('title') == title, driver.find_elements(By.TAG_NAME, "frame"))
    # _frame = list(_frame)[0]
    _frame = driver.find_element(By.XPATH, ".//frame[@title='{}']".format(title))
    return _frame

paper_manage_system_titles = ["主頁面資料", "功能組織樹"]
paper_manage_system_frames = {title: build_frames(title) for title in paper_manage_system_titles}

# 尋找待簽收並點選
driver.switch_to.frame(paper_manage_system_frames["功能組織樹"])
element = driver.find_elements(By.XPATH, "//*[contains(text(), '待簽收')]")[0]
# element = driver.find_elements(By.XPATH, "//*[contains(text(), '承辦待處理')]")[0]
element.click()
print("load 代簽收 | 承辦代處理")

# 開始印文!
driver.switch_to.default_content()
driver.switch_to.frame(paper_manage_system_frames["主頁面資料"])
print("load 主頁面資料")
rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'layer')]")

max_num_data = 10
num_data = 0

for row in rows:

    if num_data >= max_num_data:
        break

    try:
        agent_elements = {
            "ComesOrg"      : row.find_element(By.XPATH, ".//*[contains(@id, 'LblComesOrg')]"),
            "LblComesWord"  : row.find_element(By.XPATH, ".//*[contains(@id, 'LblComesWord')]"),
            "LblComesNum"   : row.find_element(By.XPATH, ".//*[contains(@id, 'LblComesNum')]"),
            "when_how"       : row.find_element(By.XPATH, ".//a[contains(@id, 'LnkDocNo')]"), # 文號
        }
    except:
        print(row.text)
        exit()

    if agent_elements["when_how"].text.startswith("*"):
        print(f"skip doc with id starts with *: {agent_elements["when_how"].text}")
        continue

    if not (agent_elements["ComesOrg"].text.startswith("國防部")):
        print(f"skip doc which is not from 國防部: {agent_elements["when_how"].text}")
        continue

    num_data += 1

    hover_element = row.find_element(By.XPATH, ".//*[contains(text(), '選擇檔案')]")
    hover = ActionChains(driver).move_to_element(hover_element)

    pdf_elements = row.find_elements(By.XPATH, ".//*[contains(text(), '.pdf')]")
    for pdf_element in pdf_elements:

        filename = agent_elements["when_how"].text + pdf_element.get_attribute('text')
        print(os.path.join(download_dir, filename))
        if not os.path.isfile(os.path.join(download_dir, filename)):
            hover.perform()
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(pdf_element))
            except:
                hover.perform()
                time.sleep(1)

            pdf_element.click()
        else:
            print(f"{filename} already exist")

    try:
        row.find_element(By.XPATH, ".//input[@type='checkbox']").click()
        print("checkbox clicked")
    except:
        print(f"fail to click checkbox {agent_elements["LblComesNum"].text}")

    time.sleep(0.1)

time.sleep(2)
from pdf_handle import handle
handle(download_dir)

driver.get(os.path.join(download_dir, "final.pdf"))

for window in driver.window_handles:
    driver.switch_to.window(window)
    if driver.title.endswith('.pdf'):
        driver.close()
        driver.switch_to.frame(window)
        break

driver.execute_script("window.print()")
input("Done press any to terminate")