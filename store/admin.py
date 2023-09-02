from django.contrib import admin

from store import models


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", )
    list_display_links = ("name", )
    sortable_by = ("name", "cost", )


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", "density", )
    list_display_links = ("name", )
    sortable_by = ("name", "cost", )


@admin.register(models.PreparedPurchase)
class PreparedPurchaseAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "material", "price", )
    sortable_by = ("color", "material", "price", )

    @admin.display()
    def name(self, obj):
        return str(obj)


class ConsultInline(admin.StackedInline):
    model = models.Consult
    extra = 0

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False


@admin.register(models.Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    inlines = [ConsultInline, ]

    list_display = ("code", "state", "price", "color", "material", "date_created", )
    sortable_by = ("state", "date_created", )

    fieldsets = (
        (None, {
            "classes": ("wide", ),
            "fields": (
                "address", "state",
            )
        }),
        ("Properties", {
            "classes": ("wide", ),
            "fields": (
                "color", "material", "size",
            )
        }),
    )
