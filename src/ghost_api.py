from abc import ABC, abstractmethod


class CMSBackend(ABC):
    @abstractmethod
    def create_post(self, title: str, html: str, status: str = "draft",
                    author_email: str = "", tags: list[str] | None = None) -> dict:
        pass

    @abstractmethod
    def update_post(self, post_id: str, **kwargs) -> dict:
        pass

    @abstractmethod
    def get_post(self, post_id: str) -> dict:
        pass

    @abstractmethod
    def list_posts(self, status: str = "all", limit: int = 15) -> list[dict]:
        pass

    @abstractmethod
    def publish_post(self, post_id: str) -> dict:
        pass

    @abstractmethod
    def upload_image(self, file_path: str, ref: str = "") -> str:
        pass
