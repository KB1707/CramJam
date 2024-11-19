import flet as ft
from signin_form import SignInForm
from signup_form import SignUpForm
from users_db import *
from chat_message import *
from collections import defaultdict
from datetime import datetime, timedelta

# Dictionary to store poll results
poll_results = defaultdict(lambda: defaultdict(int))  # {poll_question: {option: count}}
# Dictionary to store events
user_events = defaultdict(list)  # {date: [event1, event2]}

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

    def create_event_click(e):
        if event_name.value.strip() and event_venue.value.strip() and event_time.value.strip() and event_hub.value.strip():
            event_message = f"📅 {page.session.get('user')} just added an event:\n" \
                            f"**{event_name.value}**\n" \
                            f"Venue: {event_venue.value}\n" \
                            f"Time: {event_time.value}\n" \
                            f"Hub: {event_hub.value}\n" \
                            f"Description: {event_description.value}"
            page.pubsub.send_all(
                Message(
                    user=page.session.get("user"),
                    text=event_message,
                    message_type="event_message",
                )
            )
            # Clear input fields
            event_name.value = ""
            event_venue.value = ""
            event_time.value = ""
            event_hub.value = ""
            event_description.value = ""
        page.update()

    def render_event(message: Message):
        event_text = message.text
        return ft.Text(event_text, weight=ft.FontWeight.BOLD, size=14, color=ft.colors.GREEN)

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
        elif message.message_type == "event_message":
            m = render_event(message)
        else:
            print(f"Unsupported message type: {message.message_type}")
            return

        chat.controls.append(m)
        page.update()

    def go_to_calendar(e):
        page.route = "/calendar"
        page.update()

    # Calendar Page
    
    def calendar_view():
        def add_event(e):
            if event_date.value and event_description.value:
                date = event_date.value
                description = event_description.value
                user_events[date].append(description)
                event_date.value = ""
                event_description.value = ""
                update_calendar()
            page.update()

        def update_calendar():
            calendar.controls.clear()
            start_date = datetime.now().replace(day=1)
            for i in range(30):  # Example: 30 days for a month view
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                events = "\n".join(user_events[date])
                calendar.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(date, weight=ft.FontWeight.BOLD),
                                ft.Text(events, size=12),
                            ]
                        ),
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        padding=5,
                        expand=True,
                    )
                )
            page.update()

        event_date = ft.TextField(label="Event Date (YYYY-MM-DD)", width=200)
        event_description = ft.TextField(label="Event Description", width=300)
        add_event_button = ft.ElevatedButton(text="Add Event", on_click=add_event)

        # Adjusting GridView to use rows and runs_count if columns is not supported
        calendar = ft.GridView(
            expand=True,
            runs_count=7,  # For 7 items in a row (one for each day of the week)
            spacing=10,
            controls=[],
        )

        update_calendar()

        return ft.Column(
            [
                ft.Row([event_date, event_description, add_event_button]),
                calendar,
                ft.ElevatedButton("Back to Chat", on_click=lambda e: page.go("/chat")),
            ],
            spacing=20,
        )

    
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
        elif page.route == "/calendar":
            print("Routing to calendar page")
            page.clean()
            page.add(calendar_view())

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

    event_name = ft.TextField(label="Event Name", hint_text="Enter the event name...")
    event_venue = ft.TextField(label="Venue", hint_text="Enter the venue...")
    event_time = ft.TextField(label="Time", hint_text="Enter the event time...")
    event_hub = ft.TextField(label="Hub Name", hint_text="Enter the hub name...")
    event_description = ft.TextField(label="Description", hint_text="Enter a short description...")

    create_event_button = ft.ElevatedButton(
        text="Create Event",
        on_click=create_event_click,
    )


    # Rearrange Create Poll and Create Event UI in a column layout
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
                    ft.ElevatedButton(
                        "View Event Calendar",
                        on_click=go_to_calendar,
            ),

                ],
            ),
            ft.Column(  # Wrap Poll UI in a column
                controls=[
                    ft.Row(controls=[poll_question]),
                    ft.Row(controls=[poll_options]),
                    ft.Row(controls=[create_poll_button]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Column(  # Wrap Event UI in a column
                controls=[
                    ft.Row(controls=[event_name]),
                    ft.Row(controls=[event_venue]),
                    ft.Row(controls=[event_time]),
                    ft.Row(controls=[event_hub]),
                    ft.Row(controls=[event_description]),
                    ft.Row(controls=[create_event_button]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),

        ]
    )


    page.on_route_change = route_change
    page.add(ft.Row([signin_UI], alignment=ft.MainAxisAlignment.CENTER))

ft.app(target=main)
