
import socket
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from kivy_garden.webview import WebView

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        self.status_label = Label(text="PC Server Dhoonda ja raha hai...\n(Please wait)", font_size='18sp', halign='center')
        layout.add_widget(self.status_label)
        self.add_widget(layout)

    def start_discovery(self):
        threading.Thread(target=self.discover_server, daemon=True).start()

    def discover_server(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(('', 5001))
        udp_socket.settimeout(10)

        try:
            while True:
                data, addr = udp_socket.recvfrom(1024)
                msg = data.decode('utf-8')
                if msg.startswith("NEXUS_SERVER_IP:"):
                    parts = msg.split(":")
                    server_ip = parts[1]
                    server_port = parts[2]
                    Clock.schedule_once(lambda dt: self.go_to_app(server_ip, server_port))
                    break
        except socket.timeout:
            Clock.schedule_once(lambda dt: self.show_error("Server nahi mila!\nPC aur Mobile same WiFi par hone chahiye."))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))

    def go_to_app(self, ip, port):
        self.manager.get_screen('web').load_app(f"http://{ip}:{port}/teacher-attendance")
        self.manager.current = 'web'

    def show_error(self, msg):
        self.status_label.text = msg
        self.status_label.color = (1, 0, 0, 1)

class WebScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)

    def load_app(self, url):
        if platform == 'android':
            self.webview = WebView(url=url)
        else:
            self.webview = Label(text=f"WebView: {url}")
        self.layout.clear_widgets()
        self.layout.add_widget(self.webview)

class NexusApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([Permission.INTERNET, Permission.ACCESS_NETWORK_STATE, Permission.ACCESS_WIFI_STATE])

        sm = ScreenManager()
        self.splash = SplashScreen(name='splash')
        self.web = WebScreen(name='web')
        sm.add_widget(self.splash)
        sm.add_widget(self.web)

        Clock.schedule_once(lambda dt: self.splash.start_discovery(), 1)
        return sm

if __name__ == '__main__':
    NexusApp().run()
