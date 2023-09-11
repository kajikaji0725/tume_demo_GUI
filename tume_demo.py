import msvcrt
import flet as ft
from tume import Camera,View,move_dir

def main(page: ft.Page):
    page.title = "tume_demo"
    page.scroll = ft.ScrollMode.ALWAYS
    page.bgcolor = ft.colors.GREY_100
    camera = Camera()
    view = View(page,camera)
    page.add(view)
    page.on_resize = view.resize
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
