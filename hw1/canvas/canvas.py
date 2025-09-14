import tkinter as tk

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y  # 시작 좌표 저장

def draw(event):
    global last_x, last_y
    canvas.create_line(last_x, last_y, event.x, event.y, fill='black', width=2)
    last_x, last_y = event.x, event.y  # 마지막 좌표 업데이트

root = tk.Tk()
root.title("그림판")

canvas = tk.Canvas(root, bg="white", width=800, height=600)
canvas.pack()

# 마우스 이벤트 바인딩
canvas.bind("<Button-1>", start_draw)      # 마우스 클릭 시 시작점 저장
canvas.bind("<B1-Motion>", draw)           # 클릭한 채로 이동하면 선 그리기

root.mainloop()