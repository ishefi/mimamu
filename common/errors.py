#!/usr/bin/env python


class MMMError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f"{super().__str__()} (error code: {self.code})"
