from fastapi.testclient import TestClient

from src.energy_agent.api import app


client = TestClient(app)


def test_openapi_contains_response_schemas():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schemas = response.json()["components"]["schemas"]

    assert "RecommendationRequest" in schemas
    assert "RecommendationResponse" in schemas
    assert "ElectricityPriceResponse" in schemas
    assert "RegionEnergyProfileResponse" in schemas


def test_recommendation_has_specific_response_model():
    specification = client.get("/openapi.json").json()

    response_schema = specification["paths"][
        "/recommendations"
    ]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    assert response_schema["$ref"].endswith(
        "/RecommendationResponse"
    )


def test_price_endpoint_has_specific_response_model():
    specification = client.get("/openapi.json").json()

    response_schema = specification["paths"][
        "/regions/{region}/price"
    ]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    assert response_schema["$ref"].endswith(
        "/ElectricityPriceResponse"
    )


def test_region_not_found_response_is_documented():
    specification = client.get("/openapi.json").json()

    responses = specification["paths"][
        "/regions/{region}"
    ]["get"]["responses"]

    assert "404" in responses
    assert responses["404"]["description"] == (
        "Region was not found."
    )


def test_database_unavailable_response_is_documented():
    specification = client.get("/openapi.json").json()

    responses = specification["paths"][
              "/recommendations"
    ]["post"]["responses"]

    assert "503" in responses