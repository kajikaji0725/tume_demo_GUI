import flet as ft
from tume import View,Camera

def main(page: ft.Page):
    page.title = "tume_demo"
    camera = Camera()
    view = View(page,camera)
    page.add(view)
    page.update()
    while True:
        view.update_image()
        page.update()

ft.app(target=main)
# ft.app(target=main, port=8080, view=ft.WEB_BROWSER)
