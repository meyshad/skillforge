---
name: api-docs
description: Produces accurate OpenAPI 3.1 specifications and developer-friendly API reference docs by reading the actual route handlers, validators and models, including examples, error formats, auth and pagination. Use when the user asks to document an API, generate or fix an OpenAPI or Swagger spec, write API reference docs, or describe endpoints for client developers.
---

# API Documentation

Documentation that disagrees with the code is worse than none. Derive everything from the source.

## 1. Inventory the API from code
- Find the routing layer: Express/Fastify/Nest routers, FastAPI/Flask/Django URLconfs, Gin/Echo/chi, Spring `@RequestMapping`, Rails `routes.rb`, Laravel `routes/api.php`.
- If the framework already generates OpenAPI (FastAPI `/openapi.json`, NestJS `@nestjs/swagger`, springdoc, drf-spectacular), **improve the annotations** rather than hand-writing a parallel spec.
- For each endpoint, collect: method, path, path/query/header params, request body schema, validation rules, auth requirement, every status code the handler can return, and the response schema.
- Read the validators (zod, Joi, pydantic, class-validator, JSON Schema) for exact types, required fields, enums, formats, min/max.

## 2. Write the spec (OpenAPI 3.1)
```yaml
openapi: 3.1.0
info:
  title: Orders API
  version: 1.4.0
  description: Create and track customer orders.
servers:
  - url: https://api.example.com/v1
security:
  - bearerAuth: []
paths:
  /orders/{orderId}:
    get:
      operationId: getOrder
      summary: Get an order by ID
      tags: [Orders]
      parameters:
        - name: orderId
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        "200":
          description: The order.
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Order" }
              example: { id: "6f1c...", status: "paid", totalCents: 4200, currency: "USD" }
        "404": { $ref: "#/components/responses/NotFound" }
components:
  securitySchemes:
    bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
  responses:
    NotFound:
      description: Resource not found.
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
  schemas:
    Problem:   # RFC 9457 problem details
      type: object
      properties:
        type: { type: string, format: uri }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
```

Rules:
- Stable, unique `operationId`s in camelCase (SDK generators use them as method names).
- Reuse via `components` (`schemas`, `responses`, `parameters`); no copy-pasted schemas.
- Realistic `example`s for every request and success response; never real customer data or real keys.
- Document **all** error responses, including 401/403/422/429, with one consistent error shape.
- Document pagination (cursor vs. offset, limits), rate limits (headers), idempotency keys, and versioning policy.

## 3. Validate
Use what's available: `npx @redocly/cli lint openapi.yaml` or `npx @stoplight/spectral-cli lint openapi.yaml`. Fix every error. Spot-check by calling real endpoints locally where possible and comparing responses to the schema.

## 4. Human-readable reference
For each resource, a guide page with: overview, authentication, a copy-paste `curl` example, the same in one or two popular languages, the response, and common errors with their fixes. Render the spec with Redoc, Scalar or Swagger UI for browsing.

## 5. Report gaps
List mismatches found between code and existing docs, undocumented endpoints, and endpoints whose behavior looked inconsistent (e.g. some return 400 and others 422 for validation errors) as follow-up suggestions.
