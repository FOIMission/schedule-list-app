# create_icon.py
from PIL import Image, ImageDraw, ImageFont
import os


def create_icon():
    # 创建一个 64x64 的图像
    img = Image.new('RGB', (64, 64), color='#3498db')
    draw = ImageDraw.Draw(img)

    # 绘制背景
    draw.rectangle([16, 16, 48, 48], fill='#ffffff')

    # 绘制勾号
    draw.text((24, 22), "✓", fill='#3498db', font=None)

    # 保存为 ICO 文件
    img.save('app_icon.ico', format='ICO')
    print("图标文件已创建: app_icon.ico")


if __name__ == '__main__':
    create_icon()