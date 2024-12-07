from pydantic import BaseModel


class Person(BaseModel):
    name: str
    email: str | None = None


class SayHelloRequest(BaseModel):
    person: Person


class SayHelloResponse(BaseModel):
    greeting_message: str
    for_person: Person


def run(payload: SayHelloRequest, **kwargs):
    return SayHelloResponse(greeting_message=f"Hello {payload.person.name}", for_person=payload.person)
