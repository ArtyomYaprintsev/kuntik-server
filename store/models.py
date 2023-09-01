from django.db import models
from django.utils.translation import gettext_lazy as _

from store.utils import hex_code


class Color(models.Model):
    """Purchase color"""

    name = models.CharField(_("name"), max_length=128, unique=True)
    cost = models.PositiveIntegerField(_("color cost per m2"), default=0)
    description = models.TextField(
        _("description"), max_length=512,
        blank=True, default="",
    )


class Material(models.Model):
    """Purchase material

    Material density will be taken from
    https://www.galakmet.ru/directory/density/

    """

    name = models.CharField(_("name"), max_length=128, unique=True)
    cost = models.PositiveIntegerField(_("cost per m3"), default=0)
    destiny = models.PositiveIntegerField(_("destiny in kg/m3 units"), default=0)
    description = models.TextField(
        _("description"), max_length=512,
        blank=True, default="",
    )


class AbstractPurchase(models.Model):
    """The purchase is represented as a cube with some properties"""

    DEFAULT_PURCHASE_PRICE = 1000

    color = models.ForeignKey(
        Color, on_delete=models.PROTECT,
        verbose_name=_("color"),
    )

    material = models.ForeignKey(
        Material, on_delete=models.PROTECT,
        verbose_name=_("material"),
    )

    class Size(models.IntegerChoices):
        """Purchase size"""
        S = 1
        M = 5
        L = 10
        XL = 15
        XXL = 20
        XXXL = 25

    size = models.PositiveSmallIntegerField(
        _("purchase size with volume in m3"),
        choices=Size.choices, default=Size.M,
    )

    @property
    def square(self):
        """Calculates as the face of the cube"""
        return self.size * self.size * 6

    @property
    def volume(self):
        """Calculates as the volume of the cube"""
        return self.size * self.size * self.size

    @property
    def weight(self):
        return self.material.destiny * self.volume

    @property
    def price(self):
        """Total purchase price

        Calculated by summing default purchase price and material and color
        costs.

        """
        return (
            self.DEFAULT_PURCHASE_PRICE
            + self.material.cost * self.volume
            + self.color.cost * self.square
        )

    @property
    def delivery_type(self):
        if self.size < self.Size.XXL and self.weight < 150_000:
            return "air balloon"

        return "trolley"

    class Meta:
        abstract = True


class PreparedPurchase(AbstractPurchase):
    """Purchase with prepared properties
    
    User can choose prepared purchase settings to order or customize it.

    """

    description = models.TextField(_("description"), max_length=512)


class Purchase(AbstractPurchase):
    """Users purchase model"""

    code = models.CharField(
        _("unique code"), max_length=32,
        unique=True, default=hex_code,
    )

    class State(models.IntegerChoices):
        REJECTED = -1, _("rejected")
        WAITED = 0, _("waited")
        ACCEPTED = 1, _("accepted")
        SENT = 2, _("sent")

    state = models.PositiveSmallIntegerField(
        _("state"),
        choices=State.choices, default=State.WAITED,
    )

    address = models.CharField(_("address inside Westland"), max_length=512)

    date_created = models.DateTimeField(_("created date"), auto_now_add=True)
    date_updated = models.DateTimeField(_("updated date"), auto_now=True)

    class Meta:
        ordering = ["-date_created", 'date_updated']


class Consult(models.Model):
    """Purchase consult model
    
    If the created purchase is not prepared, then the consultant must contact
    the customer and accept or reject them. 

    """

    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE,
        verbose_name=_("purchase"),
    )

    comment = models.TextField(_("consultant comment"), max_length=512)
    is_allowed = models.BooleanField(
        _("consulted and allowed"),
        null=True, default=None,
    )

    date_created = models.DateTimeField(_("created date"), auto_now_add=True)
    date_updated = models.DateTimeField(_("updated date"), auto_now=True)

    class Meta:
        ordering = ["-date_created"]
