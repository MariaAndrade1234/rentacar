import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth.models import User
from cars.models import Car, CarBrand, CarModel
from rentals.models import Rental, RentalPayment



class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rentals']


class CarBrandType(DjangoObjectType):
    class Meta:
        model = CarBrand
        fields = ['id', 'name', 'country', 'description', 'models']


class CarModelType(DjangoObjectType):
    class Meta:
        model = CarModel
        fields = ['id', 'name', 'brand', 'year', 'description', 'cars']


class CarType(DjangoObjectType):
    availability_status = graphene.String()
    
    class Meta:
        model = Car
        fields = [
            'id', 'model', 'license_plate', 'vin', 'color', 'mileage',
            'fuel_type', 'transmission', 'seats', 'doors', 'trunk_capacity',
            'daily_price', 'status', 'is_available', 'has_gps',
            'has_air_conditioning', 'has_power_steering', 'has_abs', 'has_airbag'
        ]
    
    def resolve_availability_status(self, info):
        return self.status


class RentalType(DjangoObjectType):
    user_name = graphene.String()
    car_details = graphene.Field(CarType)
    
    class Meta:
        model = Rental
        fields = [
            'id', 'user', 'car', 'start_date', 'end_date', 'actual_return_date',
            'pickup_location', 'dropoff_location', 'status', 'daily_rate',
            'total_days', 'subtotal', 'discount', 'tax', 'total_amount',
            'mileage_start', 'mileage_end', 'notes', 'cancellation_reason',
            'created_at', 'updated_at'
        ]
    
    def resolve_user_name(self, info):
        return self.user.username
    
    def resolve_car_details(self, info):
        return self.car


class RentalPaymentType(DjangoObjectType):
    class Meta:
        model = RentalPayment
        fields = [
            'id', 'rental', 'amount', 'payment_method', 'status',
            'transaction_id', 'payment_date', 'notes'
        ]



class Query(graphene.ObjectType):
    """GraphQL Queries for RentACar."""
    
    me = graphene.Field(UserType)
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    all_users = graphene.List(UserType, limit=graphene.Int())
    
    all_cars = graphene.List(CarType)
    available_cars = graphene.List(CarType)
    car = graphene.Field(CarType, id=graphene.Int(required=True))
    cars_by_brand = graphene.List(CarType, brand_id=graphene.Int(required=True))
    search_cars = graphene.List(CarType, query=graphene.String(required=True))
    
    all_rentals = graphene.List(RentalType)
    my_rentals = graphene.List(RentalType)
    rental = graphene.Field(RentalType, id=graphene.Int(required=True))
    active_rentals = graphene.List(RentalType)
    
    all_brands = graphene.List(CarBrandType)
    all_models = graphene.List(CarModelType)
    
    total_rentals = graphene.Int()
    total_revenue = graphene.Decimal()
    average_rental_duration = graphene.Float()
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None
    
    def resolve_user(self, info, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
    
    def resolve_all_users(self, info, limit=10):
        if info.context.user.is_staff:
            return User.objects.all()[:limit]
        return []
    
    def resolve_all_cars(self, info):
        return Car.objects.select_related('model__brand').all()
    
    def resolve_available_cars(self, info):
        return Car.objects.filter(is_available=True).select_related('model__brand')
    
    def resolve_car(self, info, id):
        try:
            return Car.objects.get(id=id)
        except Car.DoesNotExist:
            return None
    
    def resolve_cars_by_brand(self, info, brand_id):
        return Car.objects.filter(model__brand_id=brand_id).select_related('model__brand')
    
    def resolve_search_cars(self, info, query):
        return Car.objects.filter(
            models.Q(license_plate__icontains=query) |
            models.Q(vin__icontains=query) |
            models.Q(model__name__icontains=query)
        ).select_related('model__brand')
    
    def resolve_all_rentals(self, info):
        if info.context.user.is_staff:
            return Rental.objects.select_related('user', 'car').all()
        return []
    
    def resolve_my_rentals(self, info):
        user = info.context.user
        if user.is_authenticated:
            return Rental.objects.filter(user=user).select_related('car')
        return []
    
    def resolve_rental(self, info, id):
        try:
            rental = Rental.objects.get(id=id)
            if info.context.user == rental.user or info.context.user.is_staff:
                return rental
        except Rental.DoesNotExist:
            pass
        return None
    
    def resolve_active_rentals(self, info):
        return Rental.objects.filter(status__in=['CONFIRMED', 'ACTIVE']).select_related('user', 'car')
    
    def resolve_all_brands(self, info):
        return CarBrand.objects.all()
    
    def resolve_all_models(self, info):
        return CarModel.objects.select_related('brand').all()
    
    def resolve_total_rentals(self, info):
        return Rental.objects.count()
    
    def resolve_total_revenue(self, info):
        from django.db.models import Sum
        result = Rental.objects.filter(status='COMPLETED').aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    def resolve_average_rental_duration(self, info):
        from django.db.models import Avg, F
        from django.db.models.functions import Extract
        result = Rental.objects.aggregate(
            avg_duration=Avg(Extract('end_date', output_field=models.IntegerField()) - 
                           Extract('start_date', output_field=models.IntegerField()))
        )
        return result['avg_duration'] or 0


class CreateRentalMutation(graphene.Mutation):
    
    class Arguments:
        car_id = graphene.Int(required=True)
        start_date = graphene.DateTime(required=True)
        end_date = graphene.DateTime(required=True)
        pickup_location = graphene.String(required=True)
        dropoff_location = graphene.String(required=True)
    
    rental = graphene.Field(RentalType)
    success = graphene.Boolean()
    error = graphene.String()
    
    def mutate(self, info, car_id, start_date, end_date, pickup_location, dropoff_location):
        from rentals.service.services import RentalService
        
        user = info.context.user
        if not user.is_authenticated:
            return CreateRentalMutation(success=False, error='User not authenticated')
        
        result = RentalService.create_rental(
            user_id=user.id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location
        )
        
        if result['success']:
            rental = Rental.objects.get(id=result['rental_id'])
            return CreateRentalMutation(rental=rental, success=True)
        else:
            return CreateRentalMutation(success=False, error=result['error'])


class CancelRentalMutation(graphene.Mutation):
    
    class Arguments:
        rental_id = graphene.Int(required=True)
        reason = graphene.String(required=True)
    
    rental = graphene.Field(RentalType)
    success = graphene.Boolean()
    error = graphene.String()
    refund_amount = graphene.Decimal()
    
    def mutate(self, info, rental_id, reason):
        from rentals.service.services import RentalService
        
        user = info.context.user
        if not user.is_authenticated:
            return CancelRentalMutation(success=False, error='User not authenticated')
        
        try:
            rental = Rental.objects.get(id=rental_id)
            if rental.user != user and not user.is_staff:
                return CancelRentalMutation(success=False, error='Permission denied')
            
            result = RentalService.cancel_rental(rental_id=rental_id, reason=reason)
            
            if result['success']:
                rental.refresh_from_db()
                return CancelRentalMutation(
                    rental=rental,
                    success=True,
                    refund_amount=result['refund_amount']
                )
            else:
                return CancelRentalMutation(success=False, error=result['error'])
        
        except Rental.DoesNotExist:
            return CancelRentalMutation(success=False, error='Rental not found')


class Mutation(graphene.ObjectType):
    
    create_rental = CreateRentalMutation.Field()
    cancel_rental = CancelRentalMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
