from tortoise import Model, fields
from example.enums import Status, Status2


class MessageUser(Model):
    nickname = fields.CharField(max_length=32)


class Message(Model):
    info = fields.CharField(max_length=32, description="信息", verbose_name="信息")
    error_info = fields.IntEnumField(Status)
    error_info_str = fields.CharEnumField(Status2)
    # message_user = fields.ForeignKeyField("fast_tmp.MessageUser")
    # t1 = fields.JSONField()


class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ReverseRelation["Event"]

    def __str__(self):
        return self.name


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    tournament: fields.ForeignKeyRelation[Tournament] = fields.ForeignKeyField(
        "fast_tmp.Tournament",
        related_name="events",
        on_delete=fields.CASCADE,
    )
    participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField(
        "fast_tmp.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Address(Model):
    city = fields.CharField(max_length=64)
    street = fields.CharField(max_length=128)

    event: fields.OneToOneRelation[Event] = fields.OneToOneField(
        "fast_tmp.Event", on_delete=fields.CASCADE, related_name="address", pk=True
    )

    def __str__(self):
        return f"Address({self.city}, {self.street})"


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ManyToManyRelation[Event]

    def __str__(self):
        return self.name
