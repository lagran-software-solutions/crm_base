# from django.test import TestCase
import random
import string


prefix = "RN-"
suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
print('suffix: ', suffix)
# new_request = "RN" + str(request)
# print('new request: ', new_request.zfill(3))
