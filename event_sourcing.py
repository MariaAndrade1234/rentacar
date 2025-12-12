from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
from decimal import Decimal
from django.db import models
import json


@dataclass
class RentalEvent:
    
    aggregate_id: int  
    event_id: str
    timestamp: datetime
    user_id: int
    event_type: str
    data: Dict[str, Any]
    version: int


class RentalCreatedEvent(RentalEvent):
    event_type = 'rental.created'


class RentalConfirmedEvent(RentalEvent):
    event_type = 'rental.confirmed'


class RentalStartedEvent(RentalEvent):
    event_type = 'rental.started'


class RentalCompletedEvent(RentalEvent):
    event_type = 'rental.completed'


class RentalCancelledEvent(RentalEvent):
    event_type = 'rental.cancelled'


class PaymentReceivedEvent(RentalEvent):
    event_type = 'payment.received'


class RentalPriceAdjustedEvent(RentalEvent):
    event_type = 'rental.price_adjusted'



class EventStore(models.Model):
 
    aggregate_id = models.IntegerField()  
    aggregate_type = models.CharField(max_length=50)  
    event_type = models.CharField(max_length=100)  
    event_data = models.JSONField()  
    timestamp = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()  
    user_id = models.IntegerField(null=True)
    
    class Meta:
        ordering = ['timestamp', 'version']
        indexes = [
            models.Index(fields=['aggregate_id', 'version']),
            models.Index(fields=['event_type', 'timestamp']),
        ]
        unique_together = ('aggregate_id', 'version')
    
    def __str__(self):
        return f"{self.aggregate_type}#{self.aggregate_id}: {self.event_type} v{self.version}"


class EventPublisher:
    
    _subscribers = {}
    
    @classmethod
    def subscribe(cls, event_type: str, callback):
        """Subscribe to events."""
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)
    
    @classmethod
    def publish(cls, event: RentalEvent):
        if event.event_type in cls._subscribers:
            for callback in cls._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")



class RentalAggregate:

    
    def __init__(self, rental_id: int):
        self.id = rental_id
        self.status = 'PENDING'
        self.user_id = None
        self.car_id = None
        self.start_date = None
        self.end_date = None
        self.total_amount = Decimal('0.00')
        self.discount = Decimal('0.00')
        self.tax = Decimal('0.00')
        self.version = 0
        self.uncommitted_events = []
    
    def create_rental(self, user_id: int, car_id: int, start_date, end_date,
                     pickup_location: str, dropoff_location: str,
                     total_amount: Decimal):
        
        event = RentalCreatedEvent(
            aggregate_id=self.id,
            event_id=f"rental-{self.id}-created",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            event_type='rental.created',
            data={
                'user_id': user_id,
                'car_id': car_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'pickup_location': pickup_location,
                'dropoff_location': dropoff_location,
                'total_amount': str(total_amount),
            },
            version=1
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    def confirm_rental(self):
        if self.status != 'PENDING':
            raise Exception(f"Cannot confirm rental in {self.status} status")
        
        event = RentalConfirmedEvent(
            aggregate_id=self.id,
            event_id=f"rental-{self.id}-confirmed",
            timestamp=datetime.utcnow(),
            user_id=self.user_id,
            event_type='rental.confirmed',
            data={},
            version=self.version + 1
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    def start_rental(self, mileage_start: int):
        if self.status not in ['CONFIRMED', 'PENDING']:
            raise Exception(f"Cannot start rental in {self.status} status")
        
        event = RentalStartedEvent(
            aggregate_id=self.id,
            event_id=f"rental-{self.id}-started",
            timestamp=datetime.utcnow(),
            user_id=self.user_id,
            event_type='rental.started',
            data={'mileage_start': mileage_start},
            version=self.version + 1
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    def complete_rental(self, mileage_end: int):
        if self.status != 'ACTIVE':
            raise Exception(f"Cannot complete rental in {self.status} status")
        
        event = RentalCompletedEvent(
            aggregate_id=self.id,
            event_id=f"rental-{self.id}-completed",
            timestamp=datetime.utcnow(),
            user_id=self.user_id,
            event_type='rental.completed',
            data={'mileage_end': mileage_end},
            version=self.version + 1
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    def cancel_rental(self, reason: str, refund_amount: Decimal):
        if self.status == 'COMPLETED' or self.status == 'CANCELLED':
            raise Exception(f"Cannot cancel rental in {self.status} status")
        
        event = RentalCancelledEvent(
            aggregate_id=self.id,
            event_id=f"rental-{self.id}-cancelled",
            timestamp=datetime.utcnow(),
            user_id=self.user_id,
            event_type='rental.cancelled',
            data={
                'reason': reason,
                'refund_amount': str(refund_amount)
            },
            version=self.version + 1
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    def apply_event(self, event: RentalEvent):
        
        if event.event_type == 'rental.created':
            self.user_id = event.data['user_id']
            self.car_id = event.data['car_id']
            self.start_date = event.data['start_date']
            self.end_date = event.data['end_date']
            self.total_amount = Decimal(event.data['total_amount'])
            self.status = 'PENDING'
        
        elif event.event_type == 'rental.confirmed':
            self.status = 'CONFIRMED'
        
        elif event.event_type == 'rental.started':
            self.status = 'ACTIVE'
        
        elif event.event_type == 'rental.completed':
            self.status = 'COMPLETED'
        
        elif event.event_type == 'rental.cancelled':
            self.status = 'CANCELLED'
        
        self.version = event.version
        
        EventPublisher.publish(event)
    
    def load_from_history(self, events: List[RentalEvent]):
        for event in events:
            self.apply_event(event)
    
    def save_events(self):
        for event in self.uncommitted_events:
            EventStore.objects.create(
                aggregate_id=event.aggregate_id,
                aggregate_type='Rental',
                event_type=event.event_type,
                event_data=asdict(event),
                version=event.version,
                user_id=event.user_id
            )
        self.uncommitted_events = []


class RentalProjection:

    
    def __init__(self):
        pass
    
    @staticmethod
    def handle_rental_created(event: RentalCreatedEvent):
        print(f"Projection: Rental {event.aggregate_id} created")
    
    @staticmethod
    def handle_rental_confirmed(event: RentalConfirmedEvent):
        print(f"Projection: Rental {event.aggregate_id} confirmed")
    
    @staticmethod
    def handle_rental_completed(event: RentalCompletedEvent):
        print(f"Projection: Rental {event.aggregate_id} completed")


class RentalEventRepository:
    
    @staticmethod
    def save(aggregate: RentalAggregate):
        aggregate.save_events()
    
    @staticmethod
    def get_by_id(rental_id: int) -> RentalAggregate:
        aggregate = RentalAggregate(rental_id)
        
        events = EventStore.objects.filter(
            aggregate_id=rental_id,
            aggregate_type='Rental'
        ).order_by('version')
        
        reconstructed_events = []
        for event_record in events:
            event_data = event_record.event_data
            reconstructed_events.append(event_data)
        
        for event_data in reconstructed_events:
            event = RentalEvent(**event_data)
            aggregate.apply_event(event)
        
        return aggregate
