import datetime
from unittest.mock import ANY

from fastapi.testclient import TestClient

import schemas
from app import app
from mocks import MMMTestCase


class TestAdminRouter(MMMTestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.m_ParseUrlLogic = self.patch("routers.ParseRiddleLogic")
        self.m_parse_url_logic = self.m_ParseUrlLogic.return_value
        self.m_RiddleLogic = self.patch("routers.RiddleLogic")
        self.m_riddle_logic = self.m_RiddleLogic.return_value
        self.m_config.mongo = "mongodb://mock"
        self.m_config.SECRET_TOKEN = "test_secret_token"

    def test_bad_token(self) -> None:
        # arrange
        m_time = self.patch("auth.time")

        # act
        ret = self.client.delete("/admin/cache", headers={"x-mmm-token": "bad_token"})

        # assert
        m_time.sleep.assert_called_once()
        self.assertEqual(403, ret.status_code)

    def test_get_riddle_info(self) -> None:
        # arrange
        url = self.unique("https://bing.com")
        basic_riddle = schemas.BasicGameData(
            picture=self.unique("https://bing.com/image.jpg"),
            words=[self.unique("word1"), self.unique("word2")],
        )
        self.m_parse_url_logic.parse_riddle.return_value = basic_riddle

        # act
        ret = self.client.get(
            "/admin/set-riddle/info",
            headers={"x-mmm-token": self.m_config.SECRET_TOKEN},
            params={"url": url},
        )

        # assert
        self.m_ParseUrlLogic.assert_called_once_with(url=url)
        self.m_parse_url_logic.parse_riddle.assert_called_once_with()
        self.assertEqual(basic_riddle.model_dump(), ret.json())

    def test_get_set_riddle_page(self) -> None:
        # act
        ret = self.client.get(
            "/admin/set-riddle", headers={"x-mmm-token": self.m_config.SECRET_TOKEN}
        )

        # assert
        self.assertEqual(200, ret.status_code)
        self.assertIn("<title>Set Riddle</title>", ret.text)

    def test_check_riddle(self) -> None:
        # arrange
        self.m_riddle_logic.get_max_riddle_date.return_value = datetime.date(
            1989, 12, 3
        )

        def mock_redact(riddle: schemas.GameData) -> None:
            riddle.words = ["redacted!"]

        self.m_riddle_logic.redact.side_effect = mock_redact

        riddle_to_check = schemas.GameData(
            picture=self.unique("https://bing.com/image.jpg"),
            words=["john", "is", "happy"],
            author=self.unique("author"),
            dalle=3,
        )

        # act
        ret = self.client.post(
            "/admin/set-riddle/check",
            params={"lang": "fr", "date": "1989-12-05"},
            headers={"x-mmm-token": self.m_config.SECRET_TOKEN},
            json=riddle_to_check.model_dump(),
        )

        # assert
        self.assertEqual(200, ret.status_code)
        checked = ret.json()
        self.assert_contains_key_value(checked, "picture", riddle_to_check.picture)
        self.assert_contains_key_value(checked, "words", ["redacted!"])
        self.assert_contains_key_value(checked, "author", riddle_to_check.author)
        self.assert_contains_key_value(checked, "dalle", 3)
        self.assert_contains_key_value(checked, "date", "1989-12-04")

        self.m_RiddleLogic.assert_called_once_with(
            ANY, lang="fr", date=datetime.date(1989, 12, 5)
        )
        self.m_riddle_logic.redact.assert_called_once()
        self.m_riddle_logic.get_max_riddle_date.assert_called_once()

    def test_set_riddle(self) -> None:
        # arrange
        riddle = schemas.GameData(
            picture=self.unique("https://bing.com/image.jpg"),
            words=["john", "is", "happy"],
            author=self.unique("author"),
            dalle=3,
        )

        # act
        ret = self.client.post(
            "/admin/set-riddle",
            params={"lang": "fr", "date": "1989-12-05"},
            headers={"x-mmm-token": self.m_config.SECRET_TOKEN},
            json=riddle.model_dump(),
        )

        # assert
        self.m_RiddleLogic.assert_called_once_with(
            ANY, lang="fr", date=datetime.date(1989, 12, 5)
        )
        self.m_riddle_logic.set_riddle.assert_called_once_with(riddle, force=False)
        self.assertEqual(200, ret.status_code)
