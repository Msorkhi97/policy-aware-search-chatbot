from src.contracts.models import ChatMessage


def format_history(history: list[ChatMessage]) -> str:
    if not history:
        return "بدون سابقه"

    lines = []
    for message in history:
        speaker = "کاربر" if message.role == "user" else "ربات"
        lines.append(f"{speaker}: {message.content}")

    return "\n".join(lines)
