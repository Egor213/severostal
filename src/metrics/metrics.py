from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram, Gauge
from typing import Callable
from prometheus_fastapi_instrumentator.metrics import Info
import re

def jwt_metrics() -> Callable[[Info], None]:    
    JWT_ISSUED = Counter(
        'jwt_tokens_issued_total',
        'Total issued JWT tokens'
    )
    
    JWT_VALIDATED = Counter(
        'jwt_tokens_validated_total',
        'Total validated JWT tokens'
    )
    
    JWT_INVALID = Counter(
        'jwt_tokens_invalid_total',
        'Total invalid JWT tokens',
        ['reason']
    )
    
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
    USER_REGISTRATIONS = Counter(
        'user_registrations_total',
        'Total user registrations',
        ['status']
    )
    
    def instrumentation(info: Info) -> None:
        if (info.request.url.path == "/users/register" and 
            info.request.method == "POST"):
            
            status = "success" if 200 <= info.response.status_code < 300 else "error"
            USER_REGISTRATIONS.labels(status=status).inc()
    
    return instrumentation


def todo_operation_metrics() -> Callable[[Info], None]:
    TODO_CREATED = Counter(
        'todo_items_created_total',
        'Total created todo items',
        ['method', 'status']
    )
    
    TODO_UPDATED = Counter(
        'todo_items_updated_total',
        'Total updated todo items',
        ['method', 'status']
    )
    
    TODO_DELETED = Counter(
        'todo_items_deleted_total',
        'Total deleted todo items',
        ['method', 'status']
    )
    
    TODO_COMPLETED = Counter(
        'todo_items_completed_total',
        'Total completed todo items',
        ['method', 'status']
    )
    
    def instrumentation(info: Info) -> None:
        request = info.request
        path = request.url.path
        method = request.method
        
        
        if path.startswith("/todos"):
            status = "success" if 200 <= info.response.status_code < 300 else "error"

            if method == "POST" and re.match(r'^/todos/?$', path):
                TODO_CREATED.labels(method=method, status=status).inc()
            
            elif method == "PUT" and re.match(r'^/todos/\d+/?$', path):
                TODO_UPDATED.labels(method=method, status=status).inc()
            
            elif method == "PATCH" and re.match(r'^/todos/\d+/complete/?$', path):
                TODO_COMPLETED.labels(method=method, status=status).inc()
            
            elif method == "DELETE" and re.match(r'^/todos/\d+/?$', path):
                TODO_DELETED.labels(method=method, status=status).inc()

    return instrumentation


def error_metrics() -> Callable[[Info], None]:
    ERROR_COUNTER = Counter(
        'http_errors_total',
        'Total HTTP errors',
        ['status_code', 'path', 'method']
    )
    
    JWT_ERRORS = Counter(
        'jwt_errors_total',
        'JWT related errors',
        ['error_type']
    )
    
    def instrumentation(info: Info) -> None:
        response = info.response
        request = info.request
        
        if response.status_code >= 400:
            ERROR_COUNTER.labels(
                status_code=response.status_code,
                path=request.url.path,
                method=request.method
            ).inc()
        
        if response.status_code in [401, 403] and request.headers.get("Authorization"):
            JWT_ERRORS.labels(error_type=f"http_{response.status_code}").inc()
        
    return instrumentation


def configurate_metrics(app: FastAPI):
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/docs", "/openapi.json"],
        inprogress_name="inprogress",
        inprogress_labels=True,
    )
    
    instrumentator.add(metrics.requests(
        should_include=metrics.path_not_in(["/metrics", "/health"])
    ))
    
    instrumentator.add(metrics.request_size(
        should_include=metrics.path_not_in(["/metrics", "/health"])
    ))
    
    instrumentator.add(metrics.response_size(
        should_include=metrics.path_not_in(["/metrics", "/health"])
    ))
    
    instrumentator.add(metrics.latency(
        should_include=metrics.path_not_in(["/metrics", "/health"])
    ))
    
    instrumentator.add(jwt_metrics())
    instrumentator.add(user_registration_metrics())
    instrumentator.add(todo_operation_metrics())
    instrumentator.add(error_metrics())
    
    instrumentator.instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=True,
        should_gzip=True,
    )
