from django.test import TestCase
from django.conf import settings
import bankapi.models as bankmodels
from django.db.models.functions import Now
# Create your tests here.


class DBTest(TestCase):
    multi_db = True
    def setUp(self):
        pass

    def test_transfer_query(self):
        new_transfer = bankmodels.Transfers(to_account_id=1,
                                            from_account_id=2,
                                            transfer_type="U_TO_U",
                                            amount="2.70",
                                            create_event_id=1,
                                            time_stamp=Now())

        new_transfer.save()