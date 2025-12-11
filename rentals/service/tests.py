"""
Tests for the RentalService.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from cars.models import CarBrand, CarModel, Car
from rentals.models import Rental, RentalPayment
from rentals.service import RentalService


class RentalServiceTests(TestCase):
    """Testes para o RentalService"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar carro para testes
        brand = CarBrand.objects.create(name="Toyota", country="Japan")
        car_model = CarModel.objects.create(brand=brand, name="Corolla", year=2023)
        self.car = Car.objects.create(
            model=car_model,
            license_plate="TEST-001",
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
    
    def test_create_rental_success(self):
        """Testar criação bem-sucedida de rental"""
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=3)
        
        result = RentalService.create_rental(
            user_id=self.user.id,
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date,
            pickup_location="Aeroporto",
            dropoff_location="Centro"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('rental_id', result)
        self.assertIn('total_amount', result)
        self.assertIn('breakdown', result)
    
    def test_create_rental_invalid_dates(self):
        """Testar criação com datas inválidas"""
        start_date = timezone.now() + timedelta(days=3)
        end_date = start_date - timedelta(days=1)
        
        result = RentalService.create_rental(
            user_id=self.user.id,
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date,
            pickup_location="Centro",
            dropoff_location="Centro"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_create_rental_past_date(self):
        """Testar criação com data no passado"""
        start_date = timezone.now() - timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        
        result = RentalService.create_rental(
            user_id=self.user.id,
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date,
            pickup_location="Centro",
            dropoff_location="Centro"
        )
        
        self.assertFalse(result['success'])
    
    def test_check_availability_available(self):
        """Testar verificação de disponibilidade - carro disponível"""
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        
        available = RentalService.check_availability(
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertTrue(available)
    
    def test_check_availability_not_available(self):
        """Testar verificação de disponibilidade - carro indisponível"""
        self.car.mark_as_rented()
        
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=2)
        
        available = RentalService.check_availability(
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertFalse(available)
    
    def test_check_availability_conflicting_rental(self):
        """Testar verificação com rental conflitante"""
        # Criar rental existente
        start_date1 = timezone.now() + timedelta(days=1)
        end_date1 = start_date1 + timedelta(days=3)
        
        rental1 = Rental(
            user=self.user,
            car=self.car,
            start_date=start_date1,
            end_date=end_date1,
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="CONFIRMED"
        )
        rental1.calculate_total_amount()
        rental1.save()
        
        # Tentar criar novo rental com conflito
        start_date2 = start_date1 + timedelta(days=1)
        end_date2 = start_date2 + timedelta(days=2)
        
        available = RentalService.check_availability(
            car_id=self.car.id,
            start_date=start_date2,
            end_date=end_date2
        )
        
        self.assertFalse(available)
    
    def test_calculate_total_price(self):
        """Testar cálculo de preço total"""
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=3)
        
        price_info = RentalService.calculate_total_price(
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date,
            extras=[]
        )
        
        self.assertIn('duration_days', price_info)
        self.assertIn('subtotal', price_info)
        self.assertIn('tax', price_info)
        self.assertIn('total', price_info)
        self.assertEqual(price_info['duration_days'], 3)
    
    def test_calculate_total_price_with_insurance(self):
        """Testar cálculo de preço com seguro"""
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=3)
        
        price_info = RentalService.calculate_total_price(
            car_id=self.car.id,
            start_date=start_date,
            end_date=end_date,
            extras=['insurance']
        )
        
        self.assertIn('insurance', price_info)
        self.assertGreater(Decimal(price_info['insurance']), Decimal('0'))
    
    def test_cancel_rental_with_refund(self):
        """Testar cancelamento com reembolso"""
        start_date = timezone.now() + timedelta(days=10)
        end_date = start_date + timedelta(days=3)
        
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=start_date,
            end_date=end_date,
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="PENDING"
        )
        rental.calculate_total_amount()
        rental.save()
        
        result = RentalService.cancel_rental(
            rental_id=rental.id,
            reason="Mudança de planos"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('refund_amount', result)
        self.assertGreater(Decimal(result['refund_amount']), Decimal('0'))
    
    def test_cancel_rental_no_refund(self):
        """Testar cancelamento sem reembolso (dia do início)"""
        start_date = timezone.now() + timedelta(hours=2)
        end_date = start_date + timedelta(days=3)
        
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=start_date,
            end_date=end_date,
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="PENDING"
        )
        rental.calculate_total_amount()
        rental.save()
        
        result = RentalService.cancel_rental(rental_id=rental.id)
        
        self.assertTrue(result['success'])
        self.assertEqual(Decimal(result['refund_amount']), Decimal('0'))
    
    def test_update_rental_status_valid_transition(self):
        """Testar atualização válida de status"""
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=3),
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="PENDING"
        )
        rental.calculate_total_amount()
        rental.save()
        
        result = RentalService.update_rental_status(
            rental_id=rental.id,
            new_status="CONFIRMED"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['new_status'], "CONFIRMED")
    
    def test_update_rental_status_invalid_transition(self):
        """Testar atualização inválida de status"""
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=3),
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="PENDING"
        )
        rental.calculate_total_amount()
        rental.save()
        
        result = RentalService.update_rental_status(
            rental_id=rental.id,
            new_status="COMPLETED"
        )
        
        self.assertFalse(result['success'])
    
    def test_get_customer_rentals(self):
        """Testar obtenção de rentals do cliente"""
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=3),
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00")
        )
        rental.calculate_total_amount()
        rental.save()
        
        rentals = RentalService.get_customer_rentals(user_id=self.user.id)
        
        self.assertEqual(len(rentals), 1)
        self.assertEqual(rentals[0]['id'], rental.id)
    
    def test_get_car_rental_history(self):
        """Testar obtenção do histórico do carro"""
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() - timedelta(days=5),
            end_date=timezone.now() - timedelta(days=2),
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="COMPLETED"
        )
        rental.calculate_total_amount()
        rental.save()
        
        history = RentalService.get_car_rental_history(car_id=self.car.id)
        
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]['id'], rental.id)
    
    def test_calculate_late_fees(self):
        """Testar cálculo de multa por atraso"""
        start_date = timezone.now() - timedelta(days=5)
        end_date = timezone.now() - timedelta(days=2)
        
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=start_date,
            end_date=end_date,
            pickup_location="Centro",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            status="ACTIVE"
        )
        rental.calculate_total_amount()
        rental.save()
        
        fees = RentalService.calculate_late_fees(rental_id=rental.id)
        
        self.assertTrue(fees['has_late_fees'])
        self.assertGreater(fees['late_days'], 0)
    
    def test_get_rental_summary(self):
        """Testar obtenção do resumo do rental"""
        rental = Rental(
            user=self.user,
            car=self.car,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=3),
            pickup_location="Aeroporto",
            dropoff_location="Centro",
            daily_rate=Decimal("150.00"),
            mileage_start=5000,
            mileage_end=5150
        )
        rental.calculate_total_amount()
        rental.save()
        
        summary = RentalService.get_rental_summary(rental_id=rental.id)
        
        self.assertEqual(summary['rental_id'], rental.id)
        self.assertIn('customer', summary)
        self.assertIn('car', summary)
        self.assertIn('pricing', summary)
        self.assertIn('mileage', summary)
