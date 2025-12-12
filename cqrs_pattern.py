from dataclasses import dataclass
from typing import List, Dict, Any
from decimal import Decimal
from abc import ABC, abstractmethod



class Command(ABC):
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        pass


@dataclass
class CreateRentalCommand(Command):

    user_id: int
    car_id: int
    start_date: str
    end_date: str
    pickup_location: str
    dropoff_location: str
    
    def execute(self) -> Dict[str, Any]:
        """Create rental."""
        from rentals.service.services import RentalService
        
        return RentalService.create_rental(
            user_id=self.user_id,
            car_id=self.car_id,
            start_date=self.start_date,
            end_date=self.end_date,
            pickup_location=self.pickup_location,
            dropoff_location=self.dropoff_location
        )


@dataclass
class ConfirmRentalCommand(Command):
    
    rental_id: int
    
    def execute(self) -> Dict[str, Any]:
        """Confirm rental."""
        from rentals.models import Rental
        
        rental = Rental.objects.get(id=self.rental_id)
        rental.status = 'CONFIRMED'
        rental.save()
        
        return {
            'success': True,
            'rental_id': rental.id,
            'status': rental.status
        }


@dataclass
class CancelRentalCommand(Command):
    
    rental_id: int
    reason: str
    
    def execute(self) -> Dict[str, Any]:
        """Cancel rental."""
        from rentals.service.services import RentalService
        
        return RentalService.cancel_rental(
            rental_id=self.rental_id,
            reason=self.reason
        )


@dataclass
class ProcessPaymentCommand(Command):
    
    rental_id: int
    amount: Decimal
    payment_method: str
    
    def execute(self) -> Dict[str, Any]:
        return {
            'success': True,
            'transaction_id': 'TXN123',
            'amount': str(self.amount)
        }



class Query(ABC):
    
    @abstractmethod
    def execute(self) -> Any:
        pass


@dataclass
class GetRentalQuery(Query):
    
    rental_id: int
    
    def execute(self):
        from rentals.models import Rental
        from rentals.serializers import RentalDetailSerializer
        
        rental = Rental.objects.select_related('user', 'car').get(id=self.rental_id)
        return RentalDetailSerializer(rental).data


@dataclass
class GetUserRentalsQuery(Query):
    
    user_id: int
    limit: int = 10
    
    def execute(self):
        from rentals.models import Rental
        from rentals.serializers import RentalListSerializer
        
        rentals = Rental.objects.filter(user_id=self.user_id).select_related('car')[:self.limit]
        return RentalListSerializer(rentals, many=True).data


@dataclass
class GetAvailableCarsQuery(Query):
    
    start_date: str
    end_date: str
    
    def execute(self):
        from cars.models import Car
        from rentals.models import Rental
        from cars.serializers import CarListSerializer
        
        conflicting_rentals = Rental.objects.filter(
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            status__in=['CONFIRMED', 'ACTIVE']
        ).values_list('car_id', flat=True)
        
        cars = Car.objects.filter(
            is_available=True
        ).exclude(id__in=conflicting_rentals)
        
        return CarListSerializer(cars, many=True).data


@dataclass
class GetRentalStatisticsQuery(Query):
    
    def execute(self):
        from rentals.models import Rental
        from django.db.models import Count, Sum, Avg
        
        stats = Rental.objects.aggregate(
            total_rentals=Count('id'),
            completed_rentals=Count('id', filter=models.Q(status='COMPLETED')),
            total_revenue=Sum('total_amount', filter=models.Q(status='COMPLETED')),
            average_rental_duration=Avg(
                models.F('end_date') - models.F('start_date')
            )
        )
        
        return stats



class CommandBus:
    """
    Central command dispatcher.
    Routes commands to handlers.
    """
    
    _handlers = {}
    
    @classmethod
    def register(cls, command_class: type, handler):
        """Register command handler."""
        cls._handlers[command_class.__name__] = handler
    
    @classmethod
    def execute(cls, command: Command) -> Dict[str, Any]:
        """Execute command."""
        handler = cls._handlers.get(command.__class__.__name__)
        
        if not handler:
            raise ValueError(f"No handler for {command.__class__.__name__}")
        
        return handler(command).execute()



class QueryBus:
    """
    Central query dispatcher.
    Routes queries to handlers.
    """
    
    _handlers = {}
    
    @classmethod
    def register(cls, query_class: type, handler):
        """Register query handler."""
        cls._handlers[query_class.__name__] = handler
    
    @classmethod
    def execute(cls, query: Query) -> Any:
        """Execute query."""
        handler = cls._handlers.get(query.__class__.__name__)
        
        if not handler:
            raise ValueError(f"No handler for {query.__class__.__name__}")
        
        return query.execute()



CommandBus.register(CreateRentalCommand, CreateRentalCommand)
CommandBus.register(ConfirmRentalCommand, ConfirmRentalCommand)
CommandBus.register(CancelRentalCommand, CancelRentalCommand)
CommandBus.register(ProcessPaymentCommand, ProcessPaymentCommand)

QueryBus.register(GetRentalQuery, GetRentalQuery)
QueryBus.register(GetUserRentalsQuery, GetUserRentalsQuery)
QueryBus.register(GetAvailableCarsQuery, GetAvailableCarsQuery)
QueryBus.register(GetRentalStatisticsQuery, GetRentalStatisticsQuery)



class RentalController:
    
    def create_rental(self, request):
        command = CreateRentalCommand(
            user_id=request.user.id,
            car_id=request.data['car_id'],
            start_date=request.data['start_date'],
            end_date=request.data['end_date'],
            pickup_location=request.data['pickup_location'],
            dropoff_location=request.data['dropoff_location']
        )
        
        result = CommandBus.execute(command)
        return {'status': 'success', 'data': result}
    
    def get_rentals(self, request, user_id):
        query = GetUserRentalsQuery(
            user_id=user_id,
            limit=request.query_params.get('limit', 10)
        )
        
        result = QueryBus.execute(query)
        return {'status': 'success', 'data': result}
    
    def get_available_cars(self, request):
        query = GetAvailableCarsQuery(
            start_date=request.query_params['start_date'],
            end_date=request.query_params['end_date']
        )
        
        result = QueryBus.execute(query)
        return {'status': 'success', 'data': result}
    
    def get_statistics(self, request):
        """Get statistics - Read Operation."""
        query = GetRentalStatisticsQuery()
        result = QueryBus.execute(query)
        return {'status': 'success', 'data': result}
