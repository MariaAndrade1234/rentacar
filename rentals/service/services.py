from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError

from rentals.models import Rental, RentalPayment, RentalReview, RentalDocument
from cars.models import Car


class RentalService:

    DAILY_RATE_MULTIPLIER = Decimal('1.0')
    LATE_FEE_PER_DAY = Decimal('50.00')  
    INSURANCE_DAILY_RATE = Decimal('10.00') 
    MINIMUM_RENTAL_DAYS = 1
    MAXIMUM_RENTAL_DAYS = 365

    @staticmethod
    def create_rental(
        user_id: int,
        car_id: int,
        start_date: datetime,
        end_date: datetime,
        pickup_location: str,
        dropoff_location: str,
        discount: Decimal = Decimal('0.00'),
        add_insurance: bool = False
    ) -> Dict[str, Any]:
        try:
            if start_date >= end_date:
                raise ValidationError("Data de término deve ser posterior à de início.")
            
            if start_date < timezone.now():
                raise ValidationError("Data de início não pode ser no passado.")
            
            duration = (end_date - start_date).days
            if duration < RentalService.MINIMUM_RENTAL_DAYS:
                raise ValidationError(f"Duração mínima: {RentalService.MINIMUM_RENTAL_DAYS} dia(s)")
            
            if duration > RentalService.MAXIMUM_RENTAL_DAYS:
                raise ValidationError(f"Duração máxima: {RentalService.MAXIMUM_RENTAL_DAYS} dias")
            
            if not RentalService.check_availability(car_id, start_date, end_date):
                raise ValidationError("Carro não disponível para o período selecionado.")
            
            car = Car.objects.get(id=car_id)
            
            price_info = RentalService.calculate_total_price(
                car_id=car_id,
                start_date=start_date,
                end_date=end_date,
                extras=['insurance'] if add_insurance else []
            )
            
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            
            rental = Rental(
                user=user,
                car=car,
                start_date=start_date,
                end_date=end_date,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                daily_rate=car.daily_price,
                discount=discount,
                    tax=Decimal(price_info['tax']),
                status='PENDING'
            )
            
            rental.calculate_total_amount()
            rental.save()
            
            return {
                'success': True,
                'rental_id': rental.id,
                'total_amount': str(rental.total_amount),
                'breakdown': price_info
            }
        
        except Car.DoesNotExist:
            return {'success': False, 'error': 'Carro não encontrado'}
        except ValidationError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f'Erro ao criar rental: {str(e)}'}

    @staticmethod
    def check_availability(car_id: int, start_date: datetime, end_date: datetime) -> bool:
        try:
            car = Car.objects.get(id=car_id)
            
            if not car.is_available:
                return False
            
            conflicting_rentals = Rental.objects.filter(
                car=car,
                status__in=['CONFIRMED', 'ACTIVE']
            ).filter(
                Q(start_date__lt=end_date) & Q(end_date__gt=start_date)
            ).exists()
            
            return not conflicting_rentals
        
        except Car.DoesNotExist:
            return False

    @staticmethod
    def calculate_total_price(
        car_id: int,
        start_date: datetime,
        end_date: datetime,
        extras: List[str] = None
    ) -> Dict[str, Any]:
        try:
            car = Car.objects.get(id=car_id)
            
            duration_days = (end_date - start_date).days or 1
            daily_rate = car.daily_price
            
            subtotal = daily_rate * Decimal(str(duration_days))
            
            insurance_cost = Decimal('0.00')
            if extras and 'insurance' in extras:
                insurance_cost = RentalService.INSURANCE_DAILY_RATE * Decimal(str(duration_days))
            
            tax = (subtotal + insurance_cost) * Decimal('0.10')
            
            total = subtotal + insurance_cost + tax
            
            return {
                'duration_days': duration_days,
                'daily_rate': str(daily_rate),
                'subtotal': str(subtotal),
                'insurance': str(insurance_cost),
                'tax': str(tax),
                'total': str(total)
            }
        
        except Car.DoesNotExist:
            return {'error': 'Carro não encontrado'}

    @staticmethod
    def cancel_rental(rental_id: int, reason: str = '') -> Dict[str, Any]:
        try:
            rental = Rental.objects.get(id=rental_id)
            
            if rental.status in ['COMPLETED', 'CANCELLED']:
                return {
                    'success': False,
                    'error': f'Não é possível cancelar rental com status {rental.status}'
                }
            
            refund_amount = RentalService._calculate_refund(rental)
            
            rental.status = 'CANCELLED'
            rental.cancellation_reason = reason
            if rental.car.status == 'RENTED':
                rental.car.mark_as_available()
            rental.save()
            
            return {
                'success': True,
                'rental_id': rental_id,
                'original_amount': str(rental.total_amount),
                'refund_amount': str(refund_amount),
                'cancellation_reason': reason
            }
        
        except Rental.DoesNotExist:
            return {'success': False, 'error': 'Rental não encontrado'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _calculate_refund(rental: Rental) -> Decimal:
        days_until_start = (rental.start_date - timezone.now()).days
        
        if days_until_start >= 7:
            return rental.total_amount
        elif days_until_start >= 3:
            return rental.total_amount * Decimal('0.5')
        elif days_until_start >= 1:
            return rental.total_amount * Decimal('0.25')
        else:
            return Decimal('0.00')

    @staticmethod
    def update_rental_status(rental_id: int, new_status: str) -> Dict[str, Any]:
        """
        Update rental status with validations.
        """
        valid_statuses = ['PENDING', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED']
        
        if new_status not in valid_statuses:
            return {'success': False, 'error': f'Status inválido: {new_status}'}
        
        try:
            rental = Rental.objects.get(id=rental_id)
            old_status = rental.status
            
            status_transitions = {
                'PENDING': ['CONFIRMED', 'CANCELLED'],
                'CONFIRMED': ['ACTIVE', 'CANCELLED'],
                'ACTIVE': ['COMPLETED', 'CANCELLED'],
                'COMPLETED': [],
                'CANCELLED': []
            }
            
            if new_status not in status_transitions.get(old_status, []):
                return {
                    'success': False,
                    'error': f'Transição inválida: {old_status} -> {new_status}'
                }
            
            rental.status = new_status
            
            if new_status == 'ACTIVE':
                rental.car.mark_as_rented()
            elif new_status == 'COMPLETED':
                rental.car.mark_as_available()
                rental.actual_return_date = timezone.now()
            
            rental.save()
            
            return {
                'success': True,
                'rental_id': rental_id,
                'old_status': old_status,
                'new_status': new_status
            }
        
        except Rental.DoesNotExist:
            return {'success': False, 'error': 'Rental não encontrado'}

    @staticmethod
    def get_customer_rentals(user_id: int) -> List[Dict[str, Any]]:
        try:
            rentals = Rental.objects.filter(user_id=user_id).select_related(
                'car__model__brand', 'user'
            ).prefetch_related('payments', 'documents', 'review')
            
            result = []
            for rental in rentals:
                result.append({
                    'id': rental.id,
                    'car': {
                        'brand': str(rental.car.model.brand.name),
                        'model': str(rental.car.model.name),
                        'license_plate': rental.car.license_plate,
                        'year': rental.car.model.year
                    },
                    'start_date': rental.start_date.isoformat(),
                    'end_date': rental.end_date.isoformat(),
                    'status': rental.status,
                    'total_amount': str(rental.total_amount),
                    'pickup_location': rental.pickup_location,
                    'dropoff_location': rental.dropoff_location
                })
            
            return result
        
        except Exception as e:
            return []

    @staticmethod
    def get_car_rental_history(car_id: int) -> List[Dict[str, Any]]:
        try:
            rentals = Rental.objects.filter(car_id=car_id).select_related(
                'user', 'car'
            ).order_by('-start_date')
            
            result = []
            for rental in rentals:
                result.append({
                    'id': rental.id,
                    'customer': rental.user.username,
                    'email': rental.user.email,
                    'start_date': rental.start_date.isoformat(),
                    'end_date': rental.end_date.isoformat(),
                    'actual_return': rental.actual_return_date.isoformat() if rental.actual_return_date else None,
                    'status': rental.status,
                    'total_amount': str(rental.total_amount),
                    'mileage_start': rental.mileage_start,
                    'mileage_end': rental.mileage_end
                })
            
            return result
        
        except Exception as e:
            return []

    @staticmethod
    def calculate_late_fees(rental_id: int) -> Dict[str, Any]:
        """
        Calculate late fees for a rental.
        """
        try:
            rental = Rental.objects.get(id=rental_id)
            
            if rental.status != 'ACTIVE':
                return {
                    'rental_id': rental_id,
                    'has_late_fees': False,
                    'message': f'Rental com status {rental.status} não pode ter multa'
                }
            
            now = timezone.now()
            
            if now <= rental.end_date:
                return {
                    'rental_id': rental_id,
                    'has_late_fees': False,
                    'late_days': 0,
                    'late_fees': '0.00'
                }
            
            late_days = (now - rental.end_date).days
            late_fees = RentalService.LATE_FEE_PER_DAY * Decimal(str(late_days))
            
            return {
                'rental_id': rental_id,
                'has_late_fees': True,
                'late_days': late_days,
                'daily_fee': str(RentalService.LATE_FEE_PER_DAY),
                'late_fees': str(late_fees),
                'due_date': rental.end_date.isoformat()
            }
        
        except Rental.DoesNotExist:
            return {'error': 'Rental não encontrado'}

    @staticmethod
    def get_rental_summary(rental_id: int) -> Dict[str, Any]:
        try:
            rental = Rental.objects.get(id=rental_id)
            
            duration = rental.get_duration_days() or 0
            actual_duration = rental.get_actual_duration_days()
            
            payments = RentalPayment.objects.filter(rental=rental)
            total_paid = sum(p.amount for p in payments if p.status == 'COMPLETED') or Decimal('0.00')
            
            review = RentalReview.objects.filter(rental=rental).first()
            
            return {
                'rental_id': rental.id,
                'customer': {
                    'username': rental.user.username,
                    'email': rental.user.email,
                    'phone': getattr(rental.user, 'phone', 'N/A')
                },
                'car': {
                    'brand': str(rental.car.model.brand.name),
                    'model': str(rental.car.model.name),
                    'license_plate': rental.car.license_plate,
                    'year': rental.car.model.year,
                    'color': rental.car.color
                },
                'dates': {
                    'start_date': rental.start_date.isoformat(),
                    'end_date': rental.end_date.isoformat(),
                    'actual_return': rental.actual_return_date.isoformat() if rental.actual_return_date else None,
                    'planned_duration_days': duration,
                    'actual_duration_days': actual_duration
                },
                'locations': {
                    'pickup': rental.pickup_location,
                    'dropoff': rental.dropoff_location
                },
                'pricing': {
                    'daily_rate': str(rental.daily_rate),
                    'subtotal': str(rental.subtotal),
                    'discount': str(rental.discount),
                    'tax': str(rental.tax),
                    'total_amount': str(rental.total_amount),
                    'total_paid': str(total_paid),
                    'balance': str(rental.total_amount - total_paid)
                },
                'mileage': {
                    'start': rental.mileage_start,
                    'end': rental.mileage_end,
                    'total': (rental.mileage_end - rental.mileage_start) if rental.mileage_end and rental.mileage_start else None
                },
                'status': rental.status,
                'review': {
                    'rating': review.rating if review else None,
                    'comment': review.comment if review else None
                } if review else None,
                'notes': rental.notes
            }
        
        except Rental.DoesNotExist:
            return {'error': 'Rental não encontrado'}
