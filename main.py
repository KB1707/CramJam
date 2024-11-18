import flet as ft
from signin_form import SignInForm
from signup_form import SignUpForm
from users_db import *
from chat_message import *
from collections import defaultdict

# Dictionary to store poll results
poll_results = defaultdict(lambda: defaultdict(int))  # {poll_question: {option: count}}

def main(page: ft.Page):
    page.title = "Cram-Jam"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # *************** Functions *************

    def send_message_click(e):
        if new_message.value.strip():
            msg = Message(
                user=page.session.get("user"),
                text=new_message.value.strip(),
                message_type="chat_message",
            )
            page.pubsub.send_all(msg)
            new_message.value = ""
        page.update()

    def upload_file_click(e):
        if upload_file_dialog.files:
            for file in upload_file_dialog.files:
                page.pubsub.send_all(
                    Message(
                        user=page.session.get("user"),
                        text=f"{file.name}",
                        message_type="file",
                        attachments=[file.name],
                    )
                )
        page.update()

    def create_poll_click(e):
        if poll_question.value.strip() and poll_options.value.strip():
            options = [opt.strip() for opt in poll_options.value.split(",")]
            page.pubsub.send_all(
                Message(
                    user=page.session.get("user"),
                    text=poll_question.value,
                    message_type="poll",
                    attachments=options,
                )
            )
            poll_question.value = ""
            poll_options.value = ""
        page.update()

    def vote_for_option(poll_text, option):
        poll_results[poll_text][option] += 1
        print(f"Vote recorded: {poll_text} - {option}")
        page.update()

    def render_poll(message: Message):
        poll_text = message.text
        options = message.attachments
        poll_controls = [
            ft.Text(f"Poll: {poll_text}", weight=ft.FontWeight.BOLD, size=16)
        ]
        for option in options:
            poll_controls.append(
                ft.ElevatedButton(
                    text=option,
                    on_click=lambda e, opt=option: vote_for_option(poll_text, opt),
                )
            )

        # Display poll results dynamically
        if poll_text in poll_results:
            results_text = "Results:\n" + "\n".join(
                [f"{opt}: {poll_results[poll_text][opt]} votes" for opt in options]
            )
            poll_controls.append(ft.Text(results_text, italic=True, size=14))

        return ft.Column(poll_controls, spacing=5)

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ft.Text(
                f"{message.user}: {message.text}",
                color=ft.colors.BLACK,
                size=14,
            )
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.WHITE, size=12)
        elif message.message_type == "file":
            m = ft.Text(
                f"{message.user} sent a file: {message.text}",
                color=ft.colors.BLUE,
            )
        elif message.message_type == "poll":
            m = render_poll(message)
        else:
            print(f"Unsupported message type: {message.message_type}")
            return

        chat.controls.append(m)
        page.update()

    # Subscribe to pubsub
    page.pubsub.subscribe(on_message)

    # ************ Application UI ************
    chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    upload_file_dialog = ft.FilePicker(on_result=upload_file_click)

    poll_question = ft.TextField(
        label="Poll Question",
        hint_text="Enter your poll question...",
    )
    poll_options = ft.TextField(
        label="Poll Options (comma-separated)",
        hint_text="e.g., Option1, Option2, Option3",
    )
    create_poll_button = ft.ElevatedButton(
        text="Create Poll",
        on_click=create_poll_click,
    )

    chat_layout = ft.Column(
        [
            ft.Container(
                content=chat,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.FILE_UPLOAD,
                        tooltip="Upload file",
                        on_click=lambda e: page.dialog.show(upload_file_dialog),
                    ),
                    new_message,
                    ft.IconButton(
                        icon=ft.icons.SEND_ROUNDED,
                        tooltip="Send message",
                        on_click=send_message_click,
                    ),
                ],
            ),
            ft.Row(
                controls=[poll_question, poll_options, create_poll_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )

    # Routes
    def route_change(route):
        if page.route == "/":
            page.clean()
            page.add(
                ft.Row(
                    [signin_UI],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        elif page.route == "/signup":
            page.clean()
            page.add(
                ft.Row(
                    [signup_UI],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        elif page.route == "/chat":
            if page.session.contains_key("user"):
                page.clean()
                page.add(chat_layout)
            else:
                page.route = "/"
                page.update()

    # *********** Instantiate UI Components ***********
    def handle_signin(user, password):
        page.session.set("user", user)
        page.route = "/chat"
        page.update()

    def go_to_signup(e):
        page.route = "/signup"
        page.update()

    def go_to_signin(e):
        page.route = "/"
        page.update()

    def on_signup_success(user, password):
        page.session.set("user", user)
        page.route = "/chat"
        page.update()

    signin_UI = SignInForm(handle_signin, go_to_signup)
    signup_UI = SignUpForm(on_signup_success, go_to_signin)

    page.on_route_change = route_change
    page.add(ft.Row([signin_UI], alignment=ft.MainAxisAlignment.CENTER))

ft.app(target=main)
