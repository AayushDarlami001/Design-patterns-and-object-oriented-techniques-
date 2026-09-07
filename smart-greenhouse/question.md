Phase 1 — Skeleton Questions
A. Pattern

1. What is a design pattern?
A design pattern is a common way to solve a software design problem. It is not ready-made code that we copy directly.

2. Three GoF pattern families:

Creational – how objects are created. Factory Method belongs here.
Structural – how objects and classes are connected.
Behavioral – how objects work and communicate together. Strategy belongs here.

3. When should you skip a pattern?
If the problem is simple and the pattern does not really help, I would skip it. Using patterns too early can make simple code unnecessarily complicated.

B. This Phase of the Application

4. Why is Phase 1 “empty but running”?
The goal is to make sure the frontend, backend and database work together before adding real greenhouse features. Running software proves the setup works, while empty classes do not.

5. What are the four backend layers?

domain – business rules and concepts
application – use cases and application logic
infrastructure – database and technical setup
interfaces/api – API routes and HTTP communication

The domain should not contain FastAPI routes or database-specific code.

6. What does /health do?
It shows whether the API and database are working. In my project it returns "status": "ok" and "db": "ok". /scalar is used for API documentation, while /docs is disabled.

7. Why use Alembic already?
Alembic gives us a proper way to manage database changes from the beginning. Creating tables manually could cause different database structures later.

C. Compare and Scenarios

8. What is dependency direction?
The core business logic should stay independent. The domain should not depend on FastAPI, SQLAlchemy or HTTP models, because these are technical details.

9. What if the health badge does not work?
I would first check the backend, database, /health response, API URL and CORS. These are setup problems, not design pattern problems.

10. What is missing after Phase 1?
The real greenhouse features are still missing. Later phases will add sensors, devices, automation, database tables and design patterns without rebuilding the basic project structure.