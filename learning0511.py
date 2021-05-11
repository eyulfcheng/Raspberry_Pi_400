# Need to install Chrome WebDriver : "https://chromedriver.chromium.org/"
# Need to install pywifi module first by 
# "pip install pywifi"
# "pip install sockets"
# "pip install iperf3"
# "pip install func-timeout"
# "pip install pycopy-webbrowser"

import pywifi
import socket
import eventlet
import iperf3
import time
import func_timeout
from func_timeout import func_set_timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
import os
SERVER_IP = '10.118.252.92'

SSID_24G_NAME="CBN_CH8679G_Nelson-24G"
SSID_24G_PASSWORD="12345678"
SSID_5G_NAME="CBN_CH8679G_Nelson-5G"
SSID_5G_PASSWORD="12345678"

# SSID_24G_NAME="UPC7685281-24G"
# SSID_24G_PASSWORD="Aa12345678"
# SSID_5G_NAME="UPC7685281-5G"
# SSID_5G_PASSWORD="Aa12345678"

WAIT_TIME=15

##################################
##For scanning wifi in neighbor
##################################
def Scan():
    wifi=pywifi.PyWiFi()                                                       # 創建WiFi對象
    interface=wifi.interfaces()[0]                                             # 獲取網卡
    interface.scan()
    ssids_scan_result=interface.scan_results()
    for ssid in ssids_scan_result:
        print(ssid.ssid)

##################################
##Show local interface name
##################################
def ShowInterfaceName():
    wifi=pywifi.PyWiFi()
    interfaces=wifi.interfaces()
    for interface in interfaces:
        print(interface.name())
    return

def GetWlan0Interface():
    wifi=pywifi.PyWiFi()
    interfaces=wifi.interfaces()
    for interface in interfaces:
        if "wlan0"==interface.name():                                          # "wlan0"看起來是外網
            return interface
    return 

##################################
## iperf3 and ip
##################################
@func_set_timeout(10)
def iperf_func(server_ip = SERVER_IP):    

    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = server_ip
    client.port = 5201
    client.protocol = 'udp'    
    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    
    result = client.run()    
    if result.error:
        print(result.error)
        return result.error
    else:
        print('  local host         {0}'.format(result.local_host))
        print('  bytes transmitted  {0}'.format(result.bytes))
        print('  avg cpu load       {0}%'.format(result.local_cpu_total))
        print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
        print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))        
        return [result.local_host, result.bytes, result.local_cpu_total, result.Mbps, result.MB_s]
    # try:
    #     iperf_func()
    # except func_timeout.exceptions.FunctionTimedOut:
    #     print('task func_timeout')
            
            


##################################
## play youtube without ads 
##################################
def play_youtube(url = 'https://www.youtube.com/watch?v=WjoplqS1u18',computer_test = False):
    

    path_to_extension_ytad = r'/home/pi/Eyulf/5.1.1_0'                         # 擴充功能檔案YT_adblock位置設定
    chrome_options = Options()    
    
    chrome_options.add_argument('load-extension=' + path_to_extension_ytad)    # 載入YT_adblock
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',
                              chrome_options = chrome_options)                 # 抓到指定路徑的chromium專用chromdiver,一定要放在原本的資料夾內,
                                                                               # 並打開擴充功能    
    driver.create_options()                                                    # 打開有擴充功能的driver     
    driver.get("http://www.google.com")                                        # 隨便開一個網頁    
    handles = driver.window_handles                                            # 獲取當前瀏覽器打開的所有分頁
    # print(len(handles))                 
    driver.switch_to.window(handles[1])                                        # driver控制第二個分頁
    print('waiting for YT_adblock') 
    time.sleep(3)            
    driver.close()                                                             # 關閉driver控制的分頁
    driver.switch_to.window(handles[0])                                        # driver控制第一個分頁
    driver.get(url)
    print('waiting for YouTube') 
    time.sleep(3)  
    try:
        driver.find_element_by_class_name('ytp-large-play-button').click()     # 點擊播放
    except:
        print('Auto play ')

    
    if driver.current_url == url:
        str_output = 'Played'
    else:    
        str_output = 'Fail'
        
    print('Play youtube :',str_output)
    time.sleep(3)
    driver.quit()
    return str_output

##################################
## record in 'XXXX-XX-XX time_os.csv'
##################################
def record_in_csv(first_col = ' ' ,record_list_input = [' ']):
    today = time.strftime("%Y-%m-%d", time.localtime())
    now   = time.strftime("%H:%M:%S", time.localtime())
    
    fn = str(today) +'time_os.csv'
    if os.path.exists(fn):content = ' '
    else: content = ' , date, time, ' + first_col +'\n'
    
    content +=  ' ,' + str(today) + ', ' +str(now)
    record_list = record_list_input
    for record in record_list:
        content += ' ,' + str(record)
    content += '\n' 
    #print(content)
    with open(fn,'a') as file_Obj:
        work = file_Obj.write(content)

##################################
##Do the connection
##################################
def Connect(wifi_ssid_name, wifi_password):
    #wifi=pywifi.PyWiFi()
    #interface=wifi.interfaces()[1]
    interface=GetWlan0Interface()

    interface.disconnect()
    #wait WAIT_TIME after disconnection
    time.sleep(WAIT_TIME)                                                      # 緩衝時間
    profile_info=pywifi.Profile()                                              # 配置文件
    profile_info.ssid=wifi_ssid_name                                           # wifi名稱
    profile_info.auth=pywifi.const.AUTH_ALG_OPEN                               # 需要密碼
    if wifi_password == '':
        profile_info.akm.append(pywifi.const.AKM_TYPE_NONE)
    else:
        profile_info.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)                 # 加密類型
    profile_info.cipher=pywifi.const.CIPHER_TYPE_CCMP                          # 加密單元
    profile_info.key=wifi_password                                             # 密碼設定                               
    interface.remove_all_network_profiles()                                    # 刪除其他配置文件
    tmp_profile=interface.add_network_profile(profile_info)                    # 加載配置文件
    #wait WAIT_TIME after conneciton
    interface.connect(tmp_profile)                                             # 連接
    time.sleep(WAIT_TIME)                                                      # 等他連成功
    if  interface.status()==pywifi.const.IFACE_CONNECTED:
        stutus_result = "Successed" 
        time.sleep(WAIT_TIME)
    elif pywifi.const.IFACE_DISCONNECTED==interface.status():
        stutus_result = "Disconnected"
    elif pywifi.const.IFACE_SCANNING==interface.status():
        stutus_result = "Scanning"
    elif pywifi.const.IFACE_INACTIVE==interface.status():
        stutus_result = "Interface inactive"
    elif pywifi.const.IFACE_CONNECTING==interface.status():
        stutus_result = "Connecting"
    else :
        stutus_result = "Unknown"
    print('Connecting:',stutus_result) 
        
    return stutus_result
def switch_YTplay_iperf3_record():
    count=0;
    while True:
        
        count+=1;
        print("\nThis is %d time to test" %count)
        print("Trying to connect 24G, please wait...")
        stutus_result_24 = Connect(SSID_24G_NAME, SSID_24G_PASSWORD)        
        try:yt_result_24 = play_youtube()
        except:yt_result_24 = 'IGNORE'
        try:iperf_info_24 = iperf_func()
        except: iperf_info_24 = ['None','None','None','None','None']
        first_col      = 'times, wifi_ssid_name, stutus_result   , play youtube, local host      , bytes transmitted, average cpu load, (Mbps)          , (MB/s)          '
        record_list_24 = [count, SSID_24G_NAME , stutus_result_24, yt_result_24, iperf_info_24[0], iperf_info_24[1] , iperf_info_24[2], iperf_info_24[3], iperf_info_24[4]]
        record_in_csv(first_col, record_list_24)
        
        print("Trying to connect  5G, please wait...")
        stutus_result_5 = Connect(SSID_5G_NAME, SSID_5G_PASSWORD)
        try:yt_result_5 = play_youtube()
        except:yt_result_5 = 'IGNORE'
        try:iperf_info_5 = iperf_func()
        except: iperf_info_5 = ['None','None','None','None','None']
        #first_col     = 'times, wifi_ssid_name, stutus_result   , play youtube, local host      , bytes transmitted, average cpu load, (Mbps)          , (MB/s)          '
        record_list_5  = ['   ', SSID_5G_NAME  , stutus_result_5 , yt_result_5 , iperf_info_5 [0], iperf_info_5 [1] , iperf_info_5 [2] ,iperf_info_5 [3] ,iperf_info_5 [4]]
        record_in_csv(first_col, record_list_5 )
        #time.sleep(WAIT_TIME)





if __name__ == "__main__":
    switch_YTplay_iperf3_record()
   
        