import flet as ft
from tume import Camera

class View(ft.UserControl):
    def __init__(self, page:ft.Page, camera:Camera) -> None:
        super().__init__()
        self.page = page
        self.camera = camera
        self.image = ft.Image(src_base64=self.camera.get_image())
    
    def build(self):
        return ft.Column(controls=[ft.Container(content=ft.Row(controls=[self.image,
                ft.Column(
                    controls=[ ft.ElevatedButton("\ Button in Container",),
                               ft.ElevatedButton("Elevated Button asdfa Container"),]
                )],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
                ft.ElevatedButton("\ Button in Container"),
                               ft.ElevatedButton("Elevated Button asdfa Container"),])
    def update_image(self):
        img = self.camera.get_image()
        self.image.src_base64 = img
        self.update()
        # self.page.update()
        # return ft.Container(
        #     content=ft.ElevatedButton("Elevated Button in Container"),
        #     bgcolor=ft.colors.YELLOW,
        #     padding=5,
        # )
    # def update_image(self):
    #     img = self.camera.get_image()
    #     image.src_base64 = img
        
        