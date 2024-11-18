import flet as ft
from users_db import UsersDB  # Import the MongoDB helper class

# SignIn Form
class SignInForm(ft.UserControl):
    def __init__(self, submit_values, btn_signup):
        super().__init__()
        self.submit_values = submit_values  # Callback for valid credentials
        self.btn_signup = btn_signup  # Route to Sign Up Form
        self.db = UsersDB()  # Initialize database connection

    def btn_signin(self, e):
        if not self.text_user.value:
            self.text_user.error_text = "Name cannot be blank!"
            self.text_user.update()
            return
        if not self.text_password.value:
            self.text_password.error_text = "Password cannot be blank!"
            self.text_password.update()
            return

        # Check credentials in MongoDB
        if self.db.find_user(self.text_user.value, self.text_password.value):
            self.submit_values(self.text_user.value, self.text_password.value)
        else:
            self.text_user.error_text = "Invalid username or password!"
            self.text_user.update()

    def build(self):
        self.signin_image = ft.Container(
            content=ft.Icon(name=ft.icons.PERSON, color=ft.colors.BLUE, size=100),
            width=120,
            height=120,
            bgcolor=ft.colors.BLACK45,
            border_radius=10,
        )
        self.title_form = ft.Text(value="Sign in", text_align=ft.TextAlign.CENTER, size=30)

        self.text_user = ft.TextField(label="User Name")
        self.text_password = ft.TextField(label="Password", password=True, can_reveal_password=True)
        self.text_signin = ft.ElevatedButton(
            text="Sign in", color=ft.colors.WHITE, width=150, height=50, on_click=self.btn_signin
        )
        self.text_signup = ft.Row(
            controls=[
                ft.Text(value="Don't have an account?"),
                ft.TextButton(text="Sign Up Here", on_click=self.btn_signup),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Container(
            width=500,
            height=560,
            bgcolor=ft.colors.TEAL_800,
            padding=30,
            border_radius=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    self.signin_image,
                    self.title_form,
                    self.text_user,
                    self.text_password,
                    ft.Container(height=10),
                    self.text_signin,
                    ft.Container(height=20),
                    self.text_signup,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
