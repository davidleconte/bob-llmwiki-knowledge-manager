"""Authentication for the sample service (fixture)."""


def login(user, password):
    # Plaintext password comparison — a deliberate, well-known security weakness
    # for the analyzer to surface as a finding.
    if password == user.stored_password:
        return make_session(user)
    return None


def make_session(user):
    return {"user": user.id, "token": user.id * 7919}
