from uuid import uuid4

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def create_test_location():
    name = f"Test Location {uuid4()}"

    response = client.post(
        "/api/locations/config",
        json={
            "location_name": name,
            "zones": [
                {
                    "name": "Zone A",
                    "moisture_threshold_low": 0.30,
                    "moisture_threshold_high": 0.70,
                    "schedule": {},
                },
                {
                    "name": "Zone B",
                    "moisture_threshold_low": 0.20,
                    "moisture_threshold_high": 0.60,
                    "schedule": {},
                },
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


def delete_test_location(location_id: str):
    client.delete(
        f"/api/locations/{location_id}"
    )


def test_create_and_get_location_config():
    created = create_test_location()

    location_id = created["location"]["id"]

    try:
        response = client.get(
            f"/api/locations/{location_id}/config"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["location"]["id"] == location_id
        assert len(data["zones"]) == 2

        for zone in data["zones"]:
            assert zone["location_id"] == location_id

    finally:
        delete_test_location(location_id)


def test_invalid_location_config_returns_400():
    response = client.post(
        "/api/locations/config",
        json={
            "location_name": "Invalid Test",
            "zones": [
                {
                    "name": "Bad Zone",
                    "moisture_threshold_low": 0.80,
                    "moisture_threshold_high": 0.40,
                    "schedule": {},
                }
            ],
        },
    )

    assert response.status_code == 400


def test_location_list_contains_created_location():
    created = create_test_location()

    location_id = created["location"]["id"]

    try:
        response = client.get(
            "/api/locations"
        )

        assert response.status_code == 200

        locations = response.json()

        assert any(
            location["id"] == location_id
            for location in locations
        )

    finally:
        delete_test_location(location_id)


def test_add_and_update_zone():
    created = create_test_location()

    location_id = created["location"]["id"]

    try:
        add_response = client.post(
            f"/api/locations/{location_id}/zones",
            json={
                "name": "Zone C",
                "moisture_threshold_low": 0.25,
                "moisture_threshold_high": 0.75,
                "schedule": {},
            },
        )

        assert add_response.status_code == 201

        zone = add_response.json()
        zone_id = zone["id"]

        update_response = client.patch(
            f"/api/locations/{location_id}/zones/{zone_id}",
            json={
                "name": "Zone C Updated",
                "moisture_threshold_low": 0.35,
                "moisture_threshold_high": 0.80,
            },
        )

        assert update_response.status_code == 200

        updated = update_response.json()

        assert updated["name"] == "Zone C Updated"
        assert updated["moisture_threshold_low"] == 0.35
        assert updated["moisture_threshold_high"] == 0.80

    finally:
        delete_test_location(location_id)


def test_invalid_zone_update_returns_400():
    created = create_test_location()

    location_id = created["location"]["id"]
    zone_id = created["zones"][0]["id"]

    try:
        response = client.patch(
            f"/api/locations/{location_id}/zones/{zone_id}",
            json={
                "moisture_threshold_low": 0.90,
                "moisture_threshold_high": 0.20,
            },
        )

        assert response.status_code == 400

    finally:
        delete_test_location(location_id)


def test_delete_zone_and_last_zone_rule():
    created = create_test_location()

    location_id = created["location"]["id"]

    zone_a = created["zones"][0]["id"]
    zone_b = created["zones"][1]["id"]

    try:
        response = client.delete(
            f"/api/locations/{location_id}/zones/{zone_a}"
        )

        assert response.status_code == 204

        last_zone_response = client.delete(
            f"/api/locations/{location_id}/zones/{zone_b}"
        )

        assert last_zone_response.status_code == 400

    finally:
        delete_test_location(location_id)


def test_assign_and_unassign_device():
    created = create_test_location()

    location_id = created["location"]["id"]
    zone_id = created["zones"][0]["id"]

    try:
        devices_response = client.get(
            "/api/devices"
        )

        assert devices_response.status_code == 200

        devices = devices_response.json()

        assert len(devices) > 0

        device_id = devices[0]["id"]

        assign_response = client.patch(
            f"/api/devices/{device_id}/zone",
            json={
                "zone_id": zone_id
            },
        )

        assert assign_response.status_code == 200

        assigned = assign_response.json()

        assert assigned["zone_id"] == zone_id
        assert assigned["location_id"] == location_id

        zone_devices_response = client.get(
            f"/api/locations/{location_id}/zones/{zone_id}/devices"
        )

        assert zone_devices_response.status_code == 200

        zone_devices = zone_devices_response.json()

        assert any(
            device["id"] == device_id
            for device in zone_devices
        )

        unassign_response = client.patch(
            f"/api/devices/{device_id}/zone",
            json={
                "zone_id": None
            },
        )

        assert unassign_response.status_code == 200

        unassigned = unassign_response.json()

        assert unassigned["zone_id"] is None
        assert unassigned["location_id"] is None

    finally:
        delete_test_location(location_id)