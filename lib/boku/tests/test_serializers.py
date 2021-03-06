from django.core.urlresolvers import reverse
from nose.tools import eq_

from ..serializers import SellerBokuSerializer
from .utils import SellerBokuTest
from lib.sellers.models import SellerBoku


class SellerBokuSerializerTests(SellerBokuTest):

    def test_seller_required(self):
        del self.seller_data['seller']

        serializer = SellerBokuSerializer(data=self.seller_data)
        eq_(serializer.is_valid(), False)

    def test_merchant_id_required(self):
        del self.seller_data['merchant_id']

        serializer = SellerBokuSerializer(data=self.seller_data)
        eq_(serializer.is_valid(), False)

    def test_service_id_required(self):
        del self.seller_data['service_id']

        serializer = SellerBokuSerializer(data=self.seller_data)
        eq_(serializer.is_valid(), False)

    def test_valid_data_creates_new_boku_seller(self):
        serializer = SellerBokuSerializer(data=self.seller_data)
        eq_(serializer.is_valid(), True)
        serializer.save()
        seller_boku = SellerBoku.objects.get(pk=serializer.object.pk)
        eq_(seller_boku.seller, self.seller)
        eq_(seller_boku.merchant_id, self.seller_data['merchant_id'])
        eq_(seller_boku.service_id, self.seller_data['service_id'])

    def test_serializer_outputs_correct_data(self):
        seller_boku = SellerBoku.objects.create(
            seller=self.seller,
            merchant_id='12345',
            service_id='12345'
        )

        serializer = SellerBokuSerializer(seller_boku)
        eq_(serializer.data['id'], seller_boku.pk)
        eq_(serializer.data['seller'], self.seller_uri)
        eq_(serializer.data['merchant_id'], seller_boku.merchant_id)
        eq_(serializer.data['service_id'], seller_boku.service_id)
        eq_(serializer.data['resource_uri'],
            reverse('boku:sellerboku-detail', kwargs={'pk': seller_boku.pk}))
