from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import CarBrand, CarModel, Car, CarDocument, CarImage
from datetime import date, timedelta


class CarBrandModelTests(TestCase):
    
    def setUp(self):
        self.brand = CarBrand.objects.create(
            name="Toyota",
            country="Japan",
            description="Leading automotive manufacturer"
        )
    
    def test_car_brand_creation(self):
        self.assertEqual(self.brand.name, "Toyota")
        self.assertEqual(self.brand.country, "Japan")
        self.assertEqual(str(self.brand), "Toyota")
    
    def test_car_brand_unique_name(self):
        with self.assertRaises(Exception):
            CarBrand.objects.create(name="Toyota")


class CarModelModelTests(TestCase):
    
    def setUp(self):
        self.brand = CarBrand.objects.create(name="Honda", country="Japan")
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Civic",
            year=2023,
            description="Compact sedan"
        )
    
    def test_car_model_creation(self):
        self.assertEqual(self.car_model.name, "Civic")
        self.assertEqual(self.car_model.year, 2023)
        self.assertEqual(str(self.car_model), "Honda Civic (2023)")
    
    def test_car_model_brand_relationship(self):
        self.assertEqual(self.car_model.brand, self.brand)
        self.assertIn(self.car_model, self.brand.models.all())


class CarModelTests(TestCase):
    
    def setUp(self):
        self.brand = CarBrand.objects.create(name="Ford", country="USA")
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Mustang",
            year=2024
        )
        self.car = Car.objects.create(
            model=self.car_model,
            license_plate="ABC-1234",
            vin="1HGBH41JXMN109186",
            color="Red",
            mileage=5000,
            fuel_type="GASOLINE",
            transmission="AUTOMATIC",
            seats=4,
            doors=2,
            trunk_capacity=350,
            daily_price=Decimal("250.00"),
            has_gps=True,
            has_air_conditioning=True
        )
    
    def test_car_creation(self):
        self.assertEqual(self.car.license_plate, "ABC-1234")
        self.assertEqual(self.car.status, "AVAILABLE")
        self.assertTrue(self.car.is_available)
    
    def test_car_status_methods(self):
        self.car.mark_as_rented()
        self.assertEqual(self.car.status, "RENTED")
        self.assertFalse(self.car.is_available)
        
        self.car.mark_as_available()
        self.assertEqual(self.car.status, "AVAILABLE")
        self.assertTrue(self.car.is_available)
        
        self.car.mark_for_maintenance()
        self.assertEqual(self.car.status, "MAINTENANCE")
        self.assertFalse(self.car.is_available)
        
        self.car.mark_as_damaged()
        self.assertEqual(self.car.status, "DAMAGED")
        self.assertFalse(self.car.is_available)
    
    def test_car_unique_license_plate(self):
        with self.assertRaises(Exception):
            Car.objects.create(
                model=self.car_model,
                license_plate="ABC-1234",
                vin="DIFFERENT123456789",
                color="Blue",
                mileage=0,
                fuel_type="GASOLINE",
                transmission="MANUAL",
                seats=5,
                doors=4,
                trunk_capacity=400,
                daily_price=Decimal("150.00")
            )


class CarDocumentModelTests(TestCase):
    
    def setUp(self):
        brand = CarBrand.objects.create(name="Chevrolet")
        car_model = CarModel.objects.create(brand=brand, name="Onix", year=2023)
        self.car = Car.objects.create(
            model=car_model,
            license_plate="XYZ-5678",
            vin="9BWZZZ377VT004251",
            color="White",
            mileage=10000,
            fuel_type="GASOLINE",
            transmission="MANUAL",
            seats=5,
            doors=4,
            trunk_capacity=300,
            daily_price=Decimal("100.00")
        )
        self.document = CarDocument.objects.create(
            car=self.car,
            document_type="INSURANCE",
            document_number="INS-123456",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )
    
    def test_document_creation(self):
        self.assertEqual(self.document.document_type, "INSURANCE")
        self.assertFalse(self.document.is_expired)
    
    def test_document_expiration(self):
        expired_doc = CarDocument.objects.create(
            car=self.car,
            document_type="INSPECTION",
            document_number="INSP-789",
            issue_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=35)
        )
        self.assertTrue(expired_doc.is_expired)
        self.assertTrue(expired_doc.days_to_expire < 0)


class CarImageModelTests(TestCase):
    
    def setUp(self):
        brand = CarBrand.objects.create(name="Volkswagen")
        car_model = CarModel.objects.create(brand=brand, name="Golf", year=2023)
        self.car = Car.objects.create(
            model=car_model,
            license_plate="DEF-9999",
            vin="WVWZZZ1KZBW000001",
            color="Black",
            mileage=2000,
            fuel_type="GASOLINE",
            transmission="AUTOMATIC",
            seats=5,
            doors=4,
            trunk_capacity=380,
            daily_price=Decimal("180.00")
        )
        self.image = CarImage.objects.create(
            car=self.car,
            image_url="https://example.com/car1.jpg",
            description="Front view",
            is_primary=True
        )
    
    def test_image_creation(self):
        self.assertEqual(self.image.car, self.car)
        self.assertTrue(self.image.is_primary)
        self.assertIn(self.image, self.car.images.all())


class CarAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user123'
        )
        
        self.brand = CarBrand.objects.create(name="Nissan", country="Japan")
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="Sentra",
            year=2023
        )
        self.car = Car.objects.create(
            model=self.car_model,
            license_plate="TEST-001",
            vin="JN1TANT31U0000001",
            color="Silver",
            mileage=1000,
            fuel_type="GASOLINE",
            transmission="AUTOMATIC",
            seats=5,
            doors=4,
            trunk_capacity=400,
            daily_price=Decimal("150.00")
        )
    
    def test_list_cars_unauthenticated(self):
        response = self.client.get('/api/cars/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_car_requires_admin(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'model': self.car_model.id,
            'license_plate': 'NEW-001',
            'vin': 'NEWVIN123456789',
            'color': 'Blue',
            'mileage': 0,
            'fuel_type': 'ELECTRIC',
            'transmission': 'AUTOMATIC',
            'seats': 5,
            'doors': 4,
            'trunk_capacity': 400,
            'daily_price': '200.00'
        }
        response = self.client.post('/api/cars/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_car_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'model': self.car_model.id,
            'license_plate': 'NEW-002',
            'vin': 'NEWVIN987654321',
            'color': 'Green',
            'mileage': 0,
            'fuel_type': 'HYBRID',
            'transmission': 'AUTOMATIC',
            'seats': 5,
            'doors': 4,
            'trunk_capacity': 450,
            'daily_price': '220.00'
        }
        response = self.client.post('/api/cars/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Car.objects.filter(license_plate='NEW-002').count(), 1)
