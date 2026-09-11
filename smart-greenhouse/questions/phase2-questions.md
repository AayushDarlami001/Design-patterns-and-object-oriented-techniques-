A.  Pattern

1. What is the intent of Factory Method?
Factory Method lets the program create different object types without spreading object creation everywhere. If many places use constructors or long if/else blocks, the code becomes harder to maintain when new types are added.

2. Main participants of Factory Method:

Product – the common object being created.
Concrete product – a specific version of that product.
Creator – defines how a product should be created.
Concrete creator – creates a specific product type.
Client – asks the creator for the object instead of creating it directly.

3. Adding a new product variant
With polymorphic creators, I can add a new creator class and register it. With one big if/elif, I have to keep modifying the same function. The creator approach is easier to extend and keeps the code cleaner.

B. This phase of the application

4. What is the product and who are the creators?
The product is the Sensor. The concrete creators are MoistureSensorCreator and LightSensorCreator. The API should use the creator or registry so sensor creation stays in one place instead of being mixed into the API code.

5. Why are type and device_type different?
type is a short value sent by the client, like "moisture". device_type is the value stored in the database, like moisture_sensor. The concrete creator decides the device_type and the default configuration.

6. Why use one devices table?
Using one devices table keeps different greenhouse devices in one common structure. Sensors are identified using role="sensor". This also prepares the project for later phases where other device roles can be added.

7. What happens with an unknown type?
The request should be rejected with an error, such as HTTP 400. The registry or service should decide this before anything is saved to the database.

C. Compare and scenarios

8. Factory Method vs simple factory
A simple factory uses one function with if/elif conditions. It is fine when there are only a few simple types. Factory Method is better when the application may grow because each type can have its own creator.

9. Factory Method vs Abstract Factory
Factory Method mainly answers: which specific object should I create?
Abstract Factory answers: which group of related objects should I create together?
For Phase 2, we only need to create individual sensor types, so Factory Method is enough.

10. Why not put database or FastAPI code inside creators?
Creators should only be responsible for creating domain objects. Database saving belongs in the repository, and HTTP request handling belongs in the API layer. Mixing them would make the creator harder to test and reuse.