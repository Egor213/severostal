import re
from typing import Callable

from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info


def jwt_metrics() -> Callable[[Info], None]:
    JWT_ISSUED = Counter("jwt_tokens_issued_total", "Total issued JWT tokens")

    JWT_VALIDATED = Counter("jwt_tokens_validated_total", "Total validated JWT tokens")

    JWT_INVALID = Counter("jwt_tokens_invalid_total", "Total invalid JWT tokens", ["reason"])

    def instrumentation(info: Info) -> None:
        request = info.request
        response = info.response

        path = request.url.path

        if path == "/login" and request.method == "POST":
            if 200 <= response.status_code < 300:
                JWT_ISSUED.inc()

        elif response.status_code == 401:
            JWT_INVALID.labels(reason="unauthorized").inc()

        elif request.headers.get("Authorization") and 200 <= response.status_code < 300:
            if not any(p in path for p in ["/login", "/register", "/docs", "/openapi.json"]):
                JWT_VALIDATED.inc()

    return instrumentation


def user_registration_metrics() -> Callable[[Info], None]:
    USER_REGISTRATIONS = Counter("user_registrations_total", "Total user registrations", ["status"])

    def instrumentation(info: Info) -> None:
        if info.request.url.path == "/users/register" and info.request.method == "POST":

            status = "success" if 200 <= info.response.status_code < 300 else "error"
            USER_REGISTRATIONS.labels(status=status).inc()

    return instrumentation


def tasks_operation_metrics() -> Callable[[Info], None]:
    TASKS_CREATED = Counter(
        "tasks_items_created_total", "Total created tasks items", ["method", "status"]
    )

    TASKS_UPDATED = Counter(
        "tasks_items_updated_total", "Total updated tasks items", ["method", "status"]
    )

    TASKS_DELETED = Counter(
        "tasks_items_deleted_total", "Total deleted tasks items", ["method", "status"]
    )

    TASKS_COMPLETED = Counter(
        "tasks_items_completed_total", "Total completed tasks items", ["method", "status"]
    )

    def instrumentation(info: Info) -> None:
        request = info.request
        path = request.url.path
        method = request.method

        start_path = "/api/v1/tasks/"
        if path.startswith(start_path):
            status = "success" if 200 <= info.response.status_code < 300 else "error"

            if method == "POST" and re.match(rf"^{start_path}?$", path):
                TASKS_CREATED.labels(method=method, status=status).inc()

            elif method == "PUT" and re.match(rf"^{start_path}\d+/?$", path):
                TASKS_UPDATED.labels(method=method, status=status).inc()

            elif method == "PATCH" and re.match(rf"^{start_path}\d+/complete/?$", path):
                TASKS_COMPLETED.labels(method=method, status=status).inc()

            elif method == "DELETE" and re.match(rf"^{start_path}\d+/?$", path):
                TASKS_DELETED.labels(method=method, status=status).inc()

    return instrumentation


def error_metrics() -> Callable[[Info], None]:
    ERROR_COUNTER = Counter(
        "http_errors_total", "Total HTTP errors", ["status_code", "path", "method"]
    )

    JWT_ERRORS = Counter("jwt_errors_total", "JWT related errors", ["error_type"])

    def instrumentation(info: Info) -> None:
        response = info.response
        request = info.request

        if response.status_code >= 400:
            ERROR_COUNTER.labels(
                status_code=response.status_code, path=request.url.path, method=request.method
            ).inc()

        if response.status_code in [401, 403] and request.headers.get("Authorization"):
            JWT_ERRORS.labels(error_type=f"http_{response.status_code}").inc()

    return instrumentation


def configurate_metrics(app: FastAPI):
    instrumentator = Instrumentator(
        excluded_handlers=["/metrics", "/ping", "/docs", "/openapi.json"],
    )

    instrumentator.add(metrics.requests())
    instrumentator.add(metrics.request_size())
    instrumentator.add(metrics.response_size())
    instrumentator.add(metrics.latency())

    instrumentator.add(jwt_metrics())
    instrumentator.add(user_registration_metrics())
    instrumentator.add(tasks_operation_metrics())
    instrumentator.add(error_metrics())

    instrumentator.instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=True,
    )
