class ValidationError(Exception):
    def __init__(self, message, tag):
        self.message = message
        self.tag = tag
        super().__init__(message)


class NegativePlacesError(ValidationError):
    message = "Sorry, you should type a positive number."
    tag = "Negative number"

    def __init__(self):
        super().__init__(self.message, self.tag)


class Over12PlacesError(ValidationError):
    message = "Sorry, you are not allow to purchase more than 12 places for this competition."
    tag = "Over 12 places"

    def __init__(self):
        super().__init__(self.message, self.tag)


class NotEnoughPlacesError(ValidationError):
    message = "Sorry, there are not enough places available for this competition."
    tag = "Not enough places"

    def __init__(self):
        super().__init__(self.message, self.tag)


class NotEnoughPointsError(ValidationError):
    message = "Sorry, you do not have enough points to purchase."
    tag = "Not enough points"

    def __init__(self):
        super().__init__(self.message, self.tag)


class OutdatedCompetitionError(ValidationError):
    message = "Sorry, this competition is outdated. Booking not possible."
    tag = "Outdated"

    def __init__(self):
        super().__init__(self.message, self.tag)


class CompetitionNullPlacesError(ValidationError):
    message = "Sorry, this competition is sold out. Booking not possible."
    tag = "Sold out"

    def __init__(self):
        super().__init__(self.message, self.tag)


class EmptyFieldError(ValidationError):
    message = "Sorry, please fill all fields."
    tag = "Empty field(s)"

    def __init__(self):
        super().__init__(self.message, self.tag)


class PasswordsNotMatchError(ValidationError):
    message = "Sorry, passwords do not match."
    tag = "Passwords not match"

    def __init__(self):
        super().__init__(self.message, self.tag)


class PasswordNotDifferentError(ValidationError):
    message = "Sorry, you have to type a new different password."
    tag = "Identical password"

    def __init__(self):
        super().__init__(self.message, self.tag)


class MailAddressInvalidFormatError(ValidationError):
    message = "Sorry, the e-mail address you entered has invalid format."
    tag = "Invalid email format"

    def __init__(self):
        super().__init__(self.message, self.tag)
