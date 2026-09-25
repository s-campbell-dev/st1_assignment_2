from datetime import date

class Patient:
    #Hints
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    contact: str
    address: str
    medical: str
    def __init__(
            self,
                 id:int,
                 first_name:str,
                 last_name: str,
                 date_of_birth: str,
                 contact: str,
                 address:str,
                 medical:str
    ):

        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.contact = contact
        self.address = address
        self.medical = medical
        self.appointments = []

        #Validation
        if not first_name.strip() or not last_name.strip():
            raise ValueError("Patient must have a first and last name")
        if not isinstance(date_of_birth, date):
            raise ValueError("Patient must have a date of birth")
        if date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future")
        if not contact.strip():
            raise ValueError("Patient must have a contact")
        if not address.strip():
            raise ValueError("Patient must have a address")

class Practitioner:
    id: int
    first_name: str
    last_name: str
    specialty: str

    def __init__(self, id:int, first_name:str, last_name:str, specialty:str):
        if not first_name.strip() or not last_name.strip():
            raise ValueError("Practitioner must have a first and last name")
        if not specialty.strip():
            raise ValueError("Practitioner must have a specialty")

# from __future__ import annotations

import datetime as dt
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    import Patient, Practitioner


class AppointmentError(Exception):
    """Raised when an appointment breaks a booking or status rule."""


class AppointmentStatus(Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    def can_transition_to(self, target: AppointmentStatus) -> bool:
        return target in _ALLOWED_TRANSITIONS[self]


_ALLOWED_TRANSITIONS: dict[AppointmentStatus, frozenset[AppointmentStatus]] = {
    AppointmentStatus.SCHEDULED: frozenset(
        {AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED}
    ),
    AppointmentStatus.COMPLETED: frozenset(),
    AppointmentStatus.CANCELLED: frozenset(),
}


class Appointment:
    SLOT_MINUTES: ClassVar[int] = 20
    _all: ClassVar[list[Appointment]] = []

    def __init__(
        self,
        patient: Patient,
        practitioner: Practitioner,
        date: dt.date,
        time: dt.time,
        double_booked: bool = False,
    ) -> None:
        self.patient = patient
        self.practitioner = practitioner
        self.date = date
        self.time = time
        self.double_booked = double_booked
        self._status = AppointmentStatus.SCHEDULED
        self._check_conflicts()
        Appointment._all.append(self)

    def __repr__(self) -> str:
        return (
            f"Appointment({self.day} {self.start:%Y-%m-%d %H:%M}-{self.end:%H:%M}, "
            f"{self._status.value})"
        )

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    @property
    def day(self) -> str:
        return self.date.strftime("%A")

    @property
    def duration(self) -> dt.timedelta:
        slots = 2 if self.double_booked else 1
        return dt.timedelta(minutes=self.SLOT_MINUTES * slots)

    @property
    def start(self) -> dt.datetime:
        return dt.datetime.combine(self.date, self.time)

    @property
    def end(self) -> dt.datetime:
        return self.start + self.duration

    @property
    def _blocks_time(self) -> bool:
        return self._status is not AppointmentStatus.CANCELLED

    def complete(self) -> None:
        self._transition_to(AppointmentStatus.COMPLETED)

    def cancel(self) -> None:
        self._transition_to(AppointmentStatus.CANCELLED)

    def _transition_to(self, target: AppointmentStatus) -> None:
        if not self._status.can_transition_to(target):
            raise AppointmentError(
                f"Cannot change appointment from {self._status.value} to {target.value}"
            )
        self._status = target

    def _overlaps(self, other: Appointment) -> bool:
        return self.start < other.end and other.start < self.end

    def _check_conflicts(self) -> None:
        clashes = (a for a in Appointment._all if a._blocks_time and self._overlaps(a))
        for other in clashes:
            same_practitioner = other.practitioner.id == self.practitioner.id
            same_patient = other.patient.id == self.patient.id
            if same_practitioner and same_patient and other.start == self.start:
                raise AppointmentError("Duplicate appointment")
            if same_practitioner:
                raise AppointmentError("Practitioner is already booked at that time")
            if same_patient:
                raise AppointmentError("Patient already has an appointment at that time")

