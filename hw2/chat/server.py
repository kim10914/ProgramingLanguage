# server.py
# UDP 채팅 서버 (브로드캐스트 역할)
# 원리: 클라이언트가 보낸 UDP 패킷을 수신 → 접속 주소 목록에 등록 → 모든 클라이언트로 재전송.
# GUI: 수신 로그 출력(Text) + 서버 발신 입력(Entry)

import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk

SERVER_HOST = "0.0.0.0"     # 모든 인터페이스 바인드
SERVER_PORT = 50000         # 서버 수신 포트 (클라이언트는 여기에 보냄)
BUF_SIZE = 4096

class UdpChatServer:
    """UDP 서버. 수신 스레드 + 클라이언트 목록 관리 + 브로드캐스트 전송."""
    def __init__(self, ui_queue):
        self.ui_queue = ui_queue              # UI 스레드로 넘길 메시지 큐(스레드 세이프)
        self.clients = set()                  # (ip, port) 집합. 수신 시 자동 등록
        self.stop_event = threading.Event()

        # UDP 소켓 생성 및 바인드
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 포트 재사용(빠른 재시작)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((SERVER_HOST, SERVER_PORT))
        self.sock.settimeout(0.5)             # 종료 체크를 위해 짧은 타임아웃

        # 수신 스레드 시작
        self.thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.thread.start()

    def _recv_loop(self):
        """블로킹 수신 루프. 패킷 수신 → 클라이언트 등록 → 브로드캐스트."""
        while not self.stop_event.is_set():
            try:
                data, addr = self.sock.recvfrom(BUF_SIZE)
            except socket.timeout:
                continue
            except OSError:
                break

            msg = data.decode("utf-8", errors="replace").strip()
            # 새 클라이언트 등록
            self.clients.add(addr)

            # 간단한 프로토콜: "JOIN|닉네임", "LEAVE|닉네임", "MSG|닉네임|내용"
            parts = msg.split("|", 2)
            tag = parts[0] if parts else "MSG"

            if tag == "JOIN" and len(parts) >= 2:
                nickname = parts[1]
                text = f"[+] {nickname} joined ({addr[0]}:{addr[1]})"
                self._append_ui(text)
                self._broadcast(text)
            elif tag == "LEAVE" and len(parts) >= 2:
                nickname = parts[1]
                text = f"[-] {nickname} left"
                self._append_ui(text)
                self._broadcast(text)
                # 선택: 즉시 제거(동일 포트를 재사용하지 않을 수 있으므로 유지해도 무방)
                # self.clients.discard(addr)
            elif tag == "MSG" and len(parts) >= 3:
                nickname, content = parts[1], parts[2]
                text = f"{nickname}: {content}"
                self._append_ui(text)
                self._broadcast(text)
            else:
                # 미정의 포맷도 브로드캐스트(단순성 유지)
                self._append_ui(msg)
                self._broadcast(msg)

    def _append_ui(self, text):
        """UI 스레드로 출력요청."""
        self.ui_queue.put(text)

    def _broadcast(self, text):
        """모든 등록 클라이언트로 송신(논리적 브로드캐스트)."""
        payload = (text + "\n").encode("utf-8")
        # 에러가 나더라도 다른 클라이언트 전송은 계속
        for addr in list(self.clients):
            try:
                self.sock.sendto(payload, addr)
            except OSError:
                pass

    def send_from_server(self, text):
        """서버 GUI에서 전송한 메시지를 브로드캐스트."""
        if not text.strip():
            return
        line = f"[SERVER] {text.strip()}"
        self._append_ui(line)
        self._broadcast(line)

    def close(self):
        """정리: 스레드 종료 및 소켓 닫기."""
        self.stop_event.set()
        try:
            self.sock.close()
        except OSError:
            pass


class ServerGUI(tk.Tk):
    """Tkinter 기반 서버 GUI. 메인 스레드에서만 위젯 조작."""
    def __init__(self):
        super().__init__()
        self.title("UDP Chat Server")
        self.geometry("560x420")

        # 출력창(Text)
        self.text = tk.Text(self, state="disabled")
        self.text.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        # 입력 + 버튼
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=8, pady=(0, 8))

        self.entry = ttk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_send)

        send_btn = ttk.Button(bottom, text="Send", command=self._on_send)
        send_btn.pack(side="left", padx=(6, 0))

        # 서버 및 큐
        self.ui_queue = queue.Queue()
        self.server = UdpChatServer(self.ui_queue)

        # 주기적 큐 폴링으로 UI 갱신(스레드 안전)
        self.after(50, self._drain_queue)

        # 종료 훅
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _drain_queue(self):
        """수신 메시지 큐를 비워 Text에 반영."""
        try:
            while True:
                line = self.ui_queue.get_nowait()
                self._append_text(line)
        except queue.Empty:
            pass
        self.after(50, self._drain_queue)

    def _append_text(self, line):
        """Text 위젯 업데이트(읽기전용 유지)."""
        self.text.config(state="normal")
        self.text.insert("end", line + "\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def _on_send(self, event=None):
        text = self.entry.get()
        self.entry.delete(0, "end")
        self.server.send_from_server(text)

    def _on_close(self):
        self.server.close()
        self.destroy()


if __name__ == "__main__":
    ServerGUI().mainloop()
