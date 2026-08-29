from pydantic import BaseModel


class ModerationConfig(BaseModel):
    refusal_message: str = (
        "متاسفانه اجازه پاسخ دادن به این سوال را ندارم."
    )

    no_search_message: str = (
        "من فقط می‌توانم به پرسش‌های دانشنامه‌ای "
        "که نیاز به جست‌وجو دارند پاسخ بدهم."
    )

    no_source_message: str = (
        "اطلاعات کافی در منابع در دسترس نیست."
    )

    error_message: str = (
        "الان مشکلی در ارتباط با سرویس مدل زبانی وجود داره؛ لطفاً دوباره امتحان کن."
    )