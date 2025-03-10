import time
import flet as ft
from .Camera import Camera
from .Console import Console
from .utils import (
    get_dir_username,
    create_user,
    check_current_dir,
    move_dir,
    read_now_temp_number,
    reading_qrcode_for_png,
    read_now_auth_number,
)
import os


class View(ft.UserControl):
    def __init__(self, page: ft.Page, camera: Camera) -> None:
        super().__init__()
        self.explain_method = {
            "A": "現在はA方式が選択されています．\n1:1認証方式であり，キャンセラブルは使用しません．\nQRコードの読みとりは不要です．\n初めに，ユーザを手動で選択してください．\nその次に，テンプレート画像の選択，または作成をして，認証をしてください",
            "B": "現在はB方式が選択されています．\n1:1認証方式であり，キャンセラブルを使用します．\n初めに，ユーザを手動で選択した後に，QRコードを読み込んでください．\nその次に，テンプレート画像の選択，または作成をして，認証をしてください",
            "C": "現在はC方式が選択されています．\n1:N認証方式であり，キャンセラブルは使用しません．\n初めにQRコードを読み取って自動でユーザ選択をしてください．\nその次に，テンプレート画像の選択，または作成をして，認証をしてください",
            "D": "現在はD方式が選択されています．\n1:N認証方式であり，キャンセラブルを使用します．\n初めにQRコードを読み取って，自動でユーザ選択をしてください．\nその次に，テンプレート画像の選択，または作成をして，認証をしてください．"}
        self.page = page
        self.camera = camera
        self.console = Console(page, camera)
        self.hover_tmp_cer = ""
        self.template_still_image_not_base64 = None
        self.ns = []
        self.ns_org = []
        self.ns_non_cancerable = [i for i in range(1, 26)]
        self.ns_org_non_cancerable = [i for i in range(1, 26)]
        self.user_name = ""
        self.isUser = False
        self.temp_counter = 0
        self.auth_counter = 0
        self.current_temp_number = 0
        self.is_set_User = False
        self.dir_user_names = []
        self.method = ""
        self.is_A_qrcode = False
        self.is_B_qrcode = False
        self.is_C_qrcode = False
        self.is_D_qrcode = False
        self.is_addable = False

        self.Image = ft.Image(
            src_base64=self.camera.get_image(), height=480, width=640)
        self.Template_image = ft.Image(
            src_base64=self.camera.get_image(), height=480, width=640
        )
        # self.Image = ft.Image(src="【2月】風真いろはメンバーシップ壁紙01.png", height=480, width=640)
        # self.Template_image = ft.Image(
        #     src="【2月】風真いろはメンバーシップ壁紙01.png", height=480, width=640
        # )
        self.Template_still_image = ft.Image()
        self.Create_user = ft.TextField(hint_text="新しいユーザーネーム")
        self.Text = ft.Text("ユーザ登録")

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

        self.Dialog_create_user = ft.AlertDialog(
            modal=True,
            title=ft.Text("新しいユーザーネームを入力してください"),
            actions=[
                ft.Column(
                    controls=[
                        self.Create_user,
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("OK", size=30),
                                    on_click=self.add_user,
                                ),
                                ft.TextButton(
                                    content=ft.Text("戻る", size=30),
                                    on_click=self.close_dialog_create_user,
                                ),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

        self.Another_user_button = ft.ElevatedButton(
            content=ft.Text("別のユーザ/別の方式に変更", size=50),
            on_click=self.initialized,
            disabled=not self.isUser,
        )

        self.Add_user_button = ft.ElevatedButton(
            content=ft.Text("ユーザを追加", size=50), on_click=self.open_dialog_create_user,disabled=self.is_addable
        )

        self.Add_template_button = ft.ElevatedButton(
            content=ft.Text("新しいテンプレートを作成", size=30),
            disabled=not self.isUser,
            on_click=self.open_dialog,
            on_hover=self.hover_template_Registration,
        )

        self.Authentication_button = ft.TextButton(
            content=ft.Text("認証", size=50),
            on_click=self.open_dialog,
            on_hover=self.hover_certification_Registration,
            disabled=True,
        )

        self.Chose_user = ft.Dropdown(
            options=[], on_change=self.set_username_dropdown, width=120, disabled=True
        )

        self.Chose_temp = ft.Dropdown(
            options=[],
            disabled=not self.isUser,
            on_change=self.set_temp_number_dropdown_value,
            width=120,
        )

        self.Chose_method = ft.Dropdown(
            options=[
                ft.dropdown.Option("A"),
                ft.dropdown.Option("B"),
                ft.dropdown.Option("C"),
                ft.dropdown.Option("D"),
            ],
            on_change=self.set_method_dropdown_value,
            width=50
        )

        self.Select_cancerable = ft.Checkbox(
            label="QRコードなし(簡易版)",
            value=False,
            on_change=self.chenge_checkbox_cancelable
        )

        self.Column_right = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Container(ft.Text("方式", size=30)),
                            self.Chose_method,]),
                        ft.Row(
                            controls=[
                                ft.Container(ft.Text("ユーザ", size=30)),
                                self.Chose_user,
                                self.Select_cancerable,
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Text("テンプレートNo", size=30), self.Chose_temp]
                        ),
                        self.Add_template_button,
                        ft.Container(content=self.Authentication_button,
                                     padding=ft.padding.only(left=100))
                    ],
                    # spacing=30,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            # alignment=ft.MainAxisAlignment.CENTER,
        )

    def build(self):
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[self.Another_user_button,
                                  self.Add_user_button],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    ),
                    padding=ft.padding.only(top=20),
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                # ft.Container(content=self.Image,bgcolor="black"),
                                self.Image,
                                ft.Container(content=self.Column_right,
                                             padding=ft.padding.only(left=200)),
                                # self.Column_right,
                            ],
                            width=5000,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        # ft.Row(
                        #     controls=[self.Authentication_button],
                        #     alignment=ft.MainAxisAlignment.CENTER,
                        # ),
                    ],
                ),
                self.console,
            ],
            # spacing=40
        )

    def initialized(self, e):
        self.isUser = not self.isUser
        self.Chose_user.value = ""
        self.Chose_temp.options = []
        self.ns = []
        self.ns_org = []
        self.user_name = ""
        self.temp_counter = 0
        self.auth_counter = 0
        self.current_temp_number = 0
        self.dir_user_names = []
        self.Chose_method.value = ""
        self.is_set_User = False
        self.Select_cancerable.value = False
        self.is_A_qrcode = False
        self.is_B_qrcode = False
        self.is_C_qrcode = False
        self.is_D_qrcode = False
        self.Chose_user.disabled = True
        self.is_addable = False
        self.Another_user_button.disabled = not self.isUser
        time.sleep(0.01)
        self.Add_template_button.disabled = not self.isUser
        time.sleep(0.01)
        self.Authentication_button.disabled = not self.isUser
        time.sleep(0.01)
        move_dir("../")
        self.page.update()

    def hover_certification_Registration(self, e):
        self.hover_tmp_cer = "certification_Registration"
        self.update()

    def hover_template_Registration(self, e):
        self.hover_tmp_cer = "template_Registration"
        self.update()

    def resize(self, e):
        data = e.data.split(",")
        height, witdh = (int(float(data[1])), int(float(data[0])))
        # self.Image.width = int(witdh / 2)
        # self.Column_right.width = int(witdh / 2)
        self.update()

    def chenge_checkbox_cancelable(self, e):
        if self.Select_cancerable.value:
            self.Chose_user.disabled = False
        else:
            if not (self.is_A_qrcode or self.is_B_qrcode or self.is_C_qrcode or self.is_D_qrcode) and (self.method == "C" or self.method == "D"):
                self.Chose_user.disabled = True
        self.page.update()
        self.update()

    def set_username_option(self):
        self.dir_user_names = get_dir_username(self.dir_user_names)
        self.Chose_user.options = [
            ft.dropdown.Option(username) for username in self.dir_user_names
        ]

    def set_method_dropdown_value(self, e):
        self.is_addable = True
        self.method = self.Chose_method.value
        self.console.append_cnosole(self.explain_method[self.method])
        self.console.set_method(self.method)
        if not ((self.method == "C" or self.method == "D") and not self.Select_cancerable.value):
            self.Chose_user.disabled = False
        else:
            self.Chose_user.disabled = True
        self.page.update()

    def set_temp_number_dropdown_value(self, e):
        self.current_temp_number = int(self.Chose_temp.value)
        self.Authentication_button.disabled = False
        self.page.update()

    def set_temp_number_dropdown_list(self):
        self.Chose_temp.disabled = not self.isUser
        self.current_temp_number = read_now_temp_number(self.method)
        print("set_temp_number_dropdown_list", self.current_temp_number)
        if not self.current_temp_number == None:
            self.Chose_temp.options = [
                ft.dropdown.Option(tmp_number + 1)
                for tmp_number in range(0, self.current_temp_number)
            ]
        else:
            self.Chose_temp.options = []

    def set_username_dropdown(self, e):
        self.is_set_User = True
        time.sleep(0.01)
        if not self.isUser:
            self.isUser = not self.isUser
        self.Another_user_button.disabled = not self.isUser
        time.sleep(0.01)
        self.Add_template_button.disabled = not self.isUser
        time.sleep(0.01)
        self.Authentication_button.disabled = True
        time.sleep(0.01)
        check_current_dir(self.dir_user_names)
        move_dir(self.Chose_user.value)
        self.set_temp_number_dropdown_list()
        self.temp_counter = read_now_temp_number(self.method)
        if self.temp_counter == None:
            self.temp_counter = 0
        self.auth_counter = read_now_auth_number(self.method)
        if self.auth_counter == None:
            self.auth_counter = 0
        time.sleep(0.01)
        self.page.update()

    def set_isUser(self, e):
        self.isUser = not self.isUser
        self.Add_template_button.disabled = not self.isUser
        self.update()
        self.page.update()

    def add_user(self, e):
        check_current_dir(self.dir_user_names)
        if not create_user(self.Create_user.value,self.dir_user_names):
            print("そのユーザ名は既に使われています")
        else:
            self.close_dialog_create_user(None)
            self.set_username_option()
            self.Create_user.value = ""
            self.set_temp_number_dropdown_list()
        self.update()

    def update_image(self):
        img = self.camera.get_image()
        self.Image.src_base64 = img
        self.update()

    def update_template_image(self):
        img = self.camera.get_image()
        self.Template_image.src_base64 = img
        self.update()

    def open_dialog_create_user(self, e):
        self.page.dialog = self.Dialog_create_user
        self.Dialog_create_user.open = True
        self.page.update()

    def close_dialog_create_user(self, e):
        self.Dialog_create_user.open = False
        self.page.update()

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
        ns, ns_org = reading_qrcode_for_png()
        # テンプレート保存
        if self.hover_tmp_cer == "template_Registration":
            self.temp_counter += 1
            if self.method == "A":
                self.console.save_template(
                    self.template_still_image_not_base64, self.temp_counter, self.ns_org_non_cancerable
                )
            elif self.method == "B":
                if self.Select_cancerable.value:
                    self.console.save_template(
                        self.template_still_image_not_base64, self.temp_counter, ns_org
                    )
                else:
                    if self.is_B_qrcode:
                        self.console.save_template(
                            self.template_still_image_not_base64, self.temp_counter, self.ns_org
                        )
                    else:
                        self.console.append_cnosole("QRコードを読み込んでください")
            elif self.method == "C":
                if self.Select_cancerable.value:
                    self.console.save_template(
                        self.template_still_image_not_base64, self.temp_counter, self.ns_org_non_cancerable
                    )
                else:
                    if self.is_C_qrcode:
                        self.console.save_template(
                            self.template_still_image_not_base64, self.temp_counter, self.ns_org_non_cancerable
                        )
                    else:
                        self.console.append_cnosole("QRコードを読み込んでください")
            else:
                if self.Select_cancerable.value:
                    self.console.save_template(
                        self.template_still_image_not_base64, self.temp_counter, ns_org
                    )
                else:
                    if self.is_D_qrcode:
                        self.console.save_template(
                            self.template_still_image_not_base64, self.temp_counter, self.ns_org
                        )
                    else:
                        self.console.append_cnosole("QRコードを読み込んでください")
            self.set_temp_number_dropdown_list()
            self.Chose_temp.value = self.temp_counter
            time.sleep(0.01)
            self.current_temp_number = self.temp_counter
            self.Authentication_button.disabled = False

        # 認証
        elif self.hover_tmp_cer == "certification_Registration":
            self.auth_counter += 1
            if self.method == "A":
                self.console.save_certification(
                    self.template_still_image_not_base64,
                    self.current_temp_number,
                    self.auth_counter,
                    self.ns_non_cancerable,
                    self.camera,
                )
            elif self.method == "B":
                if self.Select_cancerable.value:
                    self.console.save_certification(
                        self.template_still_image_not_base64,
                        self.current_temp_number,
                        self.auth_counter,
                        ns,
                        self.camera,
                    )
                else:
                    if self.is_B_qrcode:
                        self.console.save_certification(
                            self.template_still_image_not_base64,
                            self.current_temp_number,
                            self.auth_counter,
                            self.ns,
                            self.camera,
                        )
                    else:
                        self.console.append_cnosole("QRコードを読み込んでください")
            elif self.method == "C":
                if self.Select_cancerable.value:
                    self.console.save_certification(
                        self.template_still_image_not_base64,
                        self.current_temp_number,
                        self.auth_counter,
                        self.ns_non_cancerable,
                        self.camera,
                    )
                else:
                    if self.is_C_qrcode:
                        self.console.save_certification(
                            self.template_still_image_not_base64,
                            self.current_temp_number,
                            self.auth_counter,
                            self.ns_non_cancerable,
                            self.camera,
                        )
                    else:
                        self.console.append_cnosole("QRコードを読み込んでください")
            else:
                if self.Select_cancerable.value:
                    self.console.save_certification(
                        self.template_still_image_not_base64,
                        self.current_temp_number,
                        self.auth_counter,
                        ns,
                        self.camera,
                    )
                else:
                    if self.is_D_qrcode:
                        self.console.save_certification(
                            self.template_still_image_not_base64,
                            self.current_temp_number,
                            self.auth_counter,
                            self.ns,
                            self.camera,
                        )
                    else:
                        self.console.append_cnosole("QRコードを読み込んでください")
        self.page.update()

    def update_page(self, page):
        self.page = page
        self.update()

    def get_is_user(self):
        return self.isUser

    def get_is_dialog(self):
        return self.Dialog.open or self.Dialog_confirm.open

    def get_method(self):
        return self.method

    def get_is_B_qrcode(self):
        return self.is_B_qrcode

    def qrcode_reader(self):
        if not self.method == "" and not self.Select_cancerable.value:
            if self.method == "B" and not self.is_B_qrcode:
                if self.is_set_User:
                    self.ns, self.ns_org, _ = self.camera.qrcode_reader_cancerable()
                    if not (self.ns == None and self.ns_org == None):
                        if not (len(self.ns) == 0 and len(self.ns_org) == 0):
                            print(self.ns)
                            self.console.append_cnosole("QRコードを読み込みました")
                            self.is_B_qrcode = True
                            time.sleep(0.5)
                            self.update()
            else:
                if (self.ns == None or len(self.ns) == 0):
                    if not self.is_A_qrcode and not self.is_C_qrcode and not self.is_D_qrcode:
                        self.ns, self.ns_org, self.user_name = self.camera.qrcode_reader()
                        if not (self.ns == None and self.ns_org == None):
                            if self.method == "A" and not self.is_A_qrcode:
                                self.is_A_qrcode = True
                            elif self.method == "C" and not self.is_C_qrcode:
                                self.is_C_qrcode = True
                            elif self.method == "D" and not self.is_D_qrcode:
                                self.is_D_qrcode = True
                            print("読み取り成功です")
                            print(os.getcwd())
                            print(self.ns)
                            self.Chose_user.disabled = False
                            self.set_isUser(None)
                            self.Chose_user.value = self.user_name
                            self.set_username_option()
                            self.set_username_dropdown(None)
                            self.update()
