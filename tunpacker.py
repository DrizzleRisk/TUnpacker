#coding=utf-8
import sys,shutil
reload(sys)
sys.setdefaultencoding('utf-8')
import os,time,zipfile
from xml.dom import minidom

PACKAGE_NAME = ''
START_ACTIVITY = ''
APK_PATH = ''
def Title():
    print '[>>>]       TUnpacker         [<<<]'
    print '[>>>]    code by Drizzle      [<<<]'
    print '[>>>]        2016.10          [<<<]'
def CheckEnv():
    Title()
    print '[*] 初始化环境'
    global APK_PATH
    global PACKAGE_NAME
    global START_ACTIVITY
    #初始化环境
    if not os.path.exists('result'):
        os.mkdir('result')
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    CPU = 'x86'
    os.popen('adb root').readlines()[0].strip('\n')
    result = os.popen('adb shell cat /proc/cpuinfo').read()
    if result.find('ARM') != -1:
        CPU = 'armeabi'
    print '[*] 目标环境: '+CPU
    print '[---------------------------------------]'
    os.popen('adb push ext-tools/' + CPU + '/tulib /data/local/tmp')
    os.popen('adb install ' + APK_PATH)
    print '[---------------------------------------]'
    #获取包信息备用
    print '[*] 获取包信息'
    nxml = open('tmp/nxml.xml','w')
    zf = zipfile.ZipFile(APK_PATH, 'r')
    content = zf.read('AndroidManifest.xml')
    nxml.write(content)
    nxml.close()
    content = os.popen('java -jar ext-tools/AXMLPrinter2.jar tmp/nxml.xml').read()
    mfest = minidom.parseString(content)
    manifest = mfest.getElementsByTagName('manifest')
    activities = mfest.getElementsByTagName("activity")
    for node in manifest:
        PACKAGE_NAME = node.getAttribute("package")
    for activity in activities:
            for sitem in activity.getElementsByTagName("action"):
                val = sitem.getAttribute("android:name")
                if val == "android.intent.action.MAIN" :
                    START_ACTIVITY = activity.getAttribute("android:name")

def Dump():
    print '[*] Dump dex'
    global PACKAGE_NAME
    global START_ACTIVITY
    os.popen('adb shell am start -n ' + PACKAGE_NAME + '/' + START_ACTIVITY)
    time.sleep(5)
    content = os.popen('adb shell ./data/local/tmp/tulib ' + PACKAGE_NAME).read()
    print '[---------------------------------------]'
    os.popen('adb pull ' + content + ' tmp/extra')
    print '[---------------------------------------]'

def Compromises():
    print '[*] 修复dex'
    global APK_PATH
    global PACKAGE_NAME
    os.popen('java -jar ext-tools/baksmali.jar ' + APK_PATH + ' -o tmp/out')
    os.popen('java -jar ext-tools/baksmali.jar tmp/extra -o tmp/out')
    #清除加固残留物
    if os.path.exists('tmp/out/com/tencent/bugly'):
        os.popen('rm -rf tmp/out/com/tencent/bugly')
    if os.path.exists('tmp/out/com/tencent/StubShell'):
        os.popen('rm -rf tmp/out/com/tencent/StubShell')
    #合并修复dex
    os.popen('java -jar ext-tools/smali.jar tmp/out -o result/' + PACKAGE_NAME + '.dex')
    if os.path.exists('result/' + PACKAGE_NAME + '.dex'):
        print '[*] 脱壳修复成功 >> ' + 'result/' + PACKAGE_NAME + '.dex'
    #清理环境
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
def Useage():
    Title()
    print '[*] Useage: tunpacker.py jiagu.apk'
    print '[*] 1.运行本程序前需要确保连接Android测试设备或虚拟机,并确保Android系统已root'
    print '[*] 2.本程序仅供安全研究及授权测试使用，如用于非法用途，后果自负'
if __name__ == '__main__':
    if len(sys.argv) < 2:
        Useage()
    else:
        APK_PATH = sys.argv[1]
        CheckEnv()
        Dump()
        Compromises()
