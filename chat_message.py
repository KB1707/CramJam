import flet as ft
import webbrowser


class Message:
    def __init__(self, user: str, text: str, message_type: str, profile: dict = None, attachments: list = None):
        self.user = user
        self.text = text
        self.message_type = message_type  # e.g., 'text', 'poll', 'event', 'file', 'link'
        self.profile = profile or {}  # { "major": "", "year": "", "interests": [] }
        self.attachments = attachments or []


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.message = message
        self.vertical_alignment = "start"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user),
                tooltip=self.get_profile_tooltip(message.profile),
            ),
            self.get_message_content(message),
        ]

    def get_message_content(self, message: Message):
        if message.message_type == "text":
            return ft.Column(
                [
                    ft.Text(message.user, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            )
        elif message.message_type == "file":
            return ft.Column(
                [
                    ft.Text(message.user, weight="bold"),
                    ft.Text(f"File shared: {message.text}", selectable=True),
                    ft.Row(
                        [
                            ft.TextButton(
                                text=attachment,
                                on_click=lambda e, a=attachment: self.download_file(a),
                            )
                            for attachment in message.attachments
                        ]
                    ),
                ],
                tight=True,
                spacing=5,
            )
        elif message.message_type == "poll":
            return ft.Column(
                [
                    ft.Text(message.user, weight="bold"),
                    ft.Text("Poll: " + message.text),
                    ft.Row(
                        [
                            ft.ElevatedButton(text=option, on_click=lambda e, o=option: self.vote_poll(o))
                            for option in message.attachments
                        ]
                    ),
                ],
                tight=True,
                spacing=5,
            )
        elif message.message_type == "event":
            return ft.Column(
                [
                    ft.Text(message.user, weight="bold"),
                    ft.Text(f"Event Notification: {message.text}"),
                ],
                tight=True,
                spacing=5,
            )
        elif message.message_type == "link":
            return ft.Column(
                [
                    ft.Text(message.user, weight="bold"),
                    ft.Text(f"Resource Link: {message.text}", selectable=True),
                    ft.TextButton(
                        text="Open Link",
                        on_click=lambda e: self.open_link(message.text),
                    ),
                ],
                tight=True,
                spacing=5,
            )
        else:
            return ft.Text("Unsupported message type.")

    def get_initials(self, user: str):
        return user[:1].capitalize()

    def get_avatar_color(self, user: str):
        colors_lookup = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL, ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user) % len(colors_lookup)]

    def get_profile_tooltip(self, profile: dict):
        if not profile:
            return "No profile details available."
        return (
            f"Major: {profile.get('major', 'Unknown')}\n"
            f"Year: {profile.get('year', 'Unknown')}\n"
            f"Interests: {', '.join(profile.get('interests', []))}"
        )

    def download_file(self, file_name: str):
        file_path = f"shared_files/{file_name}"
        try:
            print(f"Downloading file: {file_name}")
            with open(file_path, "rb") as file:
                content = file.read()
            with open(f"downloads/{file_name}", "wb") as output_file:
                output_file.write(content)
            print(f"File {file_name} downloaded successfully.")
        except FileNotFoundError:
            print(f"File {file_name} not found.")

    def vote_poll(self, poll_id: str, option: str):
        polls = {"poll_1": {"Option A": 5, "Option B": 3, "Option C": 2}}
        if poll_id in polls and option in polls[poll_id]:
            polls[poll_id][option] += 1
            print(f"Voted for: {option}. Total votes: {polls[poll_id][option]}")
        else:
            print("Invalid poll or option.")

    def open_link(self, url: str):
        print(f"Opening link: {url}")
        if url.startswith("http://") or url.startswith("https://"):
            webbrowser.open(url)
            print(f"Opened {url} in the default web browser.")
        else:
            print("Invalid URL format.")
