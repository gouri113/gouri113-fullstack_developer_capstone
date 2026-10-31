from .models import CarMake, CarModel


def initiate():
    car_make_data = [
        {"name": "NISSAN", "description": "Great cars. Japanese technology"},
        {"name": "Mercedes", "description": "Set the standard in luxury"},
        {"name": "Audi", "description": "Vorsprung durch Technik"},
        {"name": "Kia", "description": "Movement that inspires"},
        {"name": "Toyota", "description": "Let's Go Places"},
    ]

    car_make_instances = []
    for data in car_make_data:
        car_make, _ = CarMake.objects.get_or_create(
            name=data['name'],
            defaults={'description': data['description']}
        )
        car_make_instances.append(car_make)

    car_model_data = [
        {"name": "Pathfinder", "type": "SUV", "year": 2023, "car_make": car_make_instances[0]},
        {"name": "Qashqai", "type": "SUV", "year": 2023, "car_make": car_make_instances[0]},
        {"name": "Altima", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[0]},
        {"name": "C-Class", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[1]},
        {"name": "E-Class", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[1]},
        {"name": "GLC", "type": "SUV", "year": 2023, "car_make": car_make_instances[1]},
        {"name": "A4", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[2]},
        {"name": "A5", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[2]},
        {"name": "A6", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[2]},
        {"name": "Sorrento", "type": "SUV", "year": 2023, "car_make": car_make_instances[3]},
        {"name": "Carnival", "type": "SUV", "year": 2023, "car_make": car_make_instances[3]},
        {"name": "Cerato", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[3]},
        {"name": "Corolla", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[4]},
        {"name": "Camry", "type": "SEDAN", "year": 2023, "car_make": car_make_instances[4]},
        {"name": "Kluger", "type": "SUV", "year": 2023, "car_make": car_make_instances[4]},
    ]

    for data in car_model_data:
        CarModel.objects.get_or_create(
            name=data['name'],
            car_make=data['car_make'],
            defaults={
                'type': data['type'],
                'year': data['year']
            }
        )
    print("Database populated successfully.")
