import socket
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, RoundedRectangle, Triangle
from kivy.uix.widget import Widget

ESP32_IP = "10.223.155.95"
ESP32_PORT = 4210

Window.clearcolor = (0.91, 0.91, 0.91, 1)


class DPadWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.current_char = "S"
        self.last_sent_char = None
        self.last_send_time = 0.0
        self.zones = {}
        self.bind(pos=self.draw_ui, size=self.draw_ui)
        Clock.schedule_interval(self.udp_loop, 0.05)

    def draw_ui(self, *args):
        self.canvas.clear()
        w, h = self.width, self.height
        cx, cy = w / 2.0, h / 2.0
        size = min(w, h) * 0.42
        arm = size * 0.34
        radius = arm * 0.45

        self.zones["F"] = (cx - arm, cy + arm, cx + arm, cy + size)
        self.zones["B"] = (cx - arm, cy - size, cx + arm, cy - arm)
        self.zones["L"] = (cx - size, cy - arm, cx - arm, cy + arm)
        self.zones["R"] = (cx + arm, cy - arm, cx + size, cy + arm)
        self.zones["S"] = (cx - arm, cy - arm, cx + arm, cy + arm)

        c_rad = arm * 0.48
        t_inner = size * 0.42
        t_outer = size * 0.82
        t_half = arm * 0.48

        with self.canvas:
            Color(0.05, 0.05, 0.05, 1)
            RoundedRectangle(
                pos=(cx - arm, cy - size),
                size=(arm * 2, size * 2),
                radius=[radius],
            )
            RoundedRectangle(
                pos=(cx - size, cy - arm),
                size=(size * 2, arm * 2),
                radius=[radius],
            )

            Color(1, 1, 1, 1)
            Ellipse(pos=(cx - c_rad, cy - c_rad), size=(c_rad * 2, c_rad * 2))

            self.set_arrow_color("F")
            Triangle(
                points=[
                    cx,
                    cy + t_outer,
                    cx - t_half,
                    cy + t_inner,
                    cx + t_half,
                    cy + t_inner,
                ]
            )

            self.set_arrow_color("B")
            Triangle(
                points=[
                    cx,
                    cy - t_outer,
                    cx - t_half,
                    cy - t_inner,
                    cx + t_half,
                    cy - t_inner,
                ]
            )

            self.set_arrow_color("L")
            Triangle(
                points=[
                    cx - t_outer,
                    cy,
                    cx - t_inner,
                    cy - t_half,
                    cx - t_inner,
                    cy + t_half,
                ]
            )

            self.set_arrow_color("R")
            Triangle(
                points=[
                    cx + t_outer,
                    cy,
                    cx + t_inner,
                    cy - t_half,
                    cx + t_inner,
                    cy + t_half,
                ]
            )

    def set_arrow_color(self, cmd):
        if self.current_char == cmd:
            Color(0.0, 0.9, 0.46, 1)
        else:
            Color(1, 1, 1, 1)

    def send_udp(self, char_to_send):
        try:
            self.sock.sendto(
                char_to_send.encode("utf-8"), (ESP32_IP, ESP32_PORT)
            )
            self.last_sent_char = char_to_send
            self.last_send_time = time.time()
        except Exception:
            pass

    def process_touch(self, x, y):
        detected = "S"
        for cmd, (x1, y1, x2, y2) in self.zones.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                detected = cmd
                break

        if detected != self.current_char:
            self.current_char = detected
            self.draw_ui()
            self.send_udp(self.current_char)

    def on_touch_down(self, touch):
        self.process_touch(touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        self.process_touch(touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        self.current_char = "S"
        self.draw_ui()
        self.send_udp("S")
        return True

    def udp_loop(self, dt):
        now = time.time()
        if (self.current_char != self.last_sent_char) or (
            now - self.last_send_time > 0.1
        ):
            self.send_udp(self.current_char)


class RobotRemoteApp(App):
    def build(self):
        return DPadWidget()


if __name__ == "__main__":
    RobotRemoteApp().run()
