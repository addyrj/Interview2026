"""Build Email Service: templates + pluggable transport + retries. Run: python main.py"""
from __future__ import annotations

import smtplib
import ssl
import time
from dataclasses import dataclass
from email.message import EmailMessage
from string import Template
from typing import Protocol
from unittest.mock import MagicMock, patch


class Transport(Protocol):
    def send(self, msg: EmailMessage) -> None: ...


@dataclass
class SMTPTransport:
    host: str
    port: int = 587
    username: str = ""
    password: str = ""

    def send(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(self.host, self.port, timeout=10) as server:  # connect
            server.starttls(context=ssl.create_default_context())  # encrypt
            if self.username:
                server.login(self.username, self.password)
            server.send_message(msg)  # deliver


class EmailService:
    TEMPLATES = {
        "welcome": ("Welcome, $name!", "Hi $name,\nYour account is ready.\n- Team"),
        "otp": ("Your OTP", "Hi $name, your OTP is $otp. Valid for 5 minutes."),
    }

    def __init__(self, transport: Transport, sender: str, retries: int = 3, sleep=time.sleep) -> None:
        self.transport, self.sender, self.retries, self.sleep = transport, sender, retries, sleep

    def build(self, to: str, template: str, **ctx: str) -> EmailMessage:
        subject, body = self.TEMPLATES[template]
        msg = EmailMessage()
        msg["From"], msg["To"] = self.sender, to
        msg["Subject"] = Template(subject).substitute(ctx)  # fills $name etc; KeyError if missing
        msg.set_content(Template(body).substitute(ctx))  # plain text part
        msg.add_alternative(f"<p>{Template(body).substitute(ctx)}</p>", subtype="html")  # HTML part
        return msg

    def send(self, to: str, template: str, **ctx: str) -> int:
        if "@" not in to:
            raise ValueError(f"bad address: {to}")
        msg = self.build(to, template, **ctx)
        for attempt in range(1, self.retries + 1):
            try:
                self.transport.send(msg)
                return attempt  # number of attempts used
            except (smtplib.SMTPException, OSError):
                if attempt == self.retries:
                    raise
                self.sleep(2 ** attempt)  # backoff
        raise AssertionError("unreachable")


class FlakyTransport:
    def __init__(self, fail_times: int) -> None:
        self.fail_times, self.sent = fail_times, []

    def send(self, msg: EmailMessage) -> None:
        if self.fail_times:
            self.fail_times -= 1
            raise smtplib.SMTPServerDisconnected("boom")
        self.sent.append(msg)


if __name__ == "__main__":
    slept: list[int] = []
    svc = EmailService(FlakyTransport(2), "noreply@shop.in", sleep=slept.append)
    print("attempts:", svc.send("asha@example.com", "otp", name="Asha", otp="482913"), "sleeps:", slept)
    sent = svc.transport.sent[0]
    print(sent["Subject"], "|", sent.get_body(("plain",)).get_content().strip())
    assert sent["To"] == "asha@example.com" and "482913" in sent.as_string()

    try:
        EmailService(FlakyTransport(0), "a@b.c").send("nope", "otp", name="x", otp="1")
    except ValueError as e:
        print("ValueError:", e)
    try:
        EmailService(FlakyTransport(0), "a@b.c").build("a@b.c", "otp", name="x")  # missing otp
    except KeyError as e:
        print("KeyError:", e)

    with patch("smtplib.SMTP") as smtp_cls:  # no real network
        smtp_cls.return_value.__enter__.return_value = srv = MagicMock()
        EmailService(SMTPTransport("smtp.example.com", username="u", password="p"), "n@s.in").send(
            "x@y.com", "welcome", name="X")
        srv.starttls.assert_called_once(); srv.login.assert_called_once_with("u", "p"); srv.send_message.assert_called_once()
    print("all ok")
