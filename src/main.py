import os
import requests
import curses

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 设置你的 API 密钥
API_KEY = os.getenv("MOONSHOT_API_KEY")
BASE_URL = "https://api.moonshot.cn/v1/files"


def list_files(stdscr):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code == 200:
        files = response.json()
        stdscr.clear()  # 清除屏幕
        stdscr.addstr("Files:\n")

        max_y, max_x = stdscr.getmaxyx()  # 获取屏幕尺寸
        num_lines = max_y - 1  # 留出一行用于提示信息
        line_count = 0

        for file in files.get("data", []):
            if line_count >= num_lines:
                stdscr.addstr(max_y - 1, 0, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()  # 等待用户按键
                stdscr.clear()  # 清除屏幕
                stdscr.addstr("Files:\n")
                line_count = 0

            file_info = f"ID: {file['id']}, Filename: {file['filename']}, Status: {file['status']}\n"
            try:
                stdscr.addstr(file_info.encode("utf-8").decode("utf-8"))
            except curses.error:
                pass  # 捕获 curses.error 异常

            line_count += 1

    else:
        stdscr.addstr(
            f"Failed to list files: {response.status_code}, {response.text}\n"
        )

    stdscr.addstr(max_y - 1, 0, "Press any key to exit...")
    stdscr.refresh()
    stdscr.getch()  # 等待用户按键以退出


def delete_file(stdscr, file_id):
    url = f"{BASE_URL}/{file_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        stdscr.addstr(f"File {file_id} deleted successfully.\n")
    else:
        stdscr.addstr(
            f"Failed to delete file {file_id}: {response.status_code}, {response.text}\n"
        )
    stdscr.refresh()


def delete_all(stdscr):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code == 200:
        files = response.json()
        max_y, max_x = stdscr.getmaxyx()  # 获取屏幕尺寸
        num_lines = max_y - 1  # 留出一行用于提示信息
        line_count = 0

        stdscr.clear()  # 清除屏幕
        stdscr.addstr("Deleting files...\n")
        stdscr.refresh()

        for file in files.get("data", []):
            try:
                delete_file(stdscr, file["id"])
                line_count += 1

                # 每 10 个文件刷新屏幕，防止输出过多导致问题
                if line_count % 10 == 0:
                    stdscr.addstr(f"Deleted {line_count} files...\n")
                    stdscr.refresh()
                    curses.napms(500)  # 暂停 500 毫秒，以便用户可以看到进度
                    stdscr.clear()  # 清除屏幕
                    stdscr.addstr("Deleting files...\n")
                    stdscr.refresh()

            except curses.error:
                # 捕获 curses.error 异常，处理屏幕更新错误
                stdscr.addstr("Error updating screen.\n")
                stdscr.refresh()

        stdscr.addstr("All files deleted.\n")
    else:
        stdscr.addstr(
            f"Failed to list files for deletion: {response.status_code}, {response.text}\n"
        )

    stdscr.addstr("Press any key to exit...")
    stdscr.refresh()
    stdscr.getch()  # 等待用户按键以退出


def get_file_content(stdscr):
    stdscr.addstr("Enter file ID to get content: ")
    stdscr.refresh()
    curses.echo()
    file_id = stdscr.getstr().decode("utf-8")
    curses.noecho()

    url = f"{BASE_URL}/{file_id}/content"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        stdscr.addstr(response.text + "\n")
    else:
        stdscr.addstr(
            f"Failed to get file content: {response.status_code}, {response.text}\n"
        )
    stdscr.refresh()
    stdscr.getch()


def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()

    menu = ["List files", "Delete file", "Delete All", "Get file content", "Exit"]

    current_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr("Select an option:\n")

        for idx, item in enumerate(menu):
            if idx == current_row:
                stdscr.addstr(f"> {item}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {item}\n")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_row = (current_row - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(menu)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == "List files":
                list_files(stdscr)
            elif menu[current_row] == "Delete file":
                delete_file(stdscr)
            elif menu[current_row] == "Delete All":
                delete_all(stdscr)
            elif menu[current_row] == "Get file content":
                get_file_content(stdscr)
            elif menu[current_row] == "Exit":
                break


if __name__ == "__main__":
    curses.wrapper(main)
