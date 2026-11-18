import re
import requests

from bs4 import BeautifulSoup


class ForumParser:
    ARTICLE_URL = (
        "https://habr.com/ru/companies/ruvds/"
        "articles/1106678/"
    )

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 "
                "Safari/537.36"
            ),
            "Accept": "application/json, text/html, */*"
        })

    def get_article_id(self, url):
        match = re.search(r"/articles/(\d+)", url)

        if not match:
            raise ValueError("Не удалось определить ID статьи")

        return int(match.group(1))

    def parse_html(self, html):
        """Извлекает комментарии из HTML."""

        soup = BeautifulSoup(html, "lxml")
        result = []

        for element in soup.select("[data-comment-id]"):
            comment_id = element.get("data-comment-id")

            author = element.select_one(
                "[data-comment-author]"
            )

            message = element.select_one(
                "[data-comment-message]"
            )

            if not comment_id or author is None or message is None:
                continue

            try:
                comment_id = int(comment_id)
            except (ValueError, TypeError):
                continue

            username = author.get_text(strip=True)
            message_html = message.decode_contents().strip()

            if not username or not message_html:
                continue

            result.append({
                "id": comment_id,
                "name": username,
                "message": message_html
            })

        return result

    def _extract_comments(self, data):
        """Извлекает комментарии из JSON-ответа Хабра."""

        result = []
        visited = set()

        def walk(value):
            if isinstance(value, list):
                for item in value:
                    walk(item)

            elif isinstance(value, dict):
                comment_id = value.get("id")
                message = value.get("message")
                author = value.get("author")

                if isinstance(author, dict):
                    username = (
                        author.get("alias")
                        or author.get("login")
                        or author.get("fullname")
                    )
                elif isinstance(author, str):
                    username = author
                else:
                    username = None

                if (
                    comment_id is not None
                    and message is not None
                    and username
                ):
                    try:
                        comment_id = int(comment_id)

                        if comment_id not in visited:
                            visited.add(comment_id)

                            message_soup = BeautifulSoup(
                                str(message),
                                "html.parser"
                            )

                            result.append({
                                "id": comment_id,
                                "name": str(username),
                                "message": (
                                    message_soup.decode_contents().strip()
                                )
                            })

                    except (ValueError, TypeError):
                        pass

                # Проверяем вложенные ответы и комментарии.
                for key in (
                    "comments",
                    "children",
                    "replies",
                    "data",
                    "items"
                ):
                    if key in value:
                        walk(value[key])

        walk(data)

        return result

    def parse_page(self, url):
        """Загружает статью и получает её комментарии."""

        article_id = self.get_article_id(url)

        # Проверяем доступность статьи.
        response = self.session.get(
            url,
            timeout=20
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        if soup.title:
            print("Статья:", soup.title.get_text(strip=True))

        # Запрашиваем комментарии.
        api_url = (
            f"https://habr.com/kek/v2/articles/"
            f"{article_id}/comments/"
        )

        api_response = self.session.get(
            api_url,
            timeout=20
        )
        api_response.raise_for_status()

        data = api_response.json()

        comments = self._extract_comments(data)

        print("Найдено комментариев:", len(comments))

        return comments

    def save_to_db(self, parsed_data, repository):
        """Сохраняет комментарии в SQLite."""

        saved = 0

        for comment in parsed_data:
            try:
                repository.add(
                    comment["id"],
                    comment["name"],
                    comment["message"]
                )
                saved += 1

            except requests.RequestException:
                raise

            except Exception as error:
                print(
                    f"Не удалось сохранить комментарий "
                    f"{comment.get('id')}: {error}"
                )

        print("Сохранено комментариев:", saved)

        return saved

    def close(self):
        self.session.close()


if __name__ == "__main__":
    from src.database import DatabaseRepository

    parser = ForumParser()
    repository = DatabaseRepository("comments.db")

    try:
        comments = parser.parse_page(
            ForumParser.ARTICLE_URL
        )

        parser.save_to_db(comments, repository)

        print("\nПервые три комментария:")

        for comment in comments[:3]:
            print(comment)

    finally:
        parser.close()
        repository.close()
