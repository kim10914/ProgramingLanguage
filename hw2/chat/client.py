# client.py
# UDP 채팅 클라이언트
# 원리: 하나의 UDP 소켓으로 서버에 송신 → 동일 소켓으로 수신 스레드가 수신.
# GUI: 출력창(Text) + 메시지 입력(Entry) + 닉네임/서버IP + Connect/Disconnect

import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk

SERVER_PORT = 50000     # 서버 수신 포트와 동일해야 함
BUF_SIZE = 4096

class UdpChatClient:
    """UDP 클라이언트. 서버로 송신 + 수신 스레드."""
    def __init__(self, server_host, nickname, ui_queue):
        self.server_addr = (server_host, SERVER_PORT)
        self.nickname = nickname
        self.ui_queue = ui_queue
        self.stop_event = threading.Event()

        # UDP 소켓 생성 및 바인드(에페메럴 포트)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0))          # 수신을 위해 로컬 임시 포트 확보
        self.sock.settimeout(0.5)

        # 수신 스레드 시작
        self.thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.thread.start()

        # 서버에 JOIN 통지
        self._send_raw(f"JOIN|{self.nickname}")

    def _recv_loop(self):
        """서버로부터의 브로드캐스트 수신 루프."""
        while not self.stop_event.is_set():
            try:
                data, _ = self.sock.recvfrom(BUF_SIZE)
            except socket.timeout:
                continue
            except OSError:
                break
            msg = data.decode("utf-8", errors="replace").strip()
            self.ui_queue.put(msg)

    def _send_raw(self, text):
        """원시 문자열 송신."""
        try:
            self.sock.sendto((text + "\n").encode("utf-8"), self.server_addr)
        except OSError:
            pass

    def send_message(self, text):
        """사용자 채팅 메시지 송신."""
        if not text.strip():
            return
        self._send_raw(f"MSG|{self.nickname}|{text.strip()}")

    def close(self):
        """정리: 서버에 LEAVE 통지 후 소켓 닫기."""
        try:
            self._send_raw(f"LEAVE|{self.nickname}")
        except Exception:
            pass
        self.stop_event.set()
        try:
            self.sock.close()
        except OSError:
            pass


class ClientGUI(tk.Tk):
    """Tkinter 기반 클라이언트 GUI."""
    def __init__(self):
        super().__init__()
        self.title("UDP Chat Client")
        self.geometry("560x480")

        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(top, text="Server IP:").pack(side="left")
        self.server_entry = ttk.Entry(top, width=16)
        self.server_entry.insert(0, "127.0.0.1")  # 동일 PC 테스트 기본값
        self.server_entry.pack(side="left", padx=(4, 10))

        ttk.Label(top, text="Nickname:").pack(side="left")
        self.name_entry = ttk.Entry(top, width=12)
        self.name_entry.insert(0, "guest")
        self.name_entry.pack(side="left", padx=(4, 10))

        self.conn_btn = ttk.Button(top, text="Connect", command=self._toggle_connect)
        self.conn_btn.pack(side="right")

        # 출력창(Text)
        self.text = tk.Text(self, state="disabled")
        self.text.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        # 입력 + 전송
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=8, pady=(0, 8))

        self.entry = ttk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_send)

        send_btn = ttk.Button(bottom, text="Send", command=self._on_send)
        send_btn.pack(side="left", padx=(6, 0))

        # 상태
        self.ui_queue = queue.Queue()
        self.client = None

        # 수신 큐 폴링 시작
        self.after(50, self._drain_queue)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _toggle_connect(self):
        if self.client is None:
            host = self.server_entry.get().strip()
            name = self.name_entry.get().strip() or "guest"
            self.client = UdpChatClient(host, name, self.ui_queue)
            self._append_text(f"[*] Connected to {host}:{SERVER_PORT} as {name}")
            # 연결 중 UI 잠금
            self.server_entry.config(state="disabled")
            self.name_entry.config(state="disabled")
            self.conn_btn.config(text="Disconnect")
        else:
            self.client.close()
            self.client = None
            self._append_text("[*] Disconnected")
            self.server_entry.config(state="normal")
            self.name_entry.config(state="normal")
            self.conn_btn.config(text="Connect")

    def _drain_queue(self):
        try:
            while True:
                line = self.ui_queue.get_nowait()
                self._append_text(line)
        except queue.Empty:
            pass
        self.after(50, self._drain_queue)

    def _append_text(self, line):
        self.text.config(state="normal")
        self.text.insert("end", line + "\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def _on_send(self, event=None):
        msg = self.entry.get()
        self.entry.delete(0, "end")
        if self.client:
            self.client.send_message(msg)

    def _on_close(self):
        if self.client:
            self.client.close()
        self.destroy()


if __name__ == "__main__":
    ClientGUI().mainloop()
