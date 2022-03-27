from json import load


class Patient:

    # vitals
    vitals_detected = False
    vitals_registered = False
    heart_rate = None

    # vision
    in_view = False
    blink_registered = False
    requesting = False


class Caretaker:
    def __init__(self) -> None:
        self.email, self.phone, self.em_service = self._generate_details()

    def _generate_details(self):

        # no locks required as this is done only after the model is
        # initiated by the website

        # note that path is relative to the server not the
        # python model anymore
        details_path = r"data/contact_details.json"
        with open(details_path) as file:
            data = load(file)

        email = data["email"]
        phone = data["phone"]

        # this is not sure...
        em_service = "example@gmail.com"

        return (email, phone, em_service)
