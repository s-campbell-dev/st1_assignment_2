
class Patient:
    def __init__(self, id, first_name, last_name, date_of_birth, contact, address, medical):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.contact = contact
        self.address = address
        self.medical = medical
        self.appointments = []

    def book_appointment(self, appointment):
        self.appointments.append(appointment)

    def cancel_appointment(self, appointment):
        self.appointments.remove(appointment)

    def view_practitioner(self, appointment):