import unittest

from backend.config import LOCALHOST_CORS_ORIGINS, _parse_cors_origins


class CorsOriginParserTests(unittest.TestCase):
    def test_accepts_explicit_http_and_https_origins(self) -> None:
        origins = _parse_cors_origins(
            "http://example.com,https://app.example.com:8443"
        )

        self.assertEqual(
            origins,
            [
                *LOCALHOST_CORS_ORIGINS,
                "http://example.com",
                "https://app.example.com:8443",
            ],
        )

    def test_trims_whitespace_around_origins(self) -> None:
        origins = _parse_cors_origins(
            "  https://app.example.com  ,  http://localhost:4000  "
        )

        self.assertEqual(
            origins,
            [
                *LOCALHOST_CORS_ORIGINS,
                "https://app.example.com",
                "http://localhost:4000",
            ],
        )

    def test_ignores_empty_entries(self) -> None:
        origins = _parse_cors_origins(",, https://app.example.com, ,")

        self.assertEqual(
            origins,
            [*LOCALHOST_CORS_ORIGINS, "https://app.example.com"],
        )

    def test_removes_duplicates_and_preserves_localhost_defaults(self) -> None:
        origins = _parse_cors_origins(
            "https://app.example.com,http://localhost:5173,"
            "https://app.example.com,http://localhost:3000"
        )

        self.assertEqual(
            origins,
            [*LOCALHOST_CORS_ORIGINS, "https://app.example.com"],
        )

    def test_rejects_wildcard_origins(self) -> None:
        for value in ("*", "https://*.example.com"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                _parse_cors_origins(value)

    def test_rejects_non_origin_or_malformed_urls(self) -> None:
        invalid_origins = (
            "ftp://example.com",
            "example.com",
            "https://",
            "https://user:pass@example.com",
            "https://example.com/",
            "https://example.com/path",
            "https://example.com?query=value",
            "https://example.com#fragment",
            "https://example.com:",
            "https://example.com:99999",
            "https://example..com",
            "https://exa\nmple.com",
        )
        for value in invalid_origins:
            with self.subTest(value=value), self.assertRaises(ValueError):
                _parse_cors_origins(value)


if __name__ == "__main__":
    unittest.main()
