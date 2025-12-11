from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Rental, RentalPayment, RentalReview, RentalDocument
from cars.models import CarBrand, CarModel, Car


class RentalModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        brand = CarBrand.objects.create(name="Toyota", country="Japan")
        car_model = CarModel.objects.create(brand=brand, name="Corolla", year=2023)
        self.car = Car.objects.create(
            model=car_model,
            license_plate="ABC-1234",
            vin="12345678901234567",
            color="White",
            mileage=5000,
            fuel_type="GASOLINE",
            transmission="AUTOMATIC",
            seats=5,
            doors=4,
            trunk_capacity=400,
            daily_price=Decimal("150.00")
        )
        
        self.rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=5),
            pickup_location="Aeroporto",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            discount=Decimal("0.00"),
            tax=Decimal("30.00")
        )
        self.rental.calculate_total_amount()
        self.rental.save()
    
    def test_rental_creation(self):
        self.assertEqual(self.rental.user, self.user)
        self.assertEqual(self.rental.car, self.car)
        self.assertEqual(self.rental.status, "PENDING")
    
    def test_calculate_total_amount(self):
        total = self.rental.calculate_total_amount()
        expected_total = (Decimal("150.00") * 4) + Decimal("30.00")  
        self.assertEqual(total, expected_total)
        self.assertEqual(self.rental.total_days, 4)
    
    def test_is_overdue(self):
        overdue_rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now() - timedelta(days=1),
            pickup_location="Centro",
            dropoff_location="Aeroporto",
            daily_rate=Decimal("150.00"),
            status="ACTIVE"
        )
        overdue_rental.calculate_total_amount()
        overdue_rental.save()
        
        self.assertTrue(overdue_rental.is_overdue())
        self.assertFalse(self.rental.is_overdue())
    
    def test_get_duration_days(self):
        duration = self.rental.get_duration_days()
        self.assertEqual(duration, 4)
    
    def test_rental_string_representation(self):
        expected = f"Rental #{self.rental.id} - {self.user.username} - {self.car.license_plate}"
        self.assertEqual(str(self.rental), expected)


class RentalPaymentModelTests(TestCase):
    
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        brand = CarBrand.objects.create(name="Honda")
        car_model = CarModel.objects.create(brand=brand, name="Civic", year=2023)
        car = Car.objects.create(
            model=car_model,
            license_plate="XYZ-5678",
            vin="98765432109876543",
            color="Black",
            mileage=3000,
            fuel_type="GASOLINE",
            transmission="MANUAL",
            seats=5,
            doors=4,
            trunk_capacity=350,
            daily_price=Decimal("120.00")
        )
        
        self.rental = Rental(
            user=user,
            car=car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=3),
            pickup_location="Hotel",
            dropoff_location="Aeroporto",
            daily_rate=Decimal("120.00")
        )
        self.rental.calculate_total_amount()
        self.rental.save()
        
        self.payment = RentalPayment.objects.create(
            rental=self.rental,
            amount=self.rental.total_amount,
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            transaction_id="TXN123456"
        )
    
    def test_payment_creation(self):
        self.assertEqual(self.payment.rental, self.rental)
        self.assertEqual(self.payment.status, "COMPLETED")
        self.assertEqual(self.payment.payment_method, "CREDIT_CARD")
    
    def test_payment_amount(self):
        self.assertEqual(self.payment.amount, self.rental.total_amount)


class RentalReviewModelTests(TestCase):
    
    def setUp(self):
        user = User.objects.create_user(username='reviewer', password='pass123')
        brand = CarBrand.objects.create(name="Ford")
        car_model = CarModel.objects.create(brand=brand, name="Focus", year=2023)
        car = Car.objects.create(
            model=car_model,
            license_plate="REV-001",
            vin="11111111111111111",
            color="Blue",
            mileage=2000,
            fuel_type="GASOLINE",
            transmission="AUTOMATIC",
            seats=5,
            doors=4,
            trunk_capacity=380,
            daily_price=Decimal("130.00")
        )
        
        rental = Rental(
            user=user,
            car=car,
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now() - timedelta(days=2),
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("130.00"),
            status="COMPLETED"
        )
        rental.calculate_total_amount()
        rental.save()
        
        self.review = RentalReview.objects.create(
            rental=rental,
            rating=5,
            comment="Excelente experiência!"
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "Excelente experiência!")


class RentalDocumentModelTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='docuser', password='pass123')
        brand = CarBrand.objects.create(name="Chevrolet")
        car_model = CarModel.objects.create(brand=brand, name="Onix", year=2023)
        car = Car.objects.create(
            model=car_model,
            license_plate="DOC-001",
            vin="22222222222222222",
            color="Silver",
            mileage=1000,
            fuel_type="GASOLINE",
            transmission="MANUAL",
            seats=5,
            doors=4,
            trunk_capacity=300,
            daily_price=Decimal("100.00")
        )
        
        rental = Rental(
            user=user,
            car=car,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=2),
            pickup_location="Loja",
            dropoff_location="Loja",
            daily_rate=Decimal("100.00")
        )
        rental.calculate_total_amount()
        rental.save()
        
        self.document = RentalDocument.objects.create(
            rental=rental,
            document_type="CONTRACT",
            file_url="https://example.com/contract.pdf",
            description="Contrato de locação"
        )
    
    def test_document_creation(self):
        self.assertEqual(self.document.document_type, "CONTRACT")
        self.assertIn("contract.pdf", self.document.file_url)


class RentalAPITests(APITestCase):    

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
        
        brand = CarBrand.objects.create(name="Nissan", country="Japan")
        car_model = CarModel.objects.create(brand=brand, name="Sentra", year=2023)
        self.car = Car.objects.create(
            model=car_model,
            license_plate="API-001",
            vin="33333333333333333",
            color="Red",
            mileage=5000,
            fuel_type="GASOLINE",
            transmission="AUTOMATIC",
            seats=5,
            doors=4,
            trunk_capacity=400,
            daily_price=Decimal("150.00")
        )
        
        self.rental = Rental(
            user=self.regular_user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=3),
            pickup_location="Aeroporto",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00")
        )
        self.rental.calculate_total_amount()
        self.rental.save()
    
    def test_list_rentals_requires_authentication(self):
        response = self.client.get('/api/rentals/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_list_user_rentals(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/rentals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 1)
        else:
            self.assertEqual(len(response.data['results']), 1)
    
    def test_admin_can_see_all_rentals(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        other_rental = Rental(
            user=other_user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=5),
            end_date=timezone.now() + timedelta(days=7),
            pickup_location="Centro",
            dropoff_location="Aeroporto",
            daily_rate=Decimal("150.00"),
            status="PENDING"
        )
        other_rental.calculate_total_amount()
        other_rental.save()
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/rentals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, list):
            self.assertGreaterEqual(len(response.data), 2)
        else:
            self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_create_rental(self):
        self.client.force_authenticate(user=self.regular_user)
        
        brand = CarBrand.objects.create(name="Volkswagen")
        car_model = CarModel.objects.create(brand=brand, name="Gol", year=2023)
        new_car = Car.objects.create(
            model=car_model,
            license_plate="NEW-001",
            vin="44444444444444444",
            color="White",
            mileage=0,
            fuel_type="GASOLINE",
            transmission="MANUAL",
            seats=5,
            doors=4,
            trunk_capacity=285,
            daily_price=Decimal("90.00")
        )
        
        data = {
            'user': self.regular_user.id,
            'car': new_car.id,
            'start_date': (timezone.now() + timedelta(days=10)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=12)).isoformat(),
            'pickup_location': 'Loja Centro',
            'dropoff_location': 'Loja Centro',
            'daily_rate': '90.00',
            'discount': '0.00',
            'tax': '0.00'
        }
        
        response = self.client.post('/api/rentals/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_cannot_rent_unavailable_car(self):
        self.client.force_authenticate(user=self.regular_user)
        
        self.car.mark_as_rented()
        
        data = {
            'user': self.regular_user.id,
            'car': self.car.id,
            'start_date': (timezone.now() + timedelta(days=20)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=22)).isoformat(),
            'pickup_location': 'Centro',
            'dropoff_location': 'Aeroporto',
            'daily_rate': '150.00'
        }
        
        response = self.client.post('/api/rentals/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
