# 操作 browser 的 API
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException
# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait
# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC
# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By
# 強制等待 (執行期間休息一下)
from time import sleep
# 整理 json 使用的工具
import json
# 執行 command 的時候用的
import os
# 子處理程序，用來取代 os.system 的功能
import subprocess
# 啟動瀏覽器工具的選項
my_options = webdriver.ChromeOptions()
# my_options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
my_options.add_argument("--start-maximized")         #最大化視窗
my_options.add_argument("--incognito")               #開啟無痕模式
my_options.add_argument("--disable-popup-blocking") #禁用彈出攔截
my_options.add_argument("--disable-notifications")  #取消 chrome 推播通知
my_options.add_argument("--lang=zh-TW")  #設定為正體中文

# 使用 Chrome 的 WebDriver
driver = webdriver.Chrome(
    options = my_options,
    service = Service(ChromeDriverManager().install())
)

folderPath='youtube'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

listData=[]
def visit():
    driver.get('https://www.youtube.com/')

def search():
    # 輸入名稱
    txtInput = driver.find_element(By.CSS_SELECTOR, "input#search")
    txtInput.send_keys("張學友")
    
    # 等待一下
    sleep(1)
    
    # 送出表單資料
    txtInput.submit()
    
    # 等待一下
    sleep(1)
def filterFunc():
    try:
        # 等待篩選元素出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located( 
                (By.CSS_SELECTOR, "ytd-toggle-button-renderer.style-scope.ytd-search-sub-menu-renderer") 
            )
        )

        #按下篩選元素，使項目浮現
        driver.find_element(
            By.CSS_SELECTOR, 
            "ytd-toggle-button-renderer.style-scope.ytd-search-sub-menu-renderer"  #name of filter
        ).click()

        # 等待一下
        sleep(2)

        # 按下選擇的項目
        driver.find_elements(
            By.CSS_SELECTOR, 
            "yt-formatted-string.style-scope.ytd-search-filter-renderer"
        )[9].click()
        
        # 等待一下
        sleep(2)
        
    except TimeoutException:
        print("等待逾時")
def scroll():
    '''
    innerHeight => 瀏覽器內部的高度
    offset => 當前捲動的量(高度)
    count => 累計無效滾動次數
    limit => 最大無效滾動次數
    '''
    innerHeight = 0
    offset = 0
    count = 0
    limit = 3  # 3 times offset is in the bottom of innerHeight so break
    
    # 在捲動到沒有元素動態產生前，持續捲動
    while count <= limit:
        # 每次移動高度
        offset = driver.execute_script(
            'return window.document.documentElement.scrollHeight;'
        )

        '''
        或是每次只滾動一點距離，
        以免有些網站會在移動長距離後，
        將先前移動當中的元素隱藏

        例如將上方的 script 改成:
        offset += 600
        '''

        # 捲軸往下滑動 use fsting f''' to do multi lines javascript if the value is {} your fstring needs two pairs of {} for python to know top is the real value
        driver.execute_script(f'''
            window.scrollTo({{
                top: {offset}, 
                behavior: 'smooth' 
            }});
        ''')
        
        # 強制等待，此時若有新元素生成，瀏覽器內部高度會自動增加
        sleep(3)
        
        # 透過執行 js 語法來取得捲動後的當前總高度
        innerHeight = driver.execute_script(
            'return window.document.documentElement.scrollHeight;'
        )
        # 經過計算，如果滾動距離(offset)大於等於視窗內部總高度(innerHeight)，代表已經到底了
        if offset == innerHeight:
            count += 1
          
        # 如果只想看效果就開這兩行 畫面就只會捲動一次
        #if offset >= 600:
        #    break
def parse():
    # 取得主要元素的集合
    ytd_video_renderers = driver.find_elements(
        By.CSS_SELECTOR, 
        'ytd-video-renderer.style-scope.ytd-item-section-renderer'
    )
    
    # 逐一檢視元素
    for ytd_video_renderer in ytd_video_renderers:
        # 印出分隔文字
        print("=" * 30)
        
        # 取得圖片連結
        img = ytd_video_renderer.find_element(
            By.CSS_SELECTOR, 
            "img"
        )
        imgSrc = img.get_attribute('src')
        print(imgSrc)
          # 取得Hyperlink名稱
        a = ytd_video_renderer.find_element(By.CSS_SELECTOR, "a#video-title")
        aTitle = a.get_attribute('innerText')
        print(aTitle)
        
        # 取得 YouTube 連結
        aLink = a.get_attribute('href')
        print(aLink)
        
        # 取得 影音 ID
        strDelimiter = 'v='  
        youtube_id = aLink.split(strDelimiter)[1]
        print(youtube_id)
          
        # 放資料到 list 中 diy json list
        listData.append({
            "id": youtube_id,
            "title": aTitle,
            "link": aLink,
            "img": imgSrc
        })
def saveJson():
    with open(f'{folderPath}/youtube.json','w',encoding='utf-8') as file:
        file.write(json.dumps(listData, ensure_ascii=False,indent=4))
# 關閉瀏覽器
def close():
    driver.quit()
def download():   
    # 開啟 json 檔案
    with open(f"{folderPath}/youtube.json", "r", encoding='utf-8') as file:
        #取得 json 字串
        strJson = file.read()
    
    # 將 json 轉成 list (裡面是 dict 集合)
    listResult = json.loads(strJson)

    # 下載所有檔案
    for index, obj in enumerate(listResult):
        if index == 3:
            break
        
        print("=" * 50)
        print(f"正在下載連結: {obj['link']}")
        
        # 定義指令
        #Linux version cmd只有第一次要授予權限時要執行
        cmd=[
            'chmod','+x','yt-dlp'
        ]
        cmd1 = [
            './yt-dlp', 
            obj['link'], 
            '-f', 'b[ext=mp4]', 
            '-o', f'{folderPath}/%(id)s.%(ext)s'
        ]
        # windows version
        # cmd1 = [
        #     './yt-dlp.exe', 
        #     obj['link'], 
        #     '-f', 'b[ext=mp4]', 
        #     '-o', f'{folderPath}/%(id)s.%(ext)s'
        # ]
        # 執行指令，並取得回傳結果
        #subprocess.run(cmd) this line must be open for the first download
        result = subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # 將回傳結果進行解碼，顯示實際執行過程的文字輸出
        output = result.stdout
        print("下載完成，訊息如下:")
        print(output)
#如果被匯入 以下就不會執行
if __name__=="__main__":
   visit()
   search()
   filterFunc()
   scroll()
   parse()
   saveJson()
   close()
   download()