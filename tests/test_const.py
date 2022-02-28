from unittest import TestCase

from intellifire4py.const import IntellifireErrorCode


class TestErrors(TestCase):

    def test_errors(self):


        e = IntellifireErrorCode(642)
        assert (e == IntellifireErrorCode.OFFLINE)


        # assert(IntellifireErrorString.from_code(642) == IntellifireErrorString.OFFLINE)
