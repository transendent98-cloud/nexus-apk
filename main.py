from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
import socket
import threading

# Permissions for Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50)
        self.lbl = Label(text="PC Server Dhoonda ja raha hai...\n(Please wait)", font_size='20sp', halign='center')
        self.layout.add_widget(self.lbl)
        self.add_widget(self.layout)

    def start_discovery(self):
        threading.Thread(target=self.find_server, daemon=True).start()

    def find_server(self):
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
        if platform == 'android':
            # Android WebView Intent (Opens directly without kivy_garden)
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            url = f"http://{ip}:{port}/teacher-attendance"
            
            intent = Intent(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(url))
            
            current_activity = PythonActivity.mActivity
            current_activity.startActivity(intent)
            
            # App ko background mein bhej do (kyunki browser khul gaya hai)
            current_activity.moveTaskToBack(True)
        else:
            self.lbl.text = f"Connected: {ip}:{port}\n(WebView not supported on PC)"

    def show_error(self, msg):
        self.lbl.text = msg
        self.lbl.color = (1, 0, 0, 1)

class NexusApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([Permission.INTERNET, Permission.ACCESS_NETWORK_STATE, Permission.ACCESS_WIFI_STATE])
        
        sm = ScreenManager()
        self.splash = SplashScreen(name='splash')
        sm.add_widget(self.splash)
        
        Clock.schedule_once(lambda dt: self.splash.start_discovery(), 1)
        return sm

if __name__ == '__main__':
    NexusApp().run()
