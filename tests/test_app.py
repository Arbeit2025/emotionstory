import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module


class TestEmotionStory(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()

    def test_healthz(self):
        resp = self.client.get("/healthz")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})

    def test_index_ok(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        for emotion in app_module.EMOTIONS:
            self.assertIn(emotion, resp.get_data(as_text=True))

    def test_generate_each_emotion(self):
        for emotion in app_module.EMOTIONS:
            title, body = app_module.generate_story(emotion)
            self.assertTrue(title)
            self.assertGreaterEqual(len(body), app_module.MIN_LENGTH, emotion)
            self.assertLessEqual(len(body), app_module.MAX_LENGTH, emotion)

    def test_length_range_many_draws(self):
        for emotion in app_module.EMOTIONS:
            for _ in range(30):
                _, body = app_module.generate_story(emotion)
                self.assertGreaterEqual(len(body), app_module.MIN_LENGTH)
                self.assertLessEqual(len(body), app_module.MAX_LENGTH)

    def test_keyword_reflected(self):
        _, body = app_module.generate_story("うれしい", "ねこ")
        self.assertIn("ねこ", body)

    def test_story_varies(self):
        bodies = {app_module.generate_story("おだやか")[1] for _ in range(10)}
        self.assertGreater(len(bodies), 1)

    def test_story_route_each_emotion(self):
        for emotion in app_module.EMOTIONS:
            resp = self.client.post("/story", data={"emotion": emotion})
            self.assertEqual(resp.status_code, 200, emotion)

    def test_story_route_keyword(self):
        resp = self.client.post(
            "/story", data={"emotion": "わくわく", "keyword": "誕生日"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("誕生日", resp.get_data(as_text=True))

    def test_invalid_emotion_no_500(self):
        resp = self.client.post("/story", data={"emotion": "そんざいしない感情"})
        self.assertNotEqual(resp.status_code, 500)
        self.assertEqual(resp.status_code, 200)
        # 生成ロジック側でも例外にならないこと
        title, body = app_module.generate_story("そんざいしない感情")
        self.assertTrue(title)
        self.assertGreaterEqual(len(body), app_module.MIN_LENGTH)

    def test_invalid_emotion_get_no_500(self):
        resp = self.client.get("/story?emotion=xxx")
        self.assertNotEqual(resp.status_code, 500)


if __name__ == "__main__":
    unittest.main()
