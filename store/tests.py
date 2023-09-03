from typing import Literal
from django.http import HttpResponse

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from store import models


class PurchaseTest(TestCase):
    """`Purchase` models logic test."""

    @classmethod
    def get_purchase_delivery_type(
        self,
        purchase: models.Purchase
    ) -> Literal["air balloon", "trolley"]:
        """Return delivery type by `Purchase` instance properties.
        
        Returns "air balloon" delivery type if `Purchase` instance size lower
        then xxl AND weight lower then 150 tones.

        """
        if (
            purchase.size < models.Purchase.Size.XXL
            and purchase.weight < 150_000
        ):
            return "air balloon"
        
        return "trolley"

    def test_purchase_delivery_type_by_size_and_weight(self):
        color = models.Color.objects.create(name="Yellow")
        material = models.Material.objects.create(name="Iron", density=7800)

        air_ballon_purchase = models.Purchase(
            color=color,
            material=material,
            size=models.Purchase.Size.S,
            address="Air ballon purchase"
        )

        self.assertEqual(
            air_ballon_purchase.delivery_type,
            self.get_purchase_delivery_type(air_ballon_purchase),
        )

        trolley_purchase = models.Purchase(
            color=color,
            material=material,
            size=models.Purchase.Size.XXXL,
            address="Trolley purchase",
        )

        self.assertEqual(
            trolley_purchase.delivery_type,
            self.get_purchase_delivery_type(trolley_purchase),
        )


class CustomerPurchaseTest(TestCase):
    """Test Customer purchase functionality logic."""

    def setUp(self) -> None:
        color = models.Color.objects.create(name="Yellow")
        material = models.Material.objects.create(
            name="Iron", density=7800,
        )

        self.prepared_purchase = (
            models.PreparedPurchase.objects.create(
                title="Yellow iron xxl prepared purchase",
                description="Prepared",
                color=color,
                material=material,
                size=models.PreparedPurchase.Size.XXL,
            )
        )

    def create_purchase_with_prepared_properties(self):
        return models.Purchase.objects.create(
            address="address",
            color=self.prepared_purchase.color,
            material=self.prepared_purchase.material,
            size=self.prepared_purchase.size,    
        )

    def create_purchase_with_custom_properties(self):
        return models.Purchase.objects.create(
            address="address",
            color=self.prepared_purchase.color,
            material=self.prepared_purchase.material,
            size=models.PreparedPurchase.Size.S,
        )

    def test_customer_can_create_purchase_with_prepared_properties(self):
        purchase = self.create_purchase_with_prepared_properties()

        self.assertTrue(
            purchase.is_prepared(),
            "The created purchase must be prepared.",
        )

    def test_customer_can_create_purchase_with_custom_properties(self):
        purchase = self.create_purchase_with_custom_properties()

        self.assertFalse(
            purchase.is_prepared(),
            "The created purchase must not be prepared.",
        )

    def test_for_prepared_purchase_customer_will_NOT_be_consulted(self):
        purchase = self.create_purchase_with_prepared_properties()

        self.assertIsNone(getattr(purchase, "consult", None))

    def test_for_custom_purchase_customer_will_be_consulted(self):
        purchase = self.create_purchase_with_custom_properties()

        self.assertIsInstance(
            getattr(purchase, "consult"),
            models.Consult,
        )


class CheckAPIAvailabilityTestMixin:
    """Provides check response availability methods.

    Notes:
        Compatibles only with viewset's views.

    """

    def check_response_availability(
        self,
        response: HttpResponse,
        request_url: str,
        expected_availability: bool,
    ) -> None:
        """Check response availability by the status code.
        
        Raises `ValueError` if requested url does not exists or requested cached
        server error, otherwise compares status code with 403 code which returns
        if request was not permitted.

        Raises:
            `ValueError`: if the response status code is 404 or higher then 499. 

        """
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise ValueError(
                f"Wrong request to {request_url}, page does not exists.",
            )

        if response.status_code > 499:
            raise ValueError(
                f"Cached {response.status_code} server error."
            )

        self.assertEqual(
            response.status_code != status.HTTP_403_FORBIDDEN,
            expected_availability,
            f"Response from {request_url} must be "
            f"{'available' if expected_availability else 'unavailable'}"
            f", but response status_code is {response.status_code}",
        )

    def get_headers(self):
        return getattr(self, "headers", {})

    def check_viewset_actions_availability(
        self,
        viewset_model,
        detail_args: tuple[str],
        expected_availability: dict[str, bool],
    ):
        """Automate views checks for the given model.
        
        Notes:
            Compatible only with viewset's views.
        
        """

        url_list = reverse(f"{viewset_model._meta.model_name}-list")
        url_detail = reverse(
            f"{viewset_model._meta.model_name}-detail",
            args=detail_args
        )

        # Check list viewset action
        self.check_response_availability(
            self.client.get(url_list, **self.get_headers()),
            url_list,
            expected_availability.get("list", False),
        )

        # Check create viewset action
        self.check_response_availability(
            self.client.post(url_list, **self.get_headers()),
            url_list,
            expected_availability.get("create", False),
        )

        # Check update viewset action
        self.check_response_availability(
            self.client.put(url_detail, **self.get_headers()),
            url_detail,
            expected_availability.get("update", False),
        )

        # Check retrieve viewset action
        self.check_response_availability(
            self.client.get(url_detail, **self.get_headers()),
            url_detail,
            expected_availability.get("retrieve", False),
        )

        # Check destroy viewset action
        self.check_response_availability(
            self.client.delete(url_detail, **self.get_headers()),
            url_detail,
            expected_availability.get("destroy", False),
        )


class CustomerAPIPermissionTest(
    CheckAPIAvailabilityTestMixin,
    APITestCase,
):
    """Tests that all API views have correct permissions for customer.

    Notes:
        Unauthenticated user is considered as Customer.

    Customers can get lists of the colors, materials and prepared purchases,
    can create a new purchase and retrieve it, can not to interact with consult
    instances.
    
    """

    def test_customer_can_only_get_colors_list(self):
        models.Color.objects.create(name="Yellow", cost=100)

        expected = {"list": True}
        self.check_viewset_actions_availability(
            models.Color, ("Yellow", ), expected,
        )

    def test_customer_can_only_get_materials_list(self):
        models.Material.objects.create(name="Iron", density=7800)

        expected = {"list": True}
        self.check_viewset_actions_availability(
            models.Material, ("Iron", ), expected,
        )

    def test_customer_can_only_get_prepared_purchases_list(self):
        color = models.Color.objects.create(name="Yellow")
        material = models.Material.objects.create(name="Iron", density=7800)

        prepared_purchase = models.PreparedPurchase.objects.create(
            title="prepared-purchase",
            description="prepared purchase description",
            color=color,
            material=material,
            size=models.PreparedPurchase.Size.S,
        )

        expected = {"list": True}
        self.check_viewset_actions_availability(
            models.PreparedPurchase, (prepared_purchase.pk, ), expected,
        )

    def test_customer_can_only_create_and_retrieve_purchase(self):
        color = models.Color.objects.create(name="Yellow")
        material = models.Material.objects.create(name="Iron", density=7800)

        purchase = models.Purchase.objects.create(
            address="Address",
            color=color,
            material=material,
            size=models.Purchase.Size.S,
        )

        expected = {"create": True, "retrieve": True}
        self.check_viewset_actions_availability(
            models.Purchase, (purchase.code, ), expected,
        )


class ManufacturerAPIPermissionTest(
    CheckAPIAvailabilityTestMixin,
    APITestCase,
):
    """Tests that all API views have correct permissions for manufacturer.

    Notes:
        Authenticated user is considered as Manufacturer.

    Customers can get lists of the colors, materials and prepared purchases,
    can create a new purchase and retrieve it, can not to interact with consult
    instances.
    
    """

    def setUp(self) -> None:
        # Create user for authentication
        user = get_user_model().objects.create(
            username="test-user",
            email="test@email.com",
            password="Pass-word123",
        )
        token = Token.objects.create(user=user)

        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token.key}"
        }

        self.all_expected = {
            "list": True,
            "create": True,
            "retrieve": True,
            "update": True,
            "destroy": True,
        }


    def test_manufacturer_has_all_permissions_for_colors(self):
        models.Color.objects.create(name="Yellow")

        self.check_viewset_actions_availability(
            models.Color, ("Yellow", ), self.all_expected,
        )

    def test_manufacturer_has_all_permissions_for_materials(self):
        models.Material.objects.create(name="Iron", density=7800)

        self.check_viewset_actions_availability(
            models.Material, ("Iron", ), self.all_expected,
        )

    def test_manufacturer_has_all_permissions_for_prepared_purchases(self):
        color = models.Color.objects.create(name="Yellow")
        material = models.Material.objects.create(name="Iron", density=7800)

        prepared_purchase = models.PreparedPurchase.objects.create(
            title="prepared-purchase",
            description="prepared purchase description",
            color=color,
            material=material,
            size=models.PreparedPurchase.Size.S,
        )

        self.check_viewset_actions_availability(
            models.PreparedPurchase, (prepared_purchase.pk, ), self.all_expected,
        )

    def test_manufacturer_has_all_permissions_for_purchases(self):
        color = models.Color.objects.create(name="Yellow")
        material = models.Material.objects.create(name="Iron", density=7800)

        purchase = models.Purchase.objects.create(
            address="Address",
            color=color,
            material=material,
            size=models.Purchase.Size.S,
        )

        self.check_viewset_actions_availability(
            models.Purchase, (purchase.code, ), self.all_expected,
        )
