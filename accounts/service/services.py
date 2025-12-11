from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from rentals.models import Rental
from decimal import Decimal


class AccountService:

    @staticmethod
    def get_user_profile(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        rentals = Rental.objects.filter(user=user)
        total_rentals = rentals.count()
        active_rentals = rentals.filter(status='ACTIVE').count()
        completed_rentals = rentals.filter(status='COMPLETED').count()
        cancelled_rentals = rentals.filter(status='CANCELLED').count()
        
        total_spent = sum(
            rental.total_amount for rental in rentals.filter(status__in=['COMPLETED', 'ACTIVE'])
            if rental.total_amount
        )
        
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'is_active': user.is_active,
            },
            'statistics': {
                'total_rentals': total_rentals,
                'active_rentals': active_rentals,
                'completed_rentals': completed_rentals,
                'cancelled_rentals': cancelled_rentals,
                'total_spent': float(total_spent) if total_spent else 0.0,
                'average_rental_value': float(total_spent / completed_rentals) if completed_rentals > 0 else 0.0,
            }
        }

    @staticmethod
    def update_user_profile(user_id, data):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        allowed_fields = ['first_name', 'last_name', 'email']
        
        for field, value in data.items():
            if field in allowed_fields:
                if field == 'email':
                    if User.objects.filter(email=value).exclude(id=user_id).exists():
                        raise ValidationError(f"Email {value} is already in use")
                setattr(user, field, value)
        
        user.full_clean()  
        user.save()
        
        return user

    @staticmethod
    def deactivate_account(user_id, reason=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        # Check for active rentals
        active_rentals = Rental.objects.filter(
            user=user,
            status__in=['PENDING', 'CONFIRMED', 'ACTIVE']
        )
        
        if active_rentals.exists():
            raise ValidationError(
                f"Cannot deactivate account. User has {active_rentals.count()} active rental(s). "
                "Please complete or cancel all rentals first."
            )
        
        user.is_active = False
        user.save()
        
        return {
            'success': True,
            'message': f"Account for {user.username} has been deactivated",
            'reason': reason
        }

    @staticmethod
    def reactivate_account(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        if user.is_active:
            raise ValidationError(f"Account for {user.username} is already active")
        
        user.is_active = True
        user.save()
        
        return user

    @staticmethod
    def get_user_rental_history(user_id, status=None, limit=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        rentals = Rental.objects.filter(user=user).select_related('car', 'car__model', 'car__model__brand')
        
        if status:
            rentals = rentals.filter(status=status)
        
        rentals = rentals.order_by('-created_at')
        
        if limit:
            rentals = rentals[:limit]
        
        return rentals

    @staticmethod
    def calculate_user_loyalty_score(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        rentals = Rental.objects.filter(user=user)
        completed_rentals = rentals.filter(status='COMPLETED')
        
        points = 0
        
        points += completed_rentals.count() * 10
        
        total_spent = sum(
            rental.total_amount for rental in completed_rentals
            if rental.total_amount
        )
        points += int(total_spent / 100)
        
        cancelled_count = rentals.filter(status='CANCELLED').count()
        if cancelled_count == 0 and completed_rentals.count() > 0:
            points += 50 
        
        
        if points >= 500:
            tier = 'PLATINUM'
            discount = 0.20  
        elif points >= 300:
            tier = 'GOLD'
            discount = 0.15  
            tier = 'SILVER'
            discount = 0.10  
        elif points >= 50:
            tier = 'BRONZE'
            discount = 0.05  
        else:
            tier = 'STANDARD'
            discount = 0.00
        
        return {
            'user_id': user_id,
            'username': user.username,
            'points': points,
            'tier': tier,
            'discount_percentage': discount * 100,
            'next_tier': AccountService._get_next_tier(points),
            'total_rentals': rentals.count(),
            'completed_rentals': completed_rentals.count(),
            'total_spent': float(total_spent) if total_spent else 0.0
        }

    @staticmethod
    def _get_next_tier(points):
        if points >= 500:
            return {'tier': 'PLATINUM', 'points_needed': 0, 'message': 'Maximum tier reached!'}
        elif points >= 300:
            return {'tier': 'PLATINUM', 'points_needed': 500 - points, 'message': f'Need {500 - points} points for PLATINUM'}
        elif points >= 150:
            return {'tier': 'GOLD', 'points_needed': 300 - points, 'message': f'Need {300 - points} points for GOLD'}
        elif points >= 50:
            return {'tier': 'SILVER', 'points_needed': 150 - points, 'message': f'Need {150 - points} points for SILVER'}
        else:
            return {'tier': 'BRONZE', 'points_needed': 50 - points, 'message': f'Need {50 - points} points for BRONZE'}

    @staticmethod
    def check_user_eligibility_for_rental(user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        reasons = []
        is_eligible = True
        
        if not user.is_active:
            is_eligible = False
            reasons.append("Account is deactivated")
        
        overdue_rentals = Rental.objects.filter(
            user=user,
            status='ACTIVE'
        ).filter(end_date__lt=timezone.now().date())
        
        if overdue_rentals.exists():
            is_eligible = False
            reasons.append(f"Has {overdue_rentals.count()} overdue rental(s)")
        
        # Check for unpaid rentals
        unpaid_rentals = Rental.objects.filter(
            user=user,
            status__in=['CONFIRMED', 'ACTIVE', 'COMPLETED']
        ).exclude(
            payments__status='PAID'
        ).distinct()
        
        if unpaid_rentals.exists():
            is_eligible = False
            reasons.append(f"Has {unpaid_rentals.count()} unpaid rental(s)")
        
        active_rentals = Rental.objects.filter(
            user=user,
            status__in=['PENDING', 'CONFIRMED', 'ACTIVE']
        )
        
        if active_rentals.count() >= 3:
            is_eligible = False
            reasons.append(f"Maximum active rentals limit reached ({active_rentals.count()}/3)")
        
        return {
            'user_id': user_id,
            'is_eligible': is_eligible,
            'reasons': reasons if not is_eligible else ['User is eligible for rentals'],
            'active_rentals': active_rentals.count(),
            'overdue_rentals': overdue_rentals.count()
        }

    @staticmethod
    @transaction.atomic
    def delete_account_permanently(user_id, confirmation_password):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} not found")
        
        if not user.check_password(confirmation_password):
            raise ValidationError("Incorrect password")
        
        active_rentals = Rental.objects.filter(
            user=user,
            status__in=['PENDING', 'CONFIRMED', 'ACTIVE']
        )
        
        if active_rentals.exists():
            raise ValidationError(
                f"Cannot delete account. User has {active_rentals.count()} active rental(s). "
                "Please complete or cancel all rentals first."
            )
        
        username = user.username
        
        user.delete()
        
        return {
            'success': True,
            'message': f"Account for {username} has been permanently deleted",
            'deleted_at': timezone.now()
        }
