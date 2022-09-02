import datetime
import json
import random
import re

import coloredlogs
import logging
import sys
import webbrowser

import requests

from njupass import NjuUiaAuth

coloredlogs.install()
logging.basicConfig(format='%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)

auth = NjuUiaAuth()

qrcode_url = auth.get_qrcode_url()
print("请扫描给出链接中的二维码登录: " + qrcode_url)
try:
    webbrowser.open(qrcode_url)
except:
    pass

try:
    if not auth.qrcode_login():
        raise Exception("登录失败!")
except Exception as e:
    logging.exception(e)
    input()
    sys.exit(-1)

logging.info("登录成功!")

# 添加响应到课程列表
courses_list = {}

term_name = ""


def get_week(date_name):
    global term_name
    term_name = date_name.split(' ')[0]
    return int(re.search("第[0-9]*周", date_name).group()[1:-1])


logging.info("获取课程表中...")

# 从当前日期倒退回第一周
r = auth.session.get("https://wx.nju.edu.cn/njukb/wap/default/classes").json()
if r['e'] == 0:
    date = datetime.datetime.strptime(r['d']['weekdays'][0], '%Y-%m-%d') + datetime.timedelta(
        weeks=-get_week(r['d']['dateInfo']['name']) + 1)
else:
    raise Exception("非0返回: " + str(r))

logging.info("第一周第一天日期: " + date.strftime('%Y-%m-%d'))

last_week = 20
# 遍历所有周
for i in range(1, 30):
    logging.info("获取第 " + str(i) + " 周课表...")
    r = auth.session.get("https://wx.nju.edu.cn/njukb/wap/default/classes", params={
        "date": (date + datetime.timedelta(weeks=(i - 1))).strftime('%Y-%m-%d')
    }).json()
    if get_week(r['d']['dateInfo']['name']) != i:
        raise Exception("课表获取失败: 周数不符! " + str(r))

    # 前几周可能还没开课, 第10周后如果没课应该是结束了
    if i > 10 and r['d']['noClasses']:
        logging.info("第 " + str(i) + " 周没有课程, 结束.")
        last_week = i - 1
        break

    # 没有课则无需回调
    if r['d']['noClasses']:
        logging.info("第 " + str(i) + " 周没有课程, 可能未开课?")
        continue

    for i2 in r['d']['kclist']:
        for j in r['d']['kclist'][i2]:
            course = r['d']['kclist'][i2][j]
            if not course:
                continue
            if len(course) > 1:
                logging.warning("出现多节课时间重叠! 该课程不会被导入! 请退课后再次导入或手动添加.")
                continue
            course = course[0]
            logging.info("课程: " + str(course))
            if course['course_id'] not in courses_list:
                courses_list[course['course_id']] = {'time': {}, 'name': course['course_name']}
            if (course['weekday'], tuple(course['lessArr']), course['classroom'], course['teacher']) not in \
                    courses_list[course['course_id']]['time']:
                courses_list[course['course_id']]['time'][
                    (course['weekday'], tuple(course['lessArr']), course['classroom'], course['teacher'])] = []
            courses_list[course['course_id']]['time'][
                (course['weekday'], tuple(course['lessArr']), course['classroom'], course['teacher'])].append(i)

logging.info("所有课程: " + str(courses_list))

# 输出课表
with open("export.wakeup_schedule", "w", encoding="utf-8") as f:
    # 固定开头
    f.write('{"courseLen":50,"id":1,"name":"\\u9ed8\\u8ba4","sameBreakLen":false,"sameLen":true,"theBreakLen":10}\n')
    f.write(
        '[{"endTime":"08:50","node":1,"startTime":"08:00","timeTable":1},{"endTime":"09:50","node":2,"startTime":"09:00","timeTable":1},{"endTime":"11:00","node":3,"startTime":"10:10","timeTable":1},{"endTime":"12:00","node":4,"startTime":"11:10","timeTable":1},{"endTime":"14:50","node":5,"startTime":"14:00","timeTable":1},{"endTime":"15:50","node":6,"startTime":"15:00","timeTable":1},{"endTime":"17:00","node":7,"startTime":"16:10","timeTable":1},{"endTime":"18:00","node":8,"startTime":"17:10","timeTable":1},{"endTime":"19:20","node":9,"startTime":"18:30","timeTable":1},{"endTime":"20:20","node":10,"startTime":"19:30","timeTable":1},{"endTime":"21:20","node":11,"startTime":"20:30","timeTable":1},{"endTime":"21:30","node":12,"startTime":"21:25","timeTable":1},{"endTime":"21:40","node":13,"startTime":"21:35","timeTable":1},{"endTime":"21:50","node":14,"startTime":"21:45","timeTable":1},{"endTime":"22:00","node":15,"startTime":"21:55","timeTable":1},{"endTime":"22:10","node":16,"startTime":"22:05","timeTable":1},{"endTime":"22:20","node":17,"startTime":"22:15","timeTable":1},{"endTime":"22:30","node":18,"startTime":"22:25","timeTable":1},{"endTime":"22:40","node":19,"startTime":"22:35","timeTable":1},{"endTime":"22:50","node":20,"startTime":"22:45","timeTable":1},{"endTime":"23:00","node":21,"startTime":"22:55","timeTable":1},{"endTime":"23:10","node":22,"startTime":"23:05","timeTable":1},{"endTime":"23:20","node":23,"startTime":"23:15","timeTable":1},{"endTime":"23:30","node":24,"startTime":"23:25","timeTable":1},{"endTime":"23:40","node":25,"startTime":"23:35","timeTable":1},{"endTime":"23:50","node":26,"startTime":"23:45","timeTable":1},{"endTime":"23:55","node":27,"startTime":"23:51","timeTable":1},{"endTime":"23:59","node":28,"startTime":"23:56","timeTable":1},{"endTime":"00:00","node":29,"startTime":"00:00","timeTable":1},{"endTime":"00:00","node":30,"startTime":"00:00","timeTable":1}]\n')
    # 学期信息
    f.write(
        '{"background":"","courseTextColor":-1,"id":1,"itemAlpha":60,"itemHeight":64,"itemTextSize":12,"maxWeek":' + str(
            last_week) + ',"nodes":11,"showOtherWeekCourse":true,"showSat":true,"showSun":true,"showTime":false,"startDate":"' + date.strftime(
            '%Y-%m-%d') + '","strokeColor":-2130706433,"sundayFirst":false,"tableName":"\\u5357\\u5927' + str(
            term_name.encode("unicode_escape"))[2:-1].replace("\\\\",
                                                              "\\") + '","textColor":-16777216,"timeTable":1,"type":0,"widgetCourseTextColor":-1,"widgetItemAlpha":60,"widgetItemHeight":64,"widgetItemTextSize":12,"widgetStrokeColor":-2130706433,"widgetTextColor":-16777216}\n')
    # 课程信息
    logging.info("课程总数: " + str(len(courses_list)))
    colors = ["#ff" + ''.join([random.choice('0123456789abcdef') for j in range(6)])
              for i in range(len(courses_list))]
    # print(colors)

    course_json = []
    cid = 0
    for j in courses_list:
        course_json.append(
            {"color": colors[cid], "courseName": courses_list[j]['name'], "credit": 0.0, "id": cid, "note": j,
             "tableId": 1})
        courses_list[j]['cid'] = cid
        cid += 1
    f.write(json.dumps(course_json) + "\n")

    # 课程时间信息
    course_time = []
    for j in courses_list:
        for t in courses_list[j]['time']:
            for week in courses_list[j]['time'][t]:
                course_time.append({
                    "day": t[0],
                    "endTime": "",
                    "endWeek": week,
                    "startWeek": week,
                    "id": courses_list[j]['cid'],
                    "level": 0,
                    "ownTime": False,
                    "room": t[2],
                    "startNode": t[1][0],
                    "startTime": "",
                    "step": len(t[1]),
                    "tableId": 1,
                    "teacher": t[3],
                    "type": 0
                })
    f.write(json.dumps(course_time) + "\n")

logging.info("导出完成!")

logging.info("上传中...")
r = requests.post("https://i.wakeup.fun/share_schedule", data={
    "schedule": open("export.wakeup_schedule", "r", encoding="utf-8").read()
}, headers={
    "version": "180",
    "User-Agent": "okhttp/3.14.9"
})

logging.info("上传完成: " + r.text)
logging.info(">>>>>>>>>>请复制以下内容<<<<<<<<<<")
logging.info(
    "这是来自「WakeUp课程表」的课表分享，10分钟内有效哦，如果失效请朋友再分享一遍叭。为了保护隐私我们选择不监听你的剪贴板，请复制这条消息后，打开App的主界面，右上角第二个按钮 -> 从分享口令导入，按操作提示即可完成导入~分享口令为「" +
    r.json()['data'] + "」")
input()
