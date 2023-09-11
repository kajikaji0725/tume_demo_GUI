import time
import flet as ft
from .Camera import Camera
from .utils import save_template, save_certification


class View(ft.UserControl):
    def __init__(self, page: ft.Page, camera: Camera) -> None:
        super().__init__()
        self.page = page
        self.camera = camera
        self.Image = ft.Image(src_base64=self.camera.get_image(), height=480, width=640)
        self.Template_image = ft.Image(
            src_base64=self.camera.get_image(), height=480, width=640
        )
        self.Template_still_image = ft.Image()
        self.hover_tmp_cer = ""
        self.template_still_image_not_base64 = None
        self.ns = []
        self.ns_org = []
        self.user_name = ""
        self.isUser = False
        self.temp_counter = 1
        self.auth_counter = 1
        # self.image = ft.Image(src="【2月】風真いろはメンバーシップ壁紙01.png", height=480, width=640)
        self.Create_user = ft.TextField(hint_text="新しいユーザーネーム")
        self.Text = ft.Text("ユーザ登録")
        self.User = ft.Text("???", size=30)

        self.Dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("指台において，爪の画像を撮影します"),
            actions=[
                ft.Column(
                    controls=[
                        self.Template_image,
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("撮影", size=30),
                                    on_click=self.open_dialog_confirm,
                                ),
                                ft.TextButton(
                                    content=ft.Text("戻る", size=30),
                                    on_click=self.close_dialog,
                                ),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

        self.Dialog_confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("この画像でいいですか？"),
            actions=[
                ft.Column(
                    controls=[
                        self.Template_still_image,
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("OK", size=30),
                                    on_click=self.clone_dialog_confirm,
                                ),
                                ft.TextButton(
                                    content=ft.Text("戻る", size=30),
                                    on_click=self.open_dialog,
                                ),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

        self.Another_user_button = ft.ElevatedButton(
            content=ft.Text("別のユーザに変更", size=50), on_click=self.set_isUser
        )

        self.Add_user_button = ft.ElevatedButton(
            content=ft.Text("ユーザを追加", size=50), on_click=self.add_user
        )

        self.Add_template_button = ft.ElevatedButton(
            content=ft.Text("新しいテンプレートを作成", size=30),
            disabled=not self.isUser,
            on_click=self.open_dialog,
            on_hover=self.hover_template_Registration,
        )

        self.Template_number_text = ft.Text("???", size=30)

        # self.userDialogButton = ft.ElevatedButton(
        #     text=self.text.value, on_click=self.open_dialog
        # )
        self.Column_right = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(ft.Text("ユーザ", size=30)),
                        self.User,
                        ft.Text("テンプレートNo", size=30),
                        self.Template_number_text,
                        self.Add_template_button,
                    ],
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def build(self):
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[self.Another_user_button, self.Add_user_button],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    padding=ft.padding.only(top=20),
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                self.Image,
                                self.Column_right,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("認証", size=50),
                                    on_click=self.open_dialog,
                                    on_hover=self.hover_certification_Registration,
                                )
                            ]
                        ),
                    ]
                ),
            ]
        )

    def hover_certification_Registration(self, e):
        self.hover_tmp_cer = "certification_Registration"
        self.update()

    def hover_template_Registration(self, e):
        self.hover_tmp_cer = "template_Registration"
        self.update()

    def resize(self, e):
        data = e.data.split(",")
        height, witdh = (int(float(data[1])), int(float(data[0])))
        self.Image.width = int(witdh / 2)
        self.Column_right.width = int(witdh / 2)
        self.update()

    def set_isUser(self, e):
        self.isUser = not self.isUser
        print(self.isUser)
        self.Add_template_button.disabled = not self.isUser
        self.update()
        self.page.update()

    def add_user(self, e):
        self.update()

    def update_image(self):
        img = self.camera.get_image()
        self.Image.src_base64 = img
        self.update()

    def update_template_image(self):
        img = self.camera.get_image()
        self.Template_image.src_base64 = img
        self.update()

    def open_dialog(self, e):
        self.Dialog_confirm.open = False
        self.page.update()
        time.sleep(0.1)
        self.page.dialog = self.Dialog
        self.Dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        self.Dialog.open = False
        self.page.update()

    def open_dialog_confirm(self, e):
        self.close_dialog(None)
        time.sleep(0.1)
        self.page.dialog = self.Dialog_confirm
        self.Dialog_confirm.open = True
        self.template_still_image_not_base64 = self.camera.get_image_not_base64()
        self.Template_still_image.src_base64 = self.camera._cv_to_base64(
            self.template_still_image_not_base64
        )
        self.page.update()

    def clone_dialog_confirm(self, e):
        self.Dialog_confirm.open = False
        if self.hover_tmp_cer == "template_Registration":
            save_template(
                self.template_still_image_not_base64, self.temp_counter - 1, self.ns_org
            )
            self.Template_number_text.value = self.temp_counter
            self.temp_counter += 1
        elif self.hover_tmp_cer == "certification_Registration":
            save_certification(
                self.template_still_image_not_base64,
                self.temp_counter - 1,
                self.auth_counter,
                self.ns,
                self.camera,
            )
            self.auth_counter += 1
        self.page.update()

    def update_page(self, page):
        self.page = page
        self.update()

    def get_is_user(self):
        return self.isUser

    def get_is_dialog(self):
        return self.Dialog.open or self.Dialog_confirm.open

    def qrcode_reader(self):
        self.ns, self.ns_org, self.user_name = self.camera.qrcode_reader()
        if not (self.ns == None and self.ns_org == None):
            self.set_isUser(None)
            self.User.value = self.user_name
            self.Template_number_text.value = "登録なし　テンプレートを登録してください"
            self.update()
