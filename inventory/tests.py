from rest_framework import status
from rest_framework.test import APITestCase

from .models import Item, Location


class ApiTests(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(name="Shelf A")

    def make_item(self, name="Laptop", location=None):
        return Item.objects.create(
            name=name, description="14 inch", location=location or self.location
        )

    # ---- locations ----
    def test_create_location(self):
        response = self.client.post(
            "/api/v1/locations/", {"name": "Shelf B"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 2)

    def test_duplicate_location_name_is_rejected(self):
        response = self.client.post(
            "/api/v1/locations/", {"name": "Shelf A"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Location.objects.count(), 1)

    def test_location_without_name_is_rejected(self):
        response = self.client.post("/api/v1/locations/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    # ---- items: create, read, update, delete ----
    def test_create_item(self):
        response = self.client.post(
            "/api/v1/items/",
            {"name": "Laptop", "description": "14 inch", "location": self.location.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.objects.get().name, "Laptop")

    def test_list_items(self):
        self.make_item("Laptop")
        self.make_item("Monitor")
        response = self.client.get("/api/v1/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_item(self):
        item = self.make_item()
        response = self.client.get(f"/api/v1/items/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop")

    def test_retrieve_missing_item_returns_404(self):
        response = self.client.get("/api/v1/items/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_item_changes_only_the_given_field(self):
        item = self.make_item()
        response = self.client.patch(
            f"/api/v1/items/{item.id}/", {"description": "updated"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.description, "updated")
        self.assertEqual(item.name, "Laptop")

    def test_delete_item(self):
        item = self.make_item()
        response = self.client.delete(f"/api/v1/items/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)

    # ---- validation ----
    def test_item_without_name_is_rejected(self):
        response = self.client.post(
            "/api/v1/items/",
            {"description": "no name", "location": self.location.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Item.objects.count(), 0)

    def test_item_with_unknown_location_is_rejected(self):
        response = self.client.post(
            "/api/v1/items/", {"name": "Laptop", "location": 9999}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("location", response.data)

    def test_item_without_location_is_rejected(self):
        response = self.client.post("/api/v1/items/", {"name": "Laptop"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("location", response.data)

    # ---- relationships and filtering ----
    def test_deleting_a_location_deletes_its_items(self):
        self.make_item("Laptop")
        self.make_item("Monitor")
        response = self.client.delete(f"/api/v1/locations/{self.location.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)

    def test_filter_items_by_location(self):
        other = Location.objects.create(name="Shelf B")
        self.make_item("Laptop", self.location)
        self.make_item("Router", other)
        response = self.client.get(f"/api/v1/items/?location={self.location.id}")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Laptop")

    # ---- pagination ----
    def test_pagination_gives_20_then_the_rest(self):
        for i in range(25):
            self.make_item(f"Item {i}")
        page1 = self.client.get("/api/v1/items/")
        page2 = self.client.get("/api/v1/items/?page=2")
        self.assertEqual(page1.data["count"], 25)
        self.assertEqual(len(page1.data["results"]), 20)
        self.assertEqual(len(page2.data["results"]), 5)

    def test_page_beyond_the_end_returns_404(self):
        response = self.client.get("/api/v1/items/?page=99")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---- health ----
    def test_health_endpoint(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})