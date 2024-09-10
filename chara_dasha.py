#根据K.N.Rao Jaimini Chara Dasha计算方法编写程序：
＃作者：李化波　电话：19140441333　微信：lihuabo9413 邮箱：lhb2715@163.com




from datetime import datetime as dt
import swisseph as swe
import datetime

from scipy.stats import rankdata

import pandas as pd
import math
from typing import Dict, Tuple

from pathlib import Path


import json




#Generate Astrological data and plot charts
ad = astrocalc.generate_astrodata(bd)
#astrocalc.plot_astrocharts(astrodata,"./charts/")





# 定义12个星座
RASHIS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# 定义每个上升星座的Chara Dasha顺序（与之前相同）
CHARA_DASHA_ORDER = {
    'Aries':     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # Aries starts from Aries to Pisces
    'Taurus':    [1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2],  # Taurus starts from Taurus but in reverse order
    'Gemini':    [2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3],
    'Cancer':    [3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4],
    'Leo':       [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3],  # Leo goes forward
    'Virgo':     [5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4],
    'Libra':     [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
    'Scorpio':   [7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8],  # Scorpio reverse order
    'Sagittarius': [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9],
    'Capricorn': [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10],
    'Aquarius':  [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # Aquarius forward
    'Pisces':    [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}


# 获取 Chara Dasha 顺序
def get_chara_dasha_order(ad):
    ascendant_sign = ad["D1"]["ascendant"]["sign"]  # 从字典中获取上升星座
    if ascendant_sign in CHARA_DASHA_ORDER:
        # 输出对应的Chara Dasha顺序
        dasha_order_indices = CHARA_DASHA_ORDER[ascendant_sign]
        dasha_order = [RASHIS[i] for i in dasha_order_indices]
        return dasha_order
    else:
        raise ValueError("无效的上升星座")
# 获取 Chara Dasha 子周期顺序
def get_chara_dasha_sub_period_order(major_sign):
    """
    根据大周期星座计算子周期顺序。子周期顺序是大周期顺序的调整版，当前星座排在最后。
    major_sign: 运行的大周期星座


    """
    if major_sign not in CHARA_DASHA_ORDER:
        raise ValueError(f"无效的大周期星座: {major_sign}")

    # 获取大周期的顺序
    dasha_order_indices = CHARA_DASHA_ORDER[major_sign]
    
    # 子周期顺序中，当前的大周期星座放在最后
    sub_period_order = dasha_order_indices[1:] + dasha_order_indices[:1]
    
    # 返回星座名称
    return [RASHIS[i] for i in sub_period_order]





# 获取 Chara Dasha 顺序
#chara_dasha_sequence = get_chara_dasha_order(ad)

# 输出 Chara Dasha 顺序
#print("Chara Dasha 顺序:", chara_dasha_sequence)


# 示例：假设当前运行的是白羊座大周期
#major_sign = "Scorpio"

#获取子周期顺序
#chara_sub_period_order = get_chara_dasha_sub_period_order(major_sign)

# 输出子周期顺序
#print(f"{major_sign} 大周期的子周期顺序:", chara_sub_period_order)



# 星座的直接组和间接组
direct_group = ['Aries', 'Taurus', 'Gemini', 'Libra', 'Scorpio', 'Sagittarius']
indirect_group = ['Cancer', 'Leo', 'Virgo', 'Capricorn', 'Aquarius', 'Pisces']



# 计算顺时针和逆时针的宫位间隔
def calculate_interval(house_num1, house_num2, direction='clockwise'):
    if direction == 'clockwise':
        if house_num2 >= house_num1:
            return house_num2 - house_num1 + 1  # 包含起点宫位
        else:
            return 12 - (house_num1 - house_num2) + 1  # 包含起点宫位
    else:  # counterclockwise
        if house_num2 <= house_num1:
            return house_num1 - house_num2 + 1  # 包含起点宫位
        else:
            return 12 - (house_num2 - house_num1) + 1  # 包含起点宫位

# 计算大运年数的主函数
def calculate_dasha_years(ad):
    dasha_years = {}

    for i in range(12):
        house_sign = ad["D1"]["houses"][i]["sign"]
        house_num = ad["D1"]["houses"][i]["house-num"]
        sign_lord = ad["D1"]["houses"][i]["sign-lord"]

        # 天蝎座的特殊处理
        if house_sign == "Scorpio":
            if ad["D1"]["planets"]["Mars"]["sign"] == "Scorpio" and ad["D1"]["planets"]["Ketu"]["sign"] != "Scorpio":
                scorpio_lord = "Ketu"
            elif ad["D1"]["planets"]["Mars"]["sign"] != "Scorpio" and ad["D1"]["planets"]["Ketu"]["sign"] == "Scorpio":
                scorpio_lord = "Mars"
            elif ad["D1"]["planets"]["Mars"]["sign"] == "Scorpio" and ad["D1"]["planets"]["Ketu"]["sign"] == "Scorpio":
                interval = 12  # 守护星都在天蝎座，直接大运12年
                dasha_years[house_sign] = interval
                continue  # 跳过后续计算
            else:
                if len(ad["D1"]["planets"]["Mars"]["conjuncts"]) > len(ad["D1"]["planets"]["Ketu"]["conjuncts"]):
                    scorpio_lord = "Mars"
                else:
                    scorpio_lord = "Ketu"
                if len(ad["D1"]["planets"]["Mars"]["conjuncts"]) == len(ad["D1"]["planets"]["Ketu"]["conjuncts"]):
                    mars_position = (ad["D1"]["planets"]["Mars"]["pos"]["deg"] * 3600 +
                                     ad["D1"]["planets"]["Mars"]["pos"]["min"] * 60 +
                                     ad["D1"]["planets"]["Mars"]["pos"]["sec"])
                    ketu_position = (ad["D1"]["planets"]["Ketu"]["pos"]["deg"] * 3600 +
                                     ad["D1"]["planets"]["Ketu"]["pos"]["min"] * 60 +
                                     ad["D1"]["planets"]["Ketu"]["pos"]["sec"])
                    scorpio_lord = "Mars" if mars_position > ketu_position else "Ketu"
            sign_lord = scorpio_lord

        # 水瓶座的特殊处理
        if house_sign == "Aquarius":
            if ad["D1"]["planets"]["Saturn"]["sign"] == "Aquarius" and ad["D1"]["planets"]["Rahu"]["sign"] != "Aquarius":
                aquarius_lord = "Rahu"
            elif ad["D1"]["planets"]["Saturn"]["sign"] != "Aquarius" and ad["D1"]["planets"]["Rahu"]["sign"] == "Aquarius":
                aquarius_lord = "Saturn"
            elif ad["D1"]["planets"]["Saturn"]["sign"] == "Aquarius" and ad["D1"]["planets"]["Rahu"]["sign"] == "Aquarius":
                interval = 12  # 守护星都在水瓶座，直接大运12年
                dasha_years[house_sign] = interval
                continue  # 跳过后续计算
            else:
                if len(ad["D1"]["planets"]["Saturn"]["conjuncts"]) > len(ad["D1"]["planets"]["Rahu"]["conjuncts"]):
                    aquarius_lord = "Saturn"
                else:
                    aquarius_lord = "Rahu"
                if len(ad["D1"]["planets"]["Saturn"]["conjuncts"]) == len(ad["D1"]["planets"]["Rahu"]["conjuncts"]):
                    saturn_position = (ad["D1"]["planets"]["Saturn"]["pos"]["deg"] * 3600 +
                                       ad["D1"]["planets"]["Saturn"]["pos"]["min"] * 60 +
                                       ad["D1"]["planets"]["Saturn"]["pos"]["sec"])
                    rahu_position = (ad["D1"]["planets"]["Rahu"]["pos"]["deg"] * 3600 +
                                     ad["D1"]["planets"]["Rahu"]["pos"]["min"] * 60 +
                                     ad["D1"]["planets"]["Rahu"]["pos"]["sec"])
                    aquarius_lord = "Saturn" if saturn_position > rahu_position else "Rahu"
            sign_lord = aquarius_lord

        # 获取宫主星的宫位号
        lord_house_num = ad["D1"]["planets"][sign_lord]["house-num"]
        
        # 判断星座是直接组还是间接组，并计算间隔
        if house_sign in direct_group:
            interval = calculate_interval(house_num, lord_house_num, direction='clockwise')
        else:
            interval = calculate_interval(house_num, lord_house_num, direction='counterclockwise')


        # 特殊处理：守护星与星座位于同一宫的情况
        if interval == 0:
            interval = 12
        else:
            interval -= 1


        # 保存计算结果
        dasha_years[house_sign] = interval

    return dasha_years
'''
# 运行并输出每个星座的大运年数
dasha_years = calculate_dasha_years(ad)
for sign, years in dasha_years.items():
    print(f"{sign}的大运年数是 {years} 年")

'''




def chara(ad,bd):
    start_date = datetime.datetime(int(bd['DOB']['year']), int(bd['DOB']['month']), int(bd['DOB']['day']), int(bd['TOB']['hour']), int(bd['TOB']['min']), int(bd['TOB']['sec']))
    major_periods = {}
    sub_periods = {}
    dasha_years = calculate_dasha_years(ad)
    #主周期顺序
    chara_dasha_sequence = get_chara_dasha_order(ad)
    print(f'''大运顺序:{chara_dasha_sequence}''')
    # Major periods

    current_start_date = start_date
    total_age = 0
    for cycle in range(3):
        for index, sign in enumerate(chara_dasha_sequence):
            duration_years = dasha_years[sign]
            end_date = current_start_date + datetime.timedelta(days=duration_years * 365.25)
            
            major_periods[f"{sign}_{duration_years}y-strat:{total_age}yr"] = {
                "dashaNum": index + 1,
                "startDate": current_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "endDate": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": f"{duration_years}y",
                "startage": f"{total_age}yr",
                "endage": f"{total_age + duration_years}yr"
            }
            
            # Update for next cycle
            total_age += duration_years
            current_start_date = end_date
        
        # Sub periods (for each major period)

    current_start_date = start_date
    total_age_years = 0
    total_age_months = 0

    for cycle in range(3):
        for major_sign in chara_dasha_sequence:
            sub_period_order = get_chara_dasha_sub_period_order(major_sign)
            print(f'''次运顺序:{sub_period_order}''')
            duration_years = dasha_years[major_sign]
            sub_period_duration = duration_years / 12
            
            for index, sub_sign in enumerate(sub_period_order):
                end_date = current_start_date + datetime.timedelta(days=sub_period_duration * 365.25)
               
                # 更新年龄，子周期以年和月来表示
                total_age_years += int(sub_period_duration)
                total_age_months += (sub_period_duration * 12) % 12
                
                # 如果月超过12，则进位
                if total_age_months >= 12:
                    total_age_years += 1
                    total_age_months -= 12


                # 记录子周期
                sub_periods[f"{major_sign}-{sub_sign}-{total_age_years}yr-{int(total_age_months)}m"] = {
                    "sub": sub_sign,
                    "Major": major_sign,
                    "bhuktiNum": index + 1,
                    "startDate": current_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "endDate": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": f"{int(sub_period_duration)}yr {int((sub_period_duration * 12) % 12)}m",
                    "startage": f"{total_age_years}yr {int(total_age_months)}m",
                    "endage": f"{int(total_age_years)}yr {int(total_age_months)}m"
                }

                current_start_date = end_date
    
    return {"major_periods": major_periods, "sub_periods": sub_periods}




# 计算 Chara Dasha 的主要时期和子时期
#主周期顺序
#chara_dasha_sequence = get_chara_dasha_order(ad)

#dasha_years = calculate_dasha_years(ad)
#for sign, years in dasha_years.items():
#    print(f"{sign}的大运年数是 {years} 年")
#chara_dashas = calculate_dasha_periods(bd, ad)





# 计算顺时针和逆时针的宫位间隔
def calculate_interval_padas(house_num1, house_num2, direction='clockwise'):
    if direction == 'clockwise':
        if house_num2 >= house_num1:
            return house_num2 - house_num1  # 间隔不包含起点宫位
        else:
            return 12 - (house_num1 - house_num2)  # 间隔不包含起点宫位
    else:  # counterclockwise
        if house_num2 <= house_num1:
            return house_num1 - house_num2  # 间隔不包含起点宫位
        else:
            return 12 - (house_num2 - house_num1)  # 间隔不包含起点宫位


def calculate_upapada(ad):
    # 假设字典包含宫位和宫主星的信息
    house_12_sign = ad['D1']['houses'][11]['sign']  # 12宫位对应的星座
    house_12_lord = ad['D1']['houses'][11]['sign-lord']  # 12宫的主星

    # 获取第12宫主星所在的宫位
    house_12_lord_house_num = ad['D1']['planets'][house_12_lord]['house-num']
    
    # 计算从12宫到主星所在宫位的间隔
    interval1 = calculate_interval_padas(12, house_12_lord_house_num, direction='clockwise')
    
    # 用第一次计算出的间隔，再向前推进同样的间隔
    upa_house = (house_12_lord_house_num + interval1) % 12
    if upa_house == 0:
        upa_house = 12  # 处理模运算结果为0的情况
    
    upapada_position = ad['D1']['houses'][upa_house-1]['sign']  # 宫位从0开始计数
    
    return upapada_position


def calculate_dara_pada(ad):
    # 获取第7宫的信息
    house_7_sign = ad['D1']['houses'][6]['sign']  # 第7宫的星座
    house_7_lord = ad['D1']['houses'][6]['sign-lord']  # 第7宫的主星
    
    # 获取第7宫主星的所在宫位
    house_7_lord_house_num = ad['D1']['planets'][house_7_lord]['house-num']  # 获取主星所在的宫位
    
    # 计算从第7宫到主星所在宫位的间隔
    interval1 = calculate_interval_padas(7, house_7_lord_house_num, direction='clockwise')
    
    # 用第一次计算出的间隔，再向前推进同样的间隔
    dp_house = (house_7_lord_house_num + interval1) % 12
    if dp_house == 0:
        dp_house = 12  # 处理模运算结果为0的情况
    
    dara_pada_position = ad['D1']['houses'][dp_house-1]['sign']  # 宫位从0开始计数

    return dara_pada_position



        # 定义星座及其映射规则
        def jaimini_aspects(rashi):
            movable_signs = {'Aries': ['Leo', 'Scorpio', 'Aquarius'], 
                           'Cancer': ['Scorpio', 'Aquarius', 'Taurus'],
                           'Libra': ['Aquarius', 'Taurus', 'Leo'], 
                           'Capricorn': ['Taurus', 'Leo', 'Scorpio']}
            
            fixed_signs = {'Taurus': ['Cancer', 'Libra', 'Capricorn'],
                            'Leo': ['Libra', 'Capricorn', 'Aries'], 
                            'Scorpio': ['Capricorn', 'Aries', 'Cancer'], 
                            'Aquarius': ['Aries', 'Cancer', 'Libra']}
            
            dual_signs = {'Gemini': ['Virgo', 'Sagittarius', 'Pisces'], 
                         'Virgo': ['Sagittarius', 'Pisces', 'Gemini'], 
                         'Sagittarius': ['Pisces', 'Gemini', 'Virgo'], 
                         'Pisces': ['Gemini', 'Virgo', 'Sagittarius']}
            
            # 查找星座及其映射关系
            if rashi in movable_signs:
                return movable_signs[rashi]
            elif rashi in fixed_signs:
                return fixed_signs[rashi]
            elif rashi in dual_signs:
                return dual_signs[rashi]
            else:
                return "Invalid Rashi"

        # 测试程序
        #rashi = "Aries"
        #result = jaimini_aspects(rashi)
        #print(f"{rashi} aspects: {result}")
        

if __name__ == "__main__":
    target_year = int(bd["DOB"]["year"])+20
    chara_html= f''''''
    chara_dasha = chara(ad,bd)

    print(chara_dasha)
    """
    

    for key, value in chara_dasha["sub_periods"].items():
        print(f"Key: {key}, Value: {value}")
     # 遍历大运周期，寻找指定年份开始的大运及其开始时间

    """

    matching_chara_dasha_with_dates = []
    for chara_dasha_name, dasha_info in chara_dasha["sub_periods"].items():
        start_date_str = dasha_info["startDate"]

        start_date = dt.strptime(start_date_str[:10], "%Y-%m-%d")  # 只关注年月日部分

        if start_date.year >= target_year and start_date.year <= target_year+15:
            
            chara_html += f'''<br><font color="#FF69B4">Chara Dasha大运{chara_dasha_name},开始于{start_date_str[:10]}</font><br>'''
            chara_html += f'''主运星座：{dasha_info["Major"]}，次运星座：{dasha_info["sub"]}<br>'''
            sub_chara = dasha_info["sub"]
                
        
    print(chara_html)




# 假设ad包含D1宫位和行星信息
upapada_position = calculate_upapada(ad)
print(f"Upapada 位于第 {upapada_position} 星座")

dara_pada_position = calculate_dara_pada(ad)
print(f"Dara Pada 位于第 {dara_pada_position} 星座")


#DKN = D9中的位置；

    # 输出结果
   # print(chara_dashas)
'''
    # 转换为 JSON 格式并输出
    chara_dasha_json = json.dumps(chara_dashas, indent=4)
    #print(chara_dasha_json)

    # 将 JSON 保存到文件
    file_path = './chara_dasha.json'  # 设置文件保存路径和名称
    with open(file_path, 'w') as json_file:
        json_file.write(chara_dasha_json)

    print(f"Chara Dasha data has been saved to {file_path}"

    '''


