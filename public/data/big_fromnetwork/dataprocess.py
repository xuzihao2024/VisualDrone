import csv
import os
from datetime import datetime

def csv_to_kml(csv_file, output_kml=None):
    """
    将CSV格式的飞行数据转换为KML格式
    
    参数:
    csv_file (str): CSV文件路径
    output_kml (str, 可选): 输出KML文件路径
    
    返回:
    str: 创建的KML文件路径
    """
    if output_kml is None:
        # 使用当前日期和时间生成文件名
        current_date = datetime.now().strftime("%b-%dth-%Y-%I-%M%p")
        output_kml = f"{current_date}-Flight-Airdata.kml"
    
    # 读取CSV数据
    coordinates = []
    home_lat, home_lon, home_alt_meters = None, None, None
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                alt_feet = float(row['altitude_above_seaLevel(feet)'])
                alt_meters = alt_feet * 0.3048  # 将英尺转换为米
                
                coordinates.append(f"{lon},{lat},{alt_meters}")
                
                # 使用第一个坐标作为起始点
                if home_lat is None:
                    home_lat = lat
                    home_lon = lon
                    home_alt_meters = alt_meters
            except (KeyError, ValueError) as e:
                print(f"警告: 无法处理行: {row}. 错误: {e}")
    
    # 提取KML文件名用于标记点
    kml_name = os.path.splitext(os.path.basename(output_kml))[0]
    
    # 定义换行符
    newline = "\n"
    
    # 创建KML内容
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Style id="copterLineStyle">
            <LineStyle>
            <color>ff00ffff</color>
                                <width>2</width>
                                                    </LineStyle>
        </Style>
        <Style id="home">
            <IconStyle>
            <Icon>
            <href>http://app.airdata.com/images/home-icon.png
            </href>
              </Icon>
                <hotSpot x="0"  y="0" xunits="fraction" yunits="fraction"/>
            </IconStyle>
              <BalloonStyle>
              <text>$[Message]</text>
                                </BalloonStyle>
        </Style>
        <Placemark>
  <name>Home</name>
  <styleUrl>#home</styleUrl>
  <ExtendedData>
    <Data name="Message">
      <value><![CDATA[Home point<BR>Altitude:{int(home_alt_meters * 3.28084)} feet<BR><BR>&nbsp;]]></value>
    </Data>
  </ExtendedData>
  <Point>
    <altitudeMode>absolute</altitudeMode>
    <coordinates>{home_lon},{home_lat},{home_alt_meters}</coordinates>
  </Point>
</Placemark>
        <Placemark>
            <name>{kml_name}</name>
            <styleUrl>#copterLineStyle</styleUrl>
            <LineString>
                <altitudeMode>absolute</altitudeMode>
                <coordinates>
                    {newline.join(coordinates)}
                </coordinates>
            </LineString>
        </Placemark>
    </Document>
</kml>"""
    
    # 写入KML文件
    with open(output_kml, 'w', encoding='utf-8') as f:
        f.write(kml_content)
    
    print(f"成功将 '{csv_file}' 转换为KML格式。")
    return output_kml

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = csv_to_kml(csv_file, output_file)
        print(f"KML文件已创建: {result}")
    else:
        print("用法: python datap.py 输入文件.csv [输出文件.kml]")
        print("示例: python datap.py flight_data.csv 我的飞行.kml")