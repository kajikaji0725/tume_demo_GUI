import flet as ft
from tume import Camera, View
import msvcrt
import os

def main(page: ft.Page):
    page.title = "tume_demo"
    page.scroll = ft.ScrollMode.ALWAYS
    page.bgcolor = "#F4E0C4"
    os.chdir("./tume_data")
    camera = Camera()
    view = View(page, camera)
    # view = View(page, None)
    page.add(view)
    page.on_resize = view.resize
    view.set_username_option()
    page.update()

    while True:
        if not view.get_is_user():
            view.qrcode_reader()
        if view.get_is_dialog():
            view.update_template_image()
        else:
            view.update_image()
        #     entry.update_image()
        page.update()


ft.app(target=main)
# ft.app(target=main, port=8080, view=ft.WEB_BROWSER)
