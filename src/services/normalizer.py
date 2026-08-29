from hazm import Normalizer


class PersianTextNormalizer:
    def __init__(self):
        self.normalizer = Normalizer()

    def normalize(self, text: str) -> str:
        text_lower = text.lower()
        return self.normalizer.normalize(text_lower)