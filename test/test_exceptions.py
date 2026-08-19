"""Tests for app.shared.exceptions."""

import unittest
from app.shared.exceptions import (
    AppError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
)


class TestExceptions(unittest.TestCase):
    def test_app_error_is_exception(self):
        self.assertTrue(issubclass(AppError, Exception))

    def test_validation_error_inherits_app_error(self):
        self.assertTrue(issubclass(ValidationError, AppError))

    def test_authentication_error_inherits_app_error(self):
        self.assertTrue(issubclass(AuthenticationError, AppError))

    def test_not_found_error_inherits_app_error(self):
        self.assertTrue(issubclass(NotFoundError, AppError))

    def test_exceptions_can_be_raised_and_caught(self):
        with self.assertRaises(AppError):
            raise AppError('test')
        with self.assertRaises(ValidationError):
            raise ValidationError('invalid')
        with self.assertRaises(AuthenticationError):
            raise AuthenticationError('bad creds')
        with self.assertRaises(NotFoundError):
            raise NotFoundError('missing')

    def test_exceptions_catch_as_base(self):
        for exc_cls in (ValidationError, AuthenticationError, NotFoundError):
            with self.assertRaises(AppError):
                raise exc_cls('test')
