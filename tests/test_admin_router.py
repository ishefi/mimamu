from fastapi.testclient import TestClient

import schemas
from app import app
from mocks import MMMTestCase


class TestAdminRouter(MMMTestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.m_ParseUrlLogic = self.patch("routers.ParseRiddleLogic")
        self.m_parse_url_logic = self.m_ParseUrlLogic.return_value
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
