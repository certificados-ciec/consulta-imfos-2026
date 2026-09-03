import unittest

import pandas as pd

from imfos_data import normalize_identification, search_by_id


class SearchTests(unittest.TestCase):
    def test_normalize_identification_removes_formatting(self):
        self.assertEqual(normalize_identification("1.234-567 890"), "1234567890")

    def test_search_returns_all_presentations_for_same_author(self):
        frame = pd.DataFrame(
            [
                {
                    "name": "Autora Ejemplo",
                    "identification": "123456789",
                    "title": "Ponencia uno",
                    "suggestion": "Sugerencia uno",
                },
                {
                    "name": "Autora Ejemplo",
                    "identification": "123456789",
                    "title": "Ponencia dos",
                    "suggestion": "Sugerencia dos",
                },
                {
                    "name": "Otro Autor",
                    "identification": "987654321",
                    "title": "Otra ponencia",
                    "suggestion": "Otra sugerencia",
                },
            ]
        )

        result = search_by_id(frame, "123.456.789")

        self.assertEqual(list(result["title"]), ["Ponencia uno", "Ponencia dos"])


if __name__ == "__main__":
    unittest.main()
