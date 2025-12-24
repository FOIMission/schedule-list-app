import PyInstaller.__main__
import os
import shutil


def build_app():
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('todo_app.spec'):
        os.remove('todo_app.spec')

    # PyInstaller 配置参数
    params = [
        'todo_app.py',  # 主程序文件
        '--name=悬浮日程清单',  # 应用名称
        '--onefile',  # 打包成单个可执行文件
        '--windowed',  # 不显示控制台窗口
        '--icon=app_icon.ico',  # 应用图标（可选）
        '--add-data=todo_data.json;.',  # 包含数据文件
        '--noconfirm',  # 覆盖输出目录而不确认
        '--clean',  # 清理临时文件
        '--hidden-import=pystray',  # 确保包含 pystray
        '--hidden-import=PIL',  # 确保包含 PIL
        '--hidden-import=PIL._tkinter_finder',  # 确保包含 PIL 相关模块
    ]

    # 执行打包
    PyInstaller.__main__.run(params)

    print("打包完成！可执行文件在 dist 文件夹中")


if __name__ == '__main__':
    build_app()