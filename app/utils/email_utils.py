def extract_domain(email: str):

    return email.split("@")[-1].lower()