Phase 3 — Abstract Factory questions
Pattern / focus: Abstract Factory.

Read first: Guide 03 · Requirements

How to answer
Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
When a question asks about this application, refer to device families, provision, and the unified devices API from the lab.
Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
Write each answer inside the matching Your Answer note. Replace the placeholder; leave the question text unchanged.
A. Pattern
1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (if format for each piece) instead of as a family?
Note

Your Answer

Abstract Factory is used to create a group of related objects that should work together. If every device is chosen separately with different if conditions, we could accidentally mix simulation and edge devices with incompatible settings.

2. Name the main participants (abstract factory, concrete factory, abstract products, concrete products, client). How does choosing a factory at the start commit the client to one family?
Note



The abstract factory defines how a device family is created. SimulationDeviceFactory and EdgeDeviceFactory are the concrete factories. The products are the related devices such as sensors and actuators, and the client is the service that asks the selected factory to create them. Once a factory is selected, all devices it creates belong to the same family.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?
Note

Your Answer

Abstract Factory is useful when several related products must be created as one consistent family. I would skip it if the application only creates one independent object at a time or if mixing products from different families is acceptable.

B. This phase of the application
4. In this lab, what is a device family, and what does create_device_set() (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?
Note

Your Answer

In this project, a device family is either simulation or edge. create_device_set() returns four related devices: two sensors and two actuators. The devices should stay in the same family because simulation and edge devices have different labels, protocols, and configuration values.

5. Phase 2 Factory Method creators still exist. How does Abstract Factory compose them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?
Note

Your Answer

The Abstract Factory still uses the Phase 2 sensor creators to create the moisture and light sensors. It then adds the family information and combines them with actuators. If I removed the sensor creators, I would duplicate sensor creation logic and lose the reusable Factory Method structure from Phase 2.

6. Why add a device_family column on the existing devices table (with a default/backfill such as "simulation") instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?
Note

Your Answer

device_family was added to the existing devices table because sensors and actuators share the same basic device structure. The default "simulation" also keeps the old Phase 2 sensor rows valid. Without the default or backfill, old rows could have no family and might fail the non-null migration or disappear from family-filtered results.

7. POST /api/devices/provision returns a kit (expected size: two sensors and two actuators). GET /api/devices can filter by family and role. Why must the UI be able to filter by family? Why do /api/sensors routes from Phase 2 still need to work?
Note

Your Answer

The UI needs family filtering so simulation and edge devices are not mixed together when viewing a kit. The Phase 2 /api/sensors routes should still work because Phase 3 extends the previous phase instead of replacing it, and the old sensor functionality must remain available.

C. Compare, contrast, and scenarios
8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which one product?” versus “which product line?” and mention that Abstract Factory often uses Factory Method–style methods inside.
Note

Your Answer

Factory Method answers “which one product should I create?”, while Abstract Factory answers “which product line or family should I create?”. In Phase 2, Factory Method creates individual moisture or light sensors. In Phase 3, Abstract Factory creates a complete simulation or edge kit, and it can use Factory Method creators internally for the individual sensors.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?
Note

Your Answer

If the DTO or API handler creates devices directly, it could mix simulation and edge configuration and break family consistency. The HTTP layer should only receive the request and call the service. The service should select the correct family factory and let it create the complete device set.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?
Note

Your Answer

A single factory for devices, locations, readings, and everything else would have too many responsibilities. Abstract Factory should create related products that belong to one family, not unrelated parts of the whole application. Separate features should keep their own appropriate services or patterns.